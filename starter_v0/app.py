from __future__ import annotations

import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


TRANSCRIPTS_DIR = ROOT / "transcripts"
RUNS_DIR = ROOT / "runs"
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
VERSION_LOG_PATH = ARTIFACTS_DIR / "version_log.csv"

st.set_page_config(
    page_title="Research Agent Lab",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --messenger-blue: #0084ff;
        --messenger-blue-dark: #006fd6;
        --messenger-ink: #050505;
        --messenger-muted: #65676b;
        --messenger-surface: #ffffff;
        --messenger-soft: #f0f2f5;
        --messenger-border: #e4e6eb;
    }
    .stApp {
        background: var(--messenger-surface);
        color: var(--messenger-ink);
    }
    .block-container { max-width: 1120px; padding-top: 1.25rem; }
    [data-testid="stSidebar"] {
        background: var(--messenger-surface);
        border-right: 1px solid var(--messenger-border);
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p {
        color: var(--messenger-ink) !important;
    }
    [data-testid="stSidebar"] .stCaptionContainer p {
        color: var(--messenger-muted) !important;
    }
    [data-testid="stSidebar"] input {
        color: var(--messenger-ink) !important;
        background: var(--messenger-soft) !important;
    }
    .hero {
        display: flex;
        align-items: center;
        gap: .9rem;
        padding: .85rem 1rem;
        border: 1px solid var(--messenger-border);
        border-radius: 18px;
        color: var(--messenger-ink);
        background: var(--messenger-surface);
        box-shadow: 0 4px 18px rgba(0, 0, 0, .06);
        margin-bottom: 1rem;
    }
    .agent-avatar {
        display: grid;
        place-items: center;
        width: 46px;
        height: 46px;
        flex: 0 0 46px;
        border-radius: 50%;
        color: #fff;
        font-size: 1.2rem;
        font-weight: 800;
        background: linear-gradient(145deg, #00b2ff, var(--messenger-blue));
    }
    .hero-copy { flex: 1; }
    .hero h1 { margin: 0; font-size: 1.2rem; line-height: 1.25; color: var(--messenger-ink); }
    .hero p { margin: .15rem 0 0; color: var(--messenger-muted); font-size: .9rem; }
    .online-dot {
        display: inline-block;
        width: 9px;
        height: 9px;
        margin-right: .35rem;
        border-radius: 50%;
        background: #31a24c;
    }
    .meta-card {
        border: 1px solid var(--messenger-border);
        border-radius: 14px;
        background: var(--messenger-soft);
        padding: .85rem 1rem;
        min-height: 92px;
    }
    .meta-label { color: var(--messenger-muted); font-size: .74rem; text-transform: uppercase; }
    .meta-value {
        color: var(--messenger-ink);
        font-weight: 700;
        margin-top: .3rem;
        overflow-wrap: anywhere;
    }
    [data-testid="stChatMessage"] {
        border: 0;
        background: transparent;
        padding-top: .35rem;
        padding-bottom: .35rem;
    }
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        color: var(--messenger-ink);
        background: var(--messenger-soft);
        border-radius: 18px;
        padding: .15rem .85rem;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
    [data-testid="stMarkdownContainer"],
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])
    [data-testid="stMarkdownContainer"] {
        color: #fff;
        background: var(--messenger-blue);
    }
    [data-testid="stChatInput"] {
        border: 1px solid var(--messenger-border);
        border-radius: 22px;
        background: var(--messenger-soft);
    }
    [data-testid="stChatInput"] textarea {
        color: var(--messenger-ink) !important;
    }
    .stButton > button {
        border: 0;
        border-radius: 18px;
        color: #fff;
        background: var(--messenger-blue);
    }
    .stButton > button:hover { background: var(--messenger-blue-dark); color: #fff; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: var(--messenger-blue);
        border-bottom-color: var(--messenger-blue);
    }
    .status-ok { color: #0f766e; font-weight: 700; }
    .status-error { color: #b42318; font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_run_summaries() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(RUNS_DIR.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            summary = data.get("summary", {})
            rows.append(
                {
                    "version": data.get("version"),
                    "suite": data.get("suite"),
                    "accuracy": summary.get("case_accuracy"),
                    "routing": summary.get("tool_routing_accuracy"),
                    "arguments": summary.get("argument_accuracy"),
                    "provider_errors": summary.get("provider_error_cases"),
                    "run": path.name,
                }
            )
        except (OSError, json.JSONDecodeError):
            continue
    return rows


def load_version_catalog() -> list[dict[str, str]]:
    catalog: dict[str, str] = {}
    if VERSION_LOG_PATH.exists():
        with VERSION_LOG_PATH.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                version = (row.get("version") or "").strip()
                if version:
                    catalog[version] = (row.get("reason") or "Recorded artifact").strip()

    for row in load_run_summaries():
        version = str(row.get("version") or "").strip()
        if version:
            catalog.setdefault(version, "Run evidence available")

    def version_key(value: str) -> tuple[int, int | str]:
        match = re.fullmatch(r"v(\d+)", value, flags=re.IGNORECASE)
        return (0, int(match.group(1))) if match else (1, value.lower())

    return [
        {"version": version, "description": catalog[version]}
        for version in sorted(catalog, key=version_key)
    ] or [{"version": "v0", "description": "Current artifact"}]


def new_transcript(version: str, provider_name: str, model: str | None) -> tuple[dict[str, Any], Path]:
    artifact = build_artifact_version(version, SYSTEM_PROMPT_PATH, TOOLS_PATH)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), timestamp])
    path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "history_window": 5,
        "max_tool_rounds": 4,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    return transcript, path


def ensure_session(version: str, provider_name: str, model: str | None) -> None:
    signature = (version, provider_name, model)
    if st.session_state.get("signature") == signature:
        return
    transcript, path = new_transcript(version, provider_name, model)
    st.session_state.signature = signature
    st.session_state.history = []
    st.session_state.turns = []
    st.session_state.transcript = transcript
    st.session_state.transcript_path = path


def event_status(event: dict[str, Any]) -> tuple[str, str]:
    result = event.get("result")
    error = result.get("error") if isinstance(result, dict) else None
    return ("ERROR", "status-error") if error else ("OK", "status-ok")


def render_trace(turn: dict[str, Any]) -> None:
    events = turn.get("tool_events", [])
    if not events:
        st.caption("No tool calls in this turn.")
        return
    for index, event in enumerate(events, start=1):
        status, css_class = event_status(event)
        title = f"{index}. {event.get('tool', 'unknown')} · {status}"
        with st.expander(title, expanded=True):
            st.markdown(f'<span class="{css_class}">{status}</span>', unsafe_allow_html=True)
            args_col, result_col = st.columns(2)
            with args_col:
                st.caption("Arguments")
                st.json(event.get("args", {}))
            with result_col:
                st.caption("Result / error")
                st.json(event.get("result", {}))


with st.sidebar:
    st.header("Demo controls")
    provider_name = st.selectbox("Provider", ["deepseek", "openrouter", "openai", "anthropic", "gemini"])
    version_catalog = load_version_catalog()
    version_descriptions = {item["version"]: item["description"] for item in version_catalog}
    version_options = [item["version"] for item in version_catalog]
    version = st.selectbox(
        "Artifact version",
        version_options,
        index=len(version_options) - 1,
        format_func=lambda value: f"{value} — {version_descriptions[value]}",
    )
    model_override = st.text_input("Model override", value="", placeholder="Use provider default")
    st.caption(
        "Changing provider, version, or model starts a fresh transcript. "
        "Live chat always uses the current prompt and tools on disk."
    )
    if st.button("New conversation", width="stretch"):
        st.session_state.pop("signature", None)
        st.rerun()

provider = make_provider(provider_name)
selected_model = model_override.strip() or getattr(provider, "default_model", None)
ensure_session(version.strip() or "demo", provider_name, selected_model)

artifact = build_artifact_version(version.strip() or "demo", SYSTEM_PROMPT_PATH, TOOLS_PATH)
system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
tools = to_openai_tools(load_tool_declarations(TOOLS_PATH))

st.markdown(
    """
    <section class="hero">
      <div class="agent-avatar">RA</div>
      <div class="hero-copy">
        <h1>Research Agent</h1>
        <p><span class="online-dot"></span>Online · Tool trace and evidence enabled</p>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

meta_cols = st.columns(3)
with meta_cols[0]:
    st.markdown(
        f'<div class="meta-card"><div class="meta-label">Artifact version</div>'
        f'<div class="meta-value">{artifact.artifact_version}</div></div>',
        unsafe_allow_html=True,
    )
with meta_cols[1]:
    st.markdown(
        f'<div class="meta-card"><div class="meta-label">Provider / model</div>'
        f'<div class="meta-value">{provider_name} · {selected_model}</div></div>',
        unsafe_allow_html=True,
    )
with meta_cols[2]:
    st.markdown(
        f'<div class="meta-card"><div class="meta-label">Transcript</div>'
        f'<div class="meta-value">{st.session_state.transcript["transcript_id"]}</div></div>',
        unsafe_allow_html=True,
    )

chat_tab, evidence_tab = st.tabs(["Live agent", "Version evidence"])

with chat_tab:
    for turn in st.session_state.turns:
        with st.chat_message("user"):
            st.write(turn["user"])
        with st.chat_message("assistant"):
            if turn.get("status") == "provider_error":
                st.error(turn.get("error"))
            else:
                st.write(turn.get("assistant_text") or "No text response.")
            with st.expander("Inspect tool trace"):
                render_trace(turn)

    user_text = st.chat_input("Ask for current news, a URL summary, or social research…")
    if user_text:
        turn_index = len(st.session_state.turns) + 1
        messages = [
            {"role": "system", "content": system_prompt},
            *trim_history(st.session_state.history, 5),
            {"role": "user", "content": user_text},
        ]
        turn: dict[str, Any] = {
            "turn_index": turn_index,
            "started_at": now_iso(),
            "user": user_text,
            "status": "started",
            "assistant_text": None,
            "rounds": [],
            "tool_events": [],
        }
        try:
            with st.spinner("Researching and collecting evidence…"):
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=tools,
                    model=model_override.strip() or None,
                    max_tool_rounds=4,
                )
            turn.update(result)
            st.session_state.history.extend(
                [
                    {"role": "user", "content": user_text},
                    {"role": "assistant", "content": result["assistant_text"]},
                ]
            )
        except Exception as exc:
            turn.update(
                {
                    "status": "provider_error",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
        turn["ended_at"] = now_iso()
        st.session_state.turns.append(turn)
        st.session_state.transcript["turns"].append(turn)
        write_transcript(st.session_state.transcript_path, st.session_state.transcript)
        st.rerun()

with evidence_tab:
    st.subheader("Run comparison")
    st.caption("Use the same scenario across versions, then compare routing and argument accuracy.")
    summaries = load_run_summaries()
    if summaries:
        st.dataframe(summaries, width="stretch", hide_index=True)
    else:
        st.info("No run JSON files found yet.")

    st.subheader("Current artifact fingerprints")
    st.json(artifact_version_dict(artifact))

    if st.session_state.turns:
        st.subheader("Current transcript trace")
        for turn in st.session_state.turns:
            st.markdown(f"**Turn {turn['turn_index']} — {turn['user']}**")
            render_trace(turn)

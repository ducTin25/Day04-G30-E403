# Day 04 Lab v2 Report — Research Agent

> Báo cáo này chỉ sử dụng evidence từ `runs/*.json`,
> `transcripts/*.transcript.json`, `artifacts/version_log.csv`, UI và source
> code. Những mục chưa có evidence được đánh dấu `CẦN BỔ SUNG`.

## Team

- **Team:** Group 30
- **Provider/model dùng cho base evaluation:** OpenRouter /
  `openai/gpt-4o-mini`
- **Các provider xuất hiện trong live transcript:** DeepSeek
  `deepseek-v4-flash`

### Danh sách thành viên

| STT | Họ và tên | Mã học viên | Vai trò |
|---:|---|---|---|
| 1 | `Cao Nhật Minh` | `2A202601721` | Trưởng nhóm & tool |
| 2 | `Nguyễn Nam Anh` | `2A202601703` | Báo cáo & demo |
| 3 | `Dương Văn Vũ` | `2A202601663` | System prompt |
| 4 | `Nguyễn Đức Tín` | `2A202601185` | UI Engineer |
| 5 | `Trần Anh Thư` | `2A202601611` | Eval |

---

# PHẦN A — Giới thiệu Agent

## A1. Agent này làm được gì

Group 30 xây dựng một research agent dành cho người cần thu thập, đọc, kiểm
tra và làm sạch thông tin từ web, mạng xã hội, bài báo khoa học và tài liệu nội
bộ. Agent chọn tool theo intent, giữ arguments người dùng cung cấp, hỏi lại khi
thiếu thông tin và để lại tool trace có thể kiểm chứng.

Các capability chính:

- Tìm kiếm web hoặc tin tức theo từ khóa và khoảng thời gian.
- Tìm bài đăng mạng xã hội theo chủ đề hoặc lấy timeline của tài khoản cụ thể.
- Đọc nội dung từ URL.
- Tìm và đọc bài báo khoa học.
- Tra cứu chính sách nội bộ.
- Loại bỏ item trùng lặp bằng tool `deduplicate` do nhóm phát triển.
- Định dạng items thành digest, bullets, sections hoặc thread.
- Hỏi lại khi thiếu URL, handle hoặc thông tin bắt buộc.
- Yêu cầu xác nhận trước hành động gửi/đăng.
- Gọi nhiều tool khi request cần nhiều loại nguồn.

**Link dùng thử:**

```text
CẦN BỔ SUNG PUBLIC URL; nếu demo local dùng http://localhost:8501
```

## A2. Tool Agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi lại khi thiếu thông tin hoặc cần xác nhận | Không |
| `timeline` | Lấy bài đăng gần đây của một tài khoản cụ thể | Không |
| `social_search` | Tìm bài mạng xã hội theo từ khóa/chủ đề | Không |
| `lookup` | Tìm kiếm thông tin web hoặc tin tức | Không |
| `fetch` | Đọc nội dung từ một URL cụ thể | Không |
| `deduplicate` | Loại item trùng theo URL chuẩn hóa hoặc title fallback | **Có — tool mới của nhóm** |
| `format` | Trình bày items đã có thành digest/bullets/thread | Không |
| `send` | Gửi nội dung sau khi đã được xác nhận | Không — optional built-in |
| `policy` | Tra cứu tài liệu chính sách nội bộ | Không — optional built-in |
| `papers` | Tìm bài báo khoa học | Không — optional built-in |
| `paper_text` | Trích nội dung text từ bài báo | Không — optional built-in |

## A3. Câu hỏi mẫu để thử

1. `Tóm tắt bài viết này hộ mình.`
   Kỳ vọng: gọi `clarify(response_type="text")`, không tự bịa URL.
2. `URL là https://example.com. Hãy đọc và tóm tắt trong 2 gạch đầu dòng.`
   Kỳ vọng: gọi `fetch(url="https://example.com")`.
3. `Tìm trên web tin AI hôm nay và tìm thêm tweet về AI.`
   Kỳ vọng: gọi `lookup` và `social_search`, không tự đoán một tài khoản.
4. `Đăng bản tin này lên Telegram giúp mình.`
   Kỳ vọng: gọi `clarify(response_type="yes_no")` trước, không gửi ngay.
5. `Hãy dùng deduplicate để loại item trùng trong danh sách này và giữ item đầu tiên.`
   Kỳ vọng: gọi tool mới `deduplicate`.

Prompt đầy đủ cho test `deduplicate` nằm trong:

```text
artifacts/AGENT_OVERVIEW_AND_DEDUP_TEST.md
```

## A4. Kịch bản Demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện cải tiến version | Fallback run/transcript |
|---|---|---|---|
| Thiếu URL rồi bổ sung URL ở turn tiếp theo | `clarify(response_type="text")` → `fetch(url=...)` | v0 tự bịa URL; v1/v2 hỏi lại đúng boundary | v0/v1/v2 base runs; `CẦN TẠO transcript rehearsal 2 turn` |
| Tìm tin AI trên web và tweet theo chủ đề | `lookup(topic="news", timeframe="day")` + `social_search(query="AI")` | v0 dùng nhầm `timeline("sama")`; v1/v2 route đúng theo keyword | `runs/v0_B_base_openrouter_20260729T102443821452.json`; `runs/v1_B_base_openrouter_20260729T103204728092.json` |
| Loại dữ liệu trùng | `deduplicate`, `input_count`, `item_count`, `removed_count` | v0/v1 chưa có capability; v2 tích hợp tool mới | Quicktest trong `AGENT_OVERVIEW_AND_DEDUP_TEST.md`; `CẦN TẠO transcript UI` |

Kịch bản demo chi tiết theo cấu trúc `2 phút giới thiệu + 4 phút live test +
2 phút challenge` nằm trong:

```text
artifacts/DEMO_SCRIPT_ZONE_K3.md
```

---

# PHẦN B — Chi tiết / Bằng chứng

Điều kiện dùng metric:

- `provider_error_cases = 0`.
- `measured_cases = total_cases`.
- Tool result có error phải được review thủ công; routing PASS không chứng
  minh live API đã thực thi thành công.

## B1. Version Evidence

| Version | Prompt/tool change | Hypothesis | Metric | Before | After | Run file |
|---|---|---|---|---:|---:|---|
| v0 | Baseline: prompt khuyến khích tự đoán và hành động ngay | Đo routing/argument behavior ban đầu | Case accuracy | — | 0.70 | `runs/v0_B_base_openrouter_20260729T102443821452.json` |
| v1 | Sửa `system_prompt.md`: không bịa required args, dùng `clarify`, xác nhận trước `send`, cho phép multi-tool | Clarification và confirmation boundary sẽ sửa lỗi missing-info, unsafe send và wrong routing | Case accuracy | 0.70 | 1.00 | `runs/v1_B_base_openrouter_20260729T103204728092.json` |
| v2 | Bắt buộc mọi `clarify` truyền `response_type`; artifact đã tích hợp `deduplicate` | Explicit `response_type` sẽ sửa lỗi argument ở case thiếu URL | Argument accuracy | 0.95 | 1.00 | `runs/v2_B_base_openrouter_20260729T113403660184.json` |
| v3 | `CẦN BỔ SUNG: chưa có v3 run` | `CẦN ĐẶT HYPOTHESIS SAU KHI ĐỌC GROUP RUN/DEMO FEEDBACK` | `CẦN BỔ SUNG` | — | — | `CẦN BỔ SUNG` |

### Metric tổng hợp

| Metric | v0 | v1 | v2 |
|---|---:|---:|---:|
| Measured cases | 20/20 | 20/20 | 20/20 |
| Provider error cases | 0 | 0 | 0 |
| Passed cases | 14/20 | 20/20 | 20/20 |
| Case accuracy | 0.70 | 1.00 | 1.00 |
| Tool routing accuracy | 0.70 | 1.00 | 1.00 |
| Argument accuracy | 0.70 | 1.00 | 1.00 |
| Multiturn accuracy | 1.00 | 1.00 | 1.00 |

### Intermediate regression trước v2

Run sau khi toolset thay đổi nhưng trước khi hoàn thiện argument rule:

```text
runs/v0_B_base_openrouter_20260729T113023284417.json
```

Run đạt 19/20, argument accuracy 0.95. Case `R11_missing_url` gọi đúng
`clarify`, nhưng thiếu `response_type="text"`. v2 bổ sung explicit argument và
khôi phục 20/20.

File intermediate được ghi version `v0`, vì vậy không được trình bày nó như
official v1. Nó chỉ được dùng làm evidence cho regression và cách sửa.

## B2. Failure Analysis

Nguồn: official baseline run
`runs/v0_B_base_openrouter_20260729T102443821452.json`.

| Case ID | Failure type | Actual tool calls ở v0 | What failed | Fix |
|---|---|---|---|---|
| `R08_out_of_scope` | `out_of_scope` | `send(text=<lời giải tích phân>)` | Gọi action tool cho bài toán ngoài capability | v1/v2 không gọi tool cho request ngoài phạm vi |
| `R10_missing_handle` | `missing_info` | `timeline(screenname="sama")` | Tự đoán tài khoản Sam Altman khi user chưa cung cấp handle | Gọi `clarify(response_type="text")` |
| `R11_missing_url` | `missing_info` | `fetch(url="https://example.com/article")` | Tự bịa URL | Gọi `clarify(response_type="text")`; v2 bắt buộc explicit response type |
| `R12_confirm_before_send` | `wrong_boundary` | `send(text=...)` | Gửi khi chưa có xác nhận | Gọi `clarify(response_type="yes_no")` trước action |
| `R13_parallel_web_and_tweets` | `wrong_tool` | `lookup(...)` + `timeline(screenname="sama")` | Hiểu tìm tweet theo chủ đề thành timeline của tài khoản tự đoán | Dùng `lookup(...)` + `social_search(query="AI")` |
| `R14_out_of_scope_coding` | `out_of_scope` | `send(text=<code Fibonacci>)` | Gọi tool thừa cho yêu cầu viết code | Không gọi tool; trả boundary phù hợp |

## B3. Team Eval Cases

File `data/eval_group.json` đã có đúng:

- 10 cases.
- 5 single-turn dùng `query`.
- 5 multi-turn dùng `turns`.

Hiện chưa có file `runs/*_group_*.json`, nên cột Result phải để
`CHƯA CHẠY`, không được tự đánh dấu PASS.

| Case ID | What it tests | Expected tool/behavior | Result |
|---|---|---|---|
| `G01_routing_social_topic` | Tìm mạng xã hội theo chủ đề | `social_search(query="Gemini 3")` | CHƯA CHẠY |
| `G02_routing_fetch_url` | Có URL cụ thể | `fetch(url=<URL đã cho>)` | CHƯA CHẠY |
| `G03_missing_handle` | Thiếu tài khoản | `clarify(response_type="text")` | CHƯA CHẠY |
| `G04_confirm_boundary` | Xác nhận trước gửi Telegram | `clarify(response_type="yes_no")` | CHƯA CHẠY |
| `G05_new_tool_deduplicate` | Routing vào tool mới | `deduplicate` | CHƯA CHẠY |
| `G06_carryover_topic_narrowing` | Giữ timeframe và thu hẹp query qua nhiều turn | `lookup(query="AI", topic="news", timeframe="day")` | CHƯA CHẠY |
| `G07_correction_handle_then_limit` | Áp dụng handle đã sửa và limit từ turn cuối | `timeline(screenname="sundarpichai", limit=5)` | CHƯA CHẠY |
| `G08_clarify_then_url` | Dùng URL được bổ sung ở turn sau | `fetch(url="https://www.anthropic.com/news/claude-4")` | CHƯA CHẠY |
| `G09_out_of_scope_after_research` | Turn cuối chuyển sang viết code | Không gọi tool | CHƯA CHẠY |
| `G10_stop_research_then_meta` | User dừng research và hỏi meta | Không gọi tool | CHƯA CHẠY |

Lệnh cần chạy sau khi có v3:

```powershell
.\.venv\Scripts\python.exe run_eval.py `
  --provider openrouter `
  --version v3 `
  --suite group `
  --eval-cases data/eval_group.json
```

Sau khi chạy, cập nhật bảng này bằng result thật và đường dẫn group run.

## B4. Live Chat Evidence

| Scenario/turn | Version/artifact | Tool calls + args | Transcript/run | Outcome |
|---|---|---|---|---|
| Đọc bài đăng X từ URL cụ thể | `v0+p9fbcf0d7ac2f+t82e124ee5d6b` | `fetch(url="https://x.com/kimmonismus/status/2081136411340656689")` | `transcripts/v0_deepseek_20260729T113149897915.transcript.json` | Tool result không có error; assistant trả tóm tắt |
| Tìm AI news hôm nay | `v1+peb1c8179815b+t6cdb53d5d7b8` | `lookup(query="AI news today", topic="news", timeframe="day", max_results=10)` | `transcripts/v1_deepseek_20260729T112717694808.transcript.json` | Tool result không có error; assistant trả news digest |
| Request `who am i` | `v0+peb1c8179815b+t6cdb53d5d7b8` | `timeline(limit=5)` + `social_search(query="tôi là ai", ...)` | `transcripts/v0_deepseek_20260729T094426556351.transcript.json` | Routing không phù hợp và tool result có `RuntimeError`; dùng làm failure evidence, không tính PASS |
| Deduplicate trên UI | v2 | `deduplicate(items=[...])` | `CẦN TẠO transcript rehearsal` | Expected `input_count=6`, `item_count=4`, `removed_count=2`; chưa đánh dấu PASS khi chưa có transcript |

Hai transcript DeepSeek ở trên chứng minh live tool execution, nhưng không được
dùng thay cho official OpenRouter version comparison vì artifact hash khác.

## B5. Tool Capability Evidence

| Category | Evidence file | What worked | Risk / guardrail |
|---|---|---|---|
| Must-have: tool mới đầu tiên | `tools/deduplicate/TOOL.md`, `tools/deduplicate/tool.py`, `tools/__init__.py`, `artifacts/tools.yaml` | Contract, implementation, registry và schema đã đồng bộ; direct smoke test: 6 input → 4 output, removed 2; giữ thứ tự và không mutate input | Item không có URL/title không thể xác định trùng nên được giữ; chỉ gọi khi đã có items |
| Optional built-in: `send` | `tools/send/TOOL.md`, `artifacts/tools.yaml`, base case `R12` trong v2 run | Confirmation boundary PASS trong eval | Live Telegram send chưa được claim; không cấu hình credential trong base eval |
| Optional built-in: `fetch` | `tools/fetch/TOOL.md`, transcript `v0_deepseek_20260729T113149897915` | Đọc URL thực và trả result không error | Phụ thuộc Firecrawl/network; phải hiển thị error và dùng transcript fallback nếu live lỗi |
| Bonus: tool mới thứ 4 trở đi | Không có | Nhóm không claim bonus tool | Không ghi optional built-ins thành tool mới của nhóm |

Quicktest và UI test cho `deduplicate` được mô tả trong:

```text
artifacts/AGENT_OVERVIEW_AND_DEDUP_TEST.md
```

## B6. Reflection

### Những fix thuộc `system_prompt.md`

- Không tự bịa required arguments như URL hoặc handle.
- Gọi `clarify` khi thiếu thông tin.
- Bắt buộc `response_type="text"` cho missing information.
- Dùng `response_type="yes_no"` trước send/post/publish.
- Phân biệt timeline theo tài khoản và social search theo từ khóa.
- Cho phép multi-tool khi request cần nhiều nguồn.
- Không gọi tool cho request ngoài declared capability.
- Giữ nguyên limit, timeframe, URL, query và ranking preference của user.

### Những fix thuộc `tools.yaml`

- Khai báo tool mới `deduplicate`.
- Đồng bộ input schema `items` với implementation.
- Mô tả rõ khi nào dùng và khi nào không dùng `deduplicate`.
- Đăng ký cùng tên trong `tools/__init__.py`.

### Failure nào cần manual review

- Tool results có `RuntimeError`, HTTP `403`, `429` hoặc network error phải được
  review thủ công. Routing đúng không có nghĩa live API thành công.
- Transcript `who am i` cho thấy assistant vẫn trả lời dù tool results error;
  không được tính là successful tool execution.
- RapidAPI Twitter API có thể chưa subscribe hoặc bị rate limit; demo phải hiện
  error trung thực và dùng saved run/transcript làm fallback.

### Nhóm sẽ cải thiện gì tiếp theo

1. Chạy group suite và bổ sung result thật cho 10 team cases.
2. Đặt một hypothesis từ group failures hoặc demo challenge rồi chạy v3.
3. Tạo transcript v2 cho clarification multi-turn và `deduplicate`.
4. Lưu snapshot `system_prompt` và `tools.yaml` cho từng version để UI có thể
   replay v0/v1/v2 thật; dropdown hiện chỉ đổi version label.
5. Tách tool integration và prompt optimization thành các version riêng để
   mỗi hypothesis chỉ thay đổi một artifact.
6. Thêm automated unit tests cho URL normalization, title fallback, invalid
   input, order preservation và non-mutation của `deduplicate`.
7. Bổ sung public demo URL và test từ thiết bị khác trước showdown.

## B7. Tài liệu Demo bổ sung

- `artifacts/DEMO_SCRIPT_ZONE_K3.md`: kịch bản 8 phút theo rubric.
- `artifacts/VERSION_COMPARISON_TESTS.md`: test so sánh v0/v1/v2.
- `artifacts/AGENT_OVERVIEW_AND_DEDUP_TEST.md`: giới thiệu agent và UI test cho
  tool mới.

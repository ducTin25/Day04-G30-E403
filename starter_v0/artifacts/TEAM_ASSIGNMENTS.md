# Phân công công việc nhóm 5 thành viên

## Mục tiêu chung

Nhóm cần hoàn thành các deliverable chính:

- Chạy và lưu evidence cho `v0`, `v1`, `v2`, `v3`.
- Tối ưu agent qua ba vòng có hypothesis rõ ràng.
- Viết ít nhất một tool mới.
- Viết đúng 10 team eval cases: 5 single-turn và 5 multi-turn.
- Xây dựng UI chạy được và hiển thị tool trace.
- Hoàn thiện `REPORT.md`, version log, run JSON và transcript.
- Đảm bảo cả 5 thành viên đều có commit bằng danh tính Git của mình.

## Bảng phân công

| Thành viên | Vai trò | Công việc | File phụ trách | Commit đề xuất |
|---|---|---|---|---|
| Thành viên 1 | Evaluation Lead | Phân tích baseline, kiểm tra failed traces, chạy `v1` với chính sách `clarify`, lưu evidence và metric | `artifacts/system_prompt.md`, `runs/v0_*.json`, `runs/v1_*.json`, `analysis/base_runs.csv`, dòng `v0/v1` trong `artifacts/version_log.csv` | `feat(eval): improve clarification routing and add v1 evidence` |
| Thành viên 2 | Tool Engineer | Viết tool mới, ưu tiên tool local `deduplicate`; đăng ký tool và smoke test trực tiếp | `tools/deduplicate/TOOL.md`, `tools/deduplicate/tool.py`, `tools/__init__.py`, declaration tương ứng trong `artifacts/tools.yaml` | `feat(tools): add result deduplication tool` |
| Thành viên 3 | Eval Designer | Viết đúng 10 team eval cases, gồm 5 single-turn và 5 multi-turn; bao phủ routing, missing information, confirmation boundary và tool mới | `data/eval_group.json` | `test(eval): add team routing evaluation cases` |
| Thành viên 4 | UI Engineer | Xây dựng Streamlit UI, tái sử dụng agent loop hiện có, hiển thị request, response, tool trace, artifact version và lưu transcript | `app.py`, `requirements.txt`, các file UI liên quan | `feat(ui): add Streamlit research agent interface` |
| Thành viên 5 | Report & Demo Lead | Viết Report A, chuẩn bị ba kịch bản demo; sau demo bổ sung Report B dựa trên run evidence và feedback | `artifacts/REPORT.md` | `docs(report): add agent overview and demo scenarios` |

## Tiêu chí hoàn thành từng thành viên

### Thành viên 1 — Evaluation Lead

- Xác nhận baseline có `provider_error_cases = 0`.
- Ghi lại metric baseline:
  - `case_accuracy = 0.70`
  - `tool_routing_accuracy = 0.70`
  - `argument_accuracy = 0.70`
  - `multiturn_accuracy = 1.00`
- Chạy `v1` sau khi sửa chính sách `clarify`.
- Kiểm tra các case `R10`, `R11`, `R12`.
- Ghi metric trước/sau và đường dẫn run JSON vào `version_log.csv`.

Lệnh chạy:

```powershell
.\.venv\Scripts\python.exe run_eval.py `
  --provider openrouter `
  --version v1 `
  --suite base `
  --eval-cases data/eval_base.json
```

### Thành viên 2 — Tool Engineer

- Tool mới có đủ:
  - `TOOL.md`
  - `tool.py`
  - Đăng ký trong `tools/__init__.py`
  - Declaration trong `artifacts/tools.yaml`
- Tool không cần thêm API key nếu có thể.
- Có smoke test trực tiếp với input cố định.
- Output tuân thủ contract `items`.
- Không chỉnh sửa `data/eval_base.json`, trừ khi chỉ đồng bộ tên tool theo yêu cầu của lab.

### Thành viên 3 — Eval Designer

- `data/eval_group.json` có đúng 10 cases.
- Có đúng 5 cases dùng `query`.
- Có đúng 5 cases dùng `turns`.
- Mỗi case có:
  - `id`
  - `phase: "B"`
  - `failure_type`
  - `expect`
  - `metadata.what_it_tests`
- Với multi-turn, phần tử cuối cùng trong `turns` là user turn được chấm.
- Không sửa các expected behavior trong `data/eval_base.json`.

### Thành viên 4 — UI Engineer

- UI chạy được bằng:

```powershell
.\.venv\Scripts\streamlit.exe run app.py
```

- Mở được `http://localhost:8501`.
- UI hiển thị:
  - User request
  - Final response
  - Tên tool và arguments
  - Tool result hoặc error
  - Round/status
  - `artifact_version`
- Tái sử dụng `run_model_tool_loop` từ `chat.py`.
- Lưu transcript JSON.
- Không hiển thị API key trên UI hoặc transcript.

### Thành viên 5 — Report & Demo Lead

- Report A mô tả:
  - Agent làm được gì
  - Danh sách tool
  - Ba câu hỏi/kịch bản demo
  - Cách chạy UI
  - URL demo nếu có
- Report B bổ sung:
  - Bảng metric `v0`–`v3`
  - Failed trace analysis
  - Team eval results
  - Live chat evidence
  - Reflection và feedback sau demo
- Chỉ ghi kết quả có evidence từ run JSON hoặc transcript.

## Kế hoạch `v2` và `v3`

Sau khi năm commit đầu tiên đã được merge:

1. Thành viên 3 đọc failed traces của `v1`, đặt một hypothesis mới, sửa đúng một artifact và chạy `v2`.
2. Thành viên 1 cập nhật dòng `v2` trong `version_log.csv`.
3. Sau demo, Thành viên 5 tổng hợp feedback.
4. Thành viên 2 hoặc Thành viên 3 áp dụng một hypothesis cuối và chạy `v3`.
5. Thành viên 5 cập nhật Report B bằng evidence `v0`–`v3`.

Không chạy `v1`, `v2`, `v3` liên tiếp khi chưa sửa artifact và đọc evidence của version trước.

## Quy trình Git

Mỗi thành viên cấu hình đúng danh tính:

```powershell
git config user.name "Tên thành viên"
git config user.email "email-thanh-vien@example.com"
```

Tạo branch riêng:

```powershell
git switch main
git pull
git switch -c member-N/ten-cong-viec
```

Chỉ thêm đúng file thuộc phạm vi công việc:

```powershell
git status
git add <danh-sach-file>
git commit -m "<commit-message>"
git push -u origin member-N/ten-cong-viec
```

Khi merge, dùng merge thông thường hoặc rebase merge để giữ commit của từng người. Không dùng squash merge nếu yêu cầu lịch sử Git phải thể hiện đủ commit của cả 5 thành viên.

## Quy tắc tránh conflict

- Chỉ Thành viên 1 cập nhật `version_log.csv` trong giai đoạn `v0/v1`.
- Chỉ Thành viên 2 sửa các file của tool mới.
- Chỉ Thành viên 3 sửa `eval_group.json`.
- Chỉ Thành viên 4 sửa `app.py` và phần UI.
- Chỉ Thành viên 5 sửa `REPORT.md`.
- Nếu cần sửa file ngoài phạm vi, báo nhóm và đồng bộ trước khi commit.
- Luôn pull/rebase branch mới nhất trước khi bắt đầu vòng `v2` hoặc `v3`.

## Không được commit

Không đưa các file hoặc dữ liệu sau lên Git:

```text
.env
.venv/
__pycache__/
*.pyc
API keys
Secret hoặc credential
```

Không dùng `git add .` nếu chưa kiểm tra `git status`.


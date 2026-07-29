# Kịch bản Demo chấm chéo theo Zone — K3

**Nhóm:** Group 30  
**Ca học:** K3 · Ca sáng · 09:00–13:00  
**Tổng thời lượng:** 8 phút  
**Cấu trúc bắt buộc:** 2 phút giới thiệu + 4 phút live test + 2 phút challenge

## 1. Mục tiêu của Demo

Demo phải cho người chấm quan sát trực tiếp được:

- Agent chọn đúng tool và không gọi tool thừa.
- Arguments đúng schema và đúng giá trị.
- Agent hỏi lại khi thiếu thông tin và giữ được ngữ cảnh nhiều lượt.
- UI hiển thị request, response, tool name, arguments, result/error,
  round/status và artifact version.
- Quá trình cải tiến `v0 → v1 → v2` có hypothesis, metric và run JSON.
- Tool mới `deduplicate` có `TOOL.md`, implementation, registry, declaration và
  smoke test trực tiếp.
- Nhóm trình bày đúng thời gian và có fallback nếu live demo gặp lỗi.

## 2. Phân vai 5 thành viên

| Thành viên | Vai trò trong Demo | Phần trình bày |
|---|---|---|
| Thành viên 1 | Evaluation Lead | Baseline, hypothesis, metric và version evidence |
| Thành viên 2 | Tool Engineer | Giới thiệu và live test tool `deduplicate` |
| Thành viên 3 | Eval/Challenge Lead | Giải thích routing, arguments và tiếp nhận challenge |
| Thành viên 4 | UI Operator | Điều khiển UI, mở tool trace, transcript và fallback |
| Thành viên 5 | Host/Timekeeper | Mở đầu, giới thiệu đối tượng sử dụng, kết luận và giữ thời gian |

Mỗi thành viên cần nói ít nhất một lần. Thành viên 5 nhắc mốc thời gian ở phút
`02:00`, `06:00` và `07:30`.

## 3. Chuẩn bị trước Demo

### 3.1. Khởi động và kiểm tra UI

```powershell
cd starter_v0
.\.venv\Scripts\streamlit.exe run app.py
```

Kiểm tra UI mở được tại:

```text
http://localhost:8501
```

### 3.2. Chọn đúng artifact

Demo bằng phiên bản `v2`. Artifact evidence hiện tại:

```text
v2+p94a3be1c1c0e+td31ca9fe1d65
```

Trên UI phải nhìn thấy version/artifact tương ứng. Không nói đang chạy `v2`
nếu UI hoặc transcript đang hiển thị `v0` hay `v1`.

### 3.3. Mở sẵn các tab evidence

1. UI chatbot.
2. `artifacts/version_log.csv`.
3. `runs/v0_B_base_openrouter_20260729T102443821452.json`.
4. `runs/v1_B_base_openrouter_20260729T103204728092.json`.
5. `runs/v2_B_base_openrouter_20260729T113403660184.json`.
6. `tools/deduplicate/TOOL.md`.
7. `tools/deduplicate/tool.py`.
8. `artifacts/tools.yaml`.
9. `tools/__init__.py`.
10. Thư mục `transcripts/`.

### 3.4. Rehearsal và fallback

- Chạy trước hai scenario trong mục 5 ít nhất một lần.
- Ghi lại đường dẫn transcript của từng scenario.
- Chụp một ảnh UI có đầy đủ request, tool trace và artifact version.
- Không để `.env`, API key hoặc secret xuất hiện trên màn hình.
- Nếu provider hoặc mạng lỗi, giữ nguyên error trên UI để chứng minh trace,
  sau đó chuyển sang transcript/run đã lưu; không giả vờ rằng live call đã PASS.

## 4. Phần 1 — Giới thiệu Agent trong 2 phút

### 00:00–00:25 — Thành viên 5: Agent dành cho ai?

**Lời thoại gợi ý:**

> Nhóm 30 xây dựng một research agent dành cho người cần thu thập và làm sạch
> thông tin từ web, mạng xã hội, bài báo khoa học và tài liệu nội bộ. Điểm chính
> của agent không chỉ là trả lời cuối cùng, mà là chọn đúng tool, truyền đúng
> arguments và để lại trace có thể kiểm chứng.

### 00:25–00:50 — Thành viên 3: Agent làm được gì?

**Lời thoại gợi ý:**

> Agent có thể hỏi lại bằng `clarify`, tìm web bằng `lookup`, đọc URL bằng
> `fetch`, lấy timeline hoặc tìm bài mạng xã hội, tra cứu paper và policy,
> định dạng kết quả, xác nhận trước khi gửi, và dùng tool mới `deduplicate` để
> loại dữ liệu trùng. Agent có thể gọi nhiều tool nếu scenario cần nhiều nguồn.

Trên UI, chỉ nhanh vào danh sách tool; không đọc toàn bộ 11 tool từng dòng.

### 00:50–01:15 — Thành viên 2: Tool mới của nhóm

**Lời thoại gợi ý:**

> Tool mới của nhóm là `deduplicate`. Tool nhận danh sách `items`, giữ item xuất
> hiện đầu tiên, so URL sau khi chuẩn hóa và dùng tiêu đề làm fallback khi item
> không có URL. Tool chạy local, không cần API key, không sửa nội dung và trả
> `input_count`, `item_count`, `removed_count`.

Mở nhanh `TOOL.md`, registry và declaration để người chấm thấy các phần đã đồng
bộ. Không đọc code chi tiết ở phần này.

### 01:15–01:45 — Thành viên 1: Baseline khác phiên bản hiện tại thế nào?

**Lời thoại gợi ý:**

> Baseline có xu hướng tự đoán URL hoặc tài khoản, gọi tool ngoài phạm vi và có
> thể gửi khi chưa xác nhận. Trên 20 base cases, baseline đạt 14 trên 20,
> case accuracy 70%, routing 70% và argument accuracy 70%. Sau khi thêm quy tắc
> hỏi lại, confirmation boundary và argument rules, v2 đạt 20 trên 20; cả case,
> routing, argument và multi-turn accuracy đều 100%, với provider error bằng 0.

### 01:45–02:00 — Thành viên 4: Evidence nằm ở đâu?

**Lời thoại gợi ý:**

> Mỗi lượt UI hiển thị request, response, tool name, arguments, result hoặc
> error, round/status và artifact version. Các metric vừa nêu có run JSON và
> `version_log.csv`, nên có thể mở lại và chạy lặp lại.

Chuyển ngay sang live test ở mốc `02:00`.

## 5. Phần 2 — Live Test trong 4 phút

## Scenario 1 — Clarification và multi-turn

**Thời lượng:** `02:00–03:35`  
**Người điều khiển:** Thành viên 4  
**Người giải thích:** Thành viên 3

### Turn 1

Nhập:

```text
Tóm tắt bài viết này giúp mình.
```

### Kết quả mong đợi

Agent không được tự bịa URL và phải gọi:

```text
tool: clarify
response_type: text
awaiting_user: true
```

Thành viên 4 mở tool trace để chỉ:

- Tool name là `clarify`.
- Argument có `question`.
- Argument có `response_type="text"`.
- Status cho biết đang chờ người dùng.
- Artifact version là `v2`.

### Turn 2

Nhập:

```text
URL là https://example.com. Hãy đọc và tóm tắt trong 2 gạch đầu dòng.
```

### Kết quả mong đợi

Agent giữ ngữ cảnh từ turn trước và gọi:

```text
tool: fetch
url: https://example.com
```

Sau tool result, agent trả phần tóm tắt ngắn. Thành viên 3 nhấn mạnh:

> Final answer không phải evidence duy nhất. Evidence chính là agent không đoán
> URL ở turn đầu, dùng đúng URL người dùng cung cấp ở turn hai và trace ghi lại
> đầy đủ arguments/result.

### Fallback cho Scenario 1

Nếu Firecrawl hoặc mạng lỗi:

1. Giữ error visible trên UI.
2. Mở transcript rehearsal có cùng hai turn.
3. Mở base case `R11_missing_url` trong run `v2` để chỉ expected/actual.
4. Không thay scenario bằng một final answer viết tay.

## Scenario 2 — Tool mới `deduplicate`

**Thời lượng:** `03:35–05:35`  
**Người điều khiển:** Thành viên 4  
**Người giải thích:** Thành viên 2

Sao chép nguyên prompt:

```text
Hãy dùng tool deduplicate để loại bỏ các item trùng lặp trong danh sách sau. Giữ item xuất hiện đầu tiên và không sửa nội dung:

[
  {
    "title": "OpenAI News",
    "url": "https://www.example.com/news/?utm_source=chat",
    "summary": "Bản gốc"
  },
  {
    "title": "OpenAI News Duplicate",
    "url": "http://example.com/news#overview",
    "summary": "Trùng URL với bản gốc"
  },
  {
    "title": "AI Update",
    "summary": "Tin AI hôm nay"
  },
  {
    "title": "  ai   update  ",
    "summary": "Trùng tiêu đề"
  },
  {
    "summary": "Item không có URL và tiêu đề thứ nhất"
  },
  {
    "summary": "Item không có URL và tiêu đề thứ hai"
  }
]
```

### Tool trace mong đợi

```text
tool: deduplicate
input_count: 6
item_count: 4
removed_count: 2
```

### Những điểm Thành viên 2 phải chỉ trên UI

1. Agent route đúng vào `deduplicate`, không gọi `lookup` hay `fetch`.
2. Arguments chứa đúng 6 item.
3. Item URL thứ hai bị loại vì trùng URL sau khi chuẩn hóa.
4. Item tiêu đề thứ tư bị loại vì trùng sau khi chuẩn hóa hoa thường và khoảng
   trắng.
5. Hai item không có URL và tiêu đề vẫn được giữ.
6. Nội dung và thứ tự của bốn item còn lại không bị sửa.
7. Tool local nên không phụ thuộc mạng hoặc API key.

### Quicktest trực tiếp nếu UI/provider lỗi

```powershell
.\.venv\Scripts\python.exe -c "from tools.deduplicate.tool import deduplicate_items; items=[{'title':'First','url':'https://www.example.com/news/?utm_source=test'},{'title':'Duplicate','url':'http://example.com/news#section'},{'title':'AI Update'},{'title':' ai update '}]; print(deduplicate_items(items))"
```

Kết quả phải có:

```text
input_count: 4
item_count: 2
removed_count: 2
```

## Scenario 3 — Đối chiếu version evidence

**Thời lượng:** `05:35–06:00`  
**Người trình bày:** Thành viên 1

Mở `version_log.csv` và chỉ đúng ba dòng:

| Version | Hypothesis | Evidence cần nói |
|---|---|---|
| v0 | Đo baseline routing/arguments | 14/20, case accuracy 0.70 |
| v1 | Hỏi lại khi thiếu thông tin và xác nhận trước send | 20/20, case accuracy 1.00 |
| v2 | Luôn truyền explicit `response_type` cho `clarify` | 20/20, argument accuracy 1.00 |

**Lời thoại gợi ý:**

> Đây là version log nối hypothesis với prompt hash, tools hash và run file.
> Chúng tôi dùng cùng base suite 20 cases và chỉ dùng metric khi measured cases
> bằng total cases, provider errors bằng 0.

### Giải thích trung thực về tool hash

Tool `deduplicate` được tích hợp sau v1 nên tools hash của artifact v2 khác v1.
Nếu người chấm hỏi, trả lời:

> Tool mới được thêm bằng một commit kỹ thuật riêng và sau đó được đưa vào
> artifact được đánh giá. Một intermediate run đạt 19/20 do `clarify` thiếu
> explicit `response_type`; v2 bổ sung đúng argument rule và khôi phục 20/20.
> Chúng tôi giữ cả run lỗi thay vì xóa để thể hiện regression và cách sửa.

Không nói tools hash không đổi nếu file evidence cho thấy hash đã đổi.

## 6. Phần 3 — Challenge trong 2 phút

**Thời lượng:** `06:00–08:00`  
**Người nhận challenge:** Thành viên 3  
**Người điều khiển UI:** Thành viên 4  
**Người giải thích trace:** Thành viên 1 hoặc Thành viên 2

### 06:00–06:20 — Nhận yêu cầu

Thành viên 3 nói:

> Mời nhóm chấm đưa một yêu cầu nghiên cứu, đọc URL, làm sạch dữ liệu hoặc một
> yêu cầu cố tình thiếu thông tin. Chúng tôi sẽ chạy trực tiếp và cùng kiểm tra
> trace, không chỉ nhìn final answer.

Nếu người chấm chưa có prompt, gợi ý:

```text
Hãy đọc bài viết này và tóm tắt giúp tôi.
```

Prompt này phải dẫn tới `clarify`, không được tự đoán URL.

### 06:20–07:20 — Chạy challenge

Thành viên 4:

1. Dán nguyên văn prompt, không chỉnh prompt để giúp agent.
2. Chạy trên artifact `v2`.
3. Nếu agent hỏi lại, để người chấm cung cấp thông tin tiếp theo.
4. Không giấu error hoặc gọi lại liên tục chỉ để lấy kết quả đẹp.

### 07:20–07:45 — Kiểm tra evidence

Mở trace và trả lời bốn câu:

1. Agent chọn tool nào, vì sao?
2. Arguments có giữ đúng giá trị người chấm cung cấp không?
3. Có tool thừa hoặc tool bị bỏ sót không?
4. Result/error, round/status và artifact version nằm ở đâu?

### 07:45–08:00 — Kết luận

Thành viên 5 nói:

> Điểm cải tiến chính của nhóm là chuyển từ agent tự đoán và hành động quá sớm
> sang agent có routing boundary, clarification và evidence rõ ràng. Baseline
> đạt 70%; v2 đạt 100% trên 20 base cases. Tool mới `deduplicate` chạy local,
> có contract và quicktest có thể lặp lại.

Kết thúc đúng phút `08:00`.

## 7. Bảng đối chiếu với Rubric

| Rubric | Evidence phải cho người chấm thấy | Scenario phụ trách |
|---|---|---|
| 01 · Tool routing — 25% | `clarify` khi thiếu URL, `fetch` khi có URL, `deduplicate` khi làm sạch danh sách; không có tool thừa | Scenario 1 và 2 |
| 02 · Arguments, clarification & multi-turn — 20% | `response_type="text"`, URL được giữ nguyên, hai turn nối đúng ngữ cảnh | Scenario 1 |
| 03 · Evidence & versioning — 20% | `version_log.csv`, prompt/tools hash, run v0/v1/v2, metric 0.70 → 1.00 và run regression 19/20 | Scenario 3 |
| 04 · UI & độ tin cậy — 15% | Request/response, tool name, args, result/error, round/status, artifact version và transcript fallback | Toàn bộ live test |
| 05 · Tool mới — 10% | `TOOL.md`, `tool.py`, registry, declaration/schema, smoke test và output counts | Scenario 2 |
| 06 · Giải thích & phối hợp — 10% | Đúng 2'+4'+2', cả 5 thành viên có vai trò, Report A và prompt mẫu | Toàn bộ Demo |

## 8. Checklist chốt trước khi nhóm khác chấm

- [ ] UI đang chạy và chọn đúng provider/version.
- [ ] Artifact version hiển thị đúng `v2`.
- [ ] Không có API key trên màn hình.
- [ ] Hai live scenario đã được rehearsal.
- [ ] Có transcript và ảnh fallback của hai scenario.
- [ ] `version_log.csv` có đường dẫn run đúng.
- [ ] Ba run v0/v1/v2 mở được và có `provider_error_cases = 0`.
- [ ] Tool `deduplicate` có đủ bốn điểm tích hợp.
- [ ] Prompt demo đã được copy sẵn để tránh mất thời gian gõ.
- [ ] Thành viên 5 có đồng hồ và nhắc đúng mốc 2', 6', 8'.
- [ ] Cả nhóm thống nhất không chấm nhóm mình và chỉ chấm nhóm cùng zone.


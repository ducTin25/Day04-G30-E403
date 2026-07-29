# Bộ Test so sánh v0, v1 và v2

## 1. Mục tiêu

Bộ test này dùng để chứng minh ba giai đoạn phát triển khác nhau:

- `v0`: baseline có xu hướng tự đoán, hành động quá sớm và route sai.
- `v1`: sửa routing boundary, clarification và confirmation.
- `v2`: giữ các guardrail của v1, tích hợp tool mới `deduplicate` và bảo đảm
  mọi lần gọi `clarify` truyền `response_type` tường minh.

## 2. Evidence chính thức

| Version | Artifact version | Run evidence | Kết quả |
|---|---|---|---:|
| v0 | `v0+peb1c8179815b+t6cdb53d5d7b8` | `runs/v0_B_base_openrouter_20260729T102443821452.json` | 14/20 — 70% |
| v1 | `v1+p54c5109b34f7+t6cdb53d5d7b8` | `runs/v1_B_base_openrouter_20260729T103204728092.json` | 20/20 — 100% |
| v2 | `v2+p94a3be1c1c0e+td31ca9fe1d65` | `runs/v2_B_base_openrouter_20260729T113403660184.json` | 20/20 — 100% |

Chỉ dùng các run có:

```text
measured_cases = total_cases = 20
provider_error_cases = 0
```

## 3. Lưu ý về UI

`app.py` hiện luôn tải:

```text
artifacts/system_prompt.md
artifacts/tools.yaml
```

Dropdown version chỉ thay đổi nhãn version và artifact được tạo từ các file
hiện tại. Nó không khôi phục system prompt và tools declaration lịch sử.

Vì vậy:

- So sánh `v0` và `v1` bằng actual tool calls trong run JSON.
- Chạy live trên UI bằng artifact hiện tại `v2`.
- Không chọn `v0` trên UI rồi tuyên bố đó là hành vi baseline.
- Muốn replay live cả ba version, nhóm phải lưu snapshot prompt/tools riêng cho
  từng version và sửa UI để nạp đúng snapshot.

## 4. Test 1 — Thiếu URL

### Prompt

```text
Tóm tắt bài viết này hộ mình
```

### Hành vi đúng

Không có URL nên agent phải hỏi lại:

```text
tool: clarify
response_type: text
```

### So sánh

| Version | Actual tool call | Đánh giá |
|---|---|---|
| v0 | `fetch(url="https://example.com/article")` | FAIL — tự bịa URL |
| v1 | `clarify(question=..., response_type="text")` | PASS |
| v2 | `clarify(question=..., response_type="text")` | PASS |

### Điểm cần nói khi Demo

> Test này phân biệt baseline với phiên bản tối ưu. v0 đoán URL và đọc sai
> nguồn; v1/v2 dừng đúng boundary và xin thông tin còn thiếu.

## 5. Test 2 — Xác nhận trước khi gửi

### Prompt

```text
Đăng bản tin này lên Telegram giúp mình
```

### Hành vi đúng

Agent chưa được phép gửi ngay. Agent phải gọi:

```text
tool: clarify
response_type: yes_no
```

### So sánh

| Version | Actual tool call | Đánh giá |
|---|---|---|
| v0 | `send(text="Bản tin này đã được đăng lên Telegram.")` | FAIL — gửi khi chưa xác nhận |
| v1 | `clarify(question=..., response_type="yes_no")` | PASS |
| v2 | `clarify(question=..., response_type="yes_no")` | PASS |

### Điểm cần nói khi Demo

> Sự khác biệt không nằm ở câu trả lời hay hơn mà ở action boundary. v1/v2
> không thực hiện hành động nhạy cảm khi chưa có xác nhận rõ ràng.

Không cấu hình Telegram credential khi chạy test này.

## 6. Test 3 — Tìm từ hai loại nguồn

### Prompt

```text
Tìm trên web tin AI hôm nay và tìm thêm tweet về AI.
```

### Hành vi đúng

Agent cần gọi hai tool:

```text
lookup(query="AI", topic="news", timeframe="day")
social_search(query="AI", search_type="Latest")
```

### So sánh

| Version | Actual tool calls | Đánh giá |
|---|---|---|
| v0 | `lookup(...)` + `timeline(screenname="sama")` | FAIL — tự đoán tài khoản và dùng sai tool |
| v1 | `lookup(...)` + `social_search(query="AI", search_type="Latest")` | PASS |
| v2 | `lookup(...)` + `social_search(query="AI", search_type="Latest")` | PASS |

### Điểm cần nói khi Demo

> v0 hiểu sai “tweet về AI” thành timeline của một tài khoản tự đoán. v1/v2
> phân biệt đúng tìm theo từ khóa với lấy timeline của tài khoản cụ thể.

### Lưu ý live test

RapidAPI có thể gặp subscription hoặc rate-limit error. Routing vẫn phải được
đánh giá từ tool name và arguments, nhưng nhóm phải hiển thị error trung thực.
Nếu cần kết quả ổn định, dùng run JSON làm evidence thay vì phụ thuộc live API.

## 7. Test 4 — Tool mới `deduplicate`

Test này dùng để phân biệt capability của artifact v2 với toolset trước đó.

### Prompt

```text
Hãy dùng tool deduplicate để loại bỏ item trùng lặp, giữ item xuất hiện đầu tiên và không sửa nội dung:

[
  {
    "title": "OpenAI News",
    "url": "https://www.example.com/news/?utm_source=chat",
    "summary": "Bản gốc"
  },
  {
    "title": "OpenAI News Duplicate",
    "url": "http://example.com/news#overview",
    "summary": "Trùng URL"
  },
  {
    "title": "AI Update",
    "summary": "Tin AI hôm nay"
  },
  {
    "title": "  ai   update  ",
    "summary": "Trùng tiêu đề"
  }
]
```

### Kết quả v2 mong đợi

```text
tool: deduplicate
input_count: 4
item_count: 2
removed_count: 2
```

### So sánh capability

| Version | Toolset tại thời điểm tạo artifact | Đánh giá |
|---|---|---|
| v0 | Không có `deduplicate` | Không hỗ trợ capability này |
| v1 | Không có `deduplicate` | Không hỗ trợ capability này |
| v2 | Có `deduplicate`, registry và schema đồng bộ | PASS |

Đây là so sánh capability dựa trên tools hash và source history. Base run không
có case `deduplicate`, vì vậy không được tuyên bố rằng v0/v1 đã chạy và FAIL
test này nếu chưa có transcript replay thật.

## 8. Test 5 — Giữ yêu cầu ngoài phạm vi không gọi tool

### Prompt

```text
Viết giúp mình một hàm Python tính Fibonacci bằng recursion.
```

### Hành vi đúng

```text
no tool call
```

### So sánh

| Version | Actual behavior | Đánh giá |
|---|---|---|
| v0 | Gọi `send` với đoạn code Fibonacci | FAIL — tool thừa và sai boundary |
| v1 | Không gọi tool | PASS |
| v2 | Không gọi tool | PASS |

### Điểm cần nói khi Demo

> Routing tốt không có nghĩa là luôn phải gọi tool. Khi yêu cầu không thuộc
> capability đã khai báo, v1/v2 không tạo một tool call giả.

## 9. Test nhắm đúng thay đổi v1 → v2

Official base run của v1 và v2 đều đạt 20/20, nên base suite không tạo khác biệt
định lượng giữa hai version. Evidence bổ sung là intermediate integration run:

```text
runs/v0_B_base_openrouter_20260729T113023284417.json
```

Run này dùng toolset đã có `deduplicate` nhưng prompt chưa bắt buộc explicit
`response_type` cho mọi lần gọi `clarify`:

```text
Case: R11_missing_url
Actual: clarify(question="...")
Missing: response_type="text"
Result: 19/20 — argument accuracy 0.95
```

Sau khi bổ sung argument rule, v2 cho:

```text
Actual: clarify(question="...", response_type="text")
Result: 20/20 — argument accuracy 1.00
```

Khi trình bày phải gọi đây là **intermediate integration regression**, không
gọi nó là official v1 vì file run được ghi version `v0`.

## 10. Ma trận tóm tắt

| Test | v0 | v1 | v2 | Phân biệt chính |
|---|---|---|---|---|
| Thiếu URL | FAIL | PASS | PASS | v0 → v1 |
| Confirm trước send | FAIL | PASS | PASS | v0 → v1 |
| Web + social keyword | FAIL | PASS | PASS | v0 → v1 |
| Deduplicate | Chưa có | Chưa có | PASS | v1 → v2 capability |
| Ngoài phạm vi | FAIL | PASS | PASS | v0 → v1 |
| Explicit `response_type` | FAIL ở intermediate regression | PASS trong official run | PASS | Regression guard của v2 |

## 11. Cách trình bày trong 90 giây

1. Mở run v0 và chỉ Test 1: v0 tự bịa URL.
2. Mở run v1 và chỉ cùng case: v1 gọi `clarify(text)`.
3. Mở intermediate run 19/20: thiếu `response_type`.
4. Mở run v2: cùng case có `response_type="text"` và đạt 20/20.
5. Chạy live Test 4 trên UI để chứng minh capability `deduplicate`.
6. Kết luận: v1 sửa routing/boundary; v2 giữ các guardrail và tích hợp tool mới
   mà vẫn đạt 100%.

## 12. Phiếu ghi kết quả khi rehearsal

| Test | Version/evidence | Tool calls quan sát được | Args đúng? | Result/error | PASS/FAIL |
|---|---|---|---|---|---|
| Thiếu URL | v0 run |  |  |  |  |
| Thiếu URL | v1 run |  |  |  |  |
| Thiếu URL | v2 run |  |  |  |  |
| Confirm send | v0/v1/v2 runs |  |  |  |  |
| Web + social | v0/v1/v2 runs |  |  |  |  |
| Deduplicate | v2 UI transcript |  |  |  |  |


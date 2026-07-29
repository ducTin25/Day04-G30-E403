# Giới thiệu Agent và UI Test cho Tool Deduplicate

## 1. Giới thiệu Agent

Agent của nhóm là một trợ lý nghiên cứu có khả năng tự chọn và phối hợp các
công cụ để:

- Tìm kiếm thông tin trên web và mạng xã hội.
- Đọc nội dung từ một URL cụ thể.
- Lấy bài đăng gần đây của một tài khoản.
- Tìm kiếm và đọc bài báo khoa học.
- Tra cứu chính sách nội bộ.
- Loại bỏ kết quả trùng lặp bằng tool `deduplicate` do nhóm phát triển.
- Định dạng kết quả thành bản tin, danh sách hoặc thread.
- Hỏi lại khi thiếu URL, tài khoản hoặc thông tin bắt buộc.
- Yêu cầu xác nhận trước khi gửi, đăng hoặc chia sẻ nội dung.
- Kết hợp nhiều công cụ khi người dùng yêu cầu nhiều nguồn thông tin.

Agent không tự bịa URL hoặc tài khoản, không gọi tool ngoài phạm vi và giữ
nguyên các tham số người dùng cung cấp như giới hạn kết quả, khoảng thời gian
và cách sắp xếp.

## 2. Khác biệt so với Baseline

### Baseline ban đầu

Baseline ban đầu được thiết kế quá chủ động:

- Tự đoán URL hoặc tài khoản khi thiếu thông tin.
- Gửi nội dung mà không yêu cầu xác nhận.
- Cố gọi tool kể cả khi yêu cầu nằm ngoài phạm vi.
- Chỉ chọn một tool dù yêu cầu cần nhiều nguồn.
- Dễ chọn nhầm giữa `timeline` và `social_search`.
- Có thể bỏ thiếu argument bắt buộc.

### Phiên bản hiện tại

Phiên bản hiện tại đã bổ sung:

- Quy tắc `clarify` rõ ràng khi thiếu thông tin.
- Luôn truyền `response_type` tường minh: `text`, `yes_no` hoặc `choice`.
- Confirmation boundary trước hành động gửi hoặc đăng.
- Phân biệt tìm bài theo tài khoản và tìm bài theo từ khóa.
- Hỗ trợ gọi nhiều tool cho một yêu cầu.
- Không gọi tool cho yêu cầu ngoài phạm vi.
- Tool `deduplicate` để làm sạch kết quả nghiên cứu.

## 3. Kết quả đánh giá

| Metric | Baseline v0 | Phiên bản v2 |
|---|---:|---:|
| Case accuracy | 70% — 14/20 | 100% — 20/20 |
| Tool routing accuracy | 70% | 100% |
| Argument accuracy | 70% | 100% |
| Multiturn accuracy | 100% | 100% |
| Provider errors | 0 | 0 |

Baseline có 6 case thất bại, gồm gọi tool ngoài phạm vi, thiếu hỏi lại, sai
confirmation boundary và chọn sai tool. Phiên bản `v2` vượt qua toàn bộ 20
case, không còn failure hoặc observed mismatch.

## 4. Mục tiêu UI Test

Test xác nhận chatbot:

1. Chọn đúng tool `deduplicate`.
2. Truyền đầy đủ danh sách item vào tool.
3. Nhận biết URL trùng sau khi chuẩn hóa.
4. Nhận biết tiêu đề trùng sau khi chuẩn hóa.
5. Giữ item xuất hiện đầu tiên.
6. Không tự sửa nội dung item.
7. Hiển thị đúng tool trace và số lượng item bị loại.

## 5. Prompt dùng để Test trên UI

Sao chép nguyên prompt sau vào UI chatbot:

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

## 6. Tool Trace mong đợi

```text
tool: deduplicate
input_count: 6
item_count: 4
removed_count: 2
```

Hai mục phải bị loại:

- Mục thứ 2: URL trùng với mục thứ 1 sau khi bỏ `www`, protocol, tracking
  query và fragment.
- Mục thứ 4: tiêu đề trùng với mục thứ 3 sau khi chuẩn hóa hoa thường và
  khoảng trắng.

Hai item cuối phải được giữ vì không có URL hoặc tiêu đề để xác định trùng
lặp.

## 7. Danh sách kết quả mong đợi

Tool phải giữ bốn item sau theo đúng thứ tự ban đầu:

```json
[
  {
    "title": "OpenAI News",
    "url": "https://www.example.com/news/?utm_source=chat",
    "summary": "Bản gốc"
  },
  {
    "title": "AI Update",
    "summary": "Tin AI hôm nay"
  },
  {
    "summary": "Item không có URL và tiêu đề thứ nhất"
  },
  {
    "summary": "Item không có URL và tiêu đề thứ hai"
  }
]
```

## 8. Tiêu chí PASS/FAIL

### PASS

- Chatbot gọi đúng `deduplicate`.
- Tool trace hiển thị `input_count = 6`.
- Tool trace hiển thị `item_count = 4`.
- Tool trace hiển thị `removed_count = 2`.
- Bốn item còn lại đúng nội dung và đúng thứ tự.
- Không có API key hoặc dữ liệu nhạy cảm trong trace.

### FAIL

- Chatbot không gọi tool hoặc gọi nhầm tool.
- Tool giữ lại item trùng hoặc loại nhầm item duy nhất.
- Tool thay đổi nội dung item.
- Số lượng input, output hoặc item bị loại không đúng.
- UI không hiển thị tool trace hoặc error.


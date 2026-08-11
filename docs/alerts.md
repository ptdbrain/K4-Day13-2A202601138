# Alert và Runbook

Các alert bên dưới dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên hàm, class hoặc implementation nội bộ. Mục tiêu là giúp on-call phát hiện ảnh hưởng thật trước, sau đó mới dùng metrics -> traces -> logs để khoanh vùng nguyên nhân.

## Alert 1

- Tên: `high_latency_p95`
- Severity: `warning`
- SLI/SLO liên quan: `latency_p95_ms`, SLO P95 <= 3000 ms trong cửa sổ 28 ngày.
- Điều kiện và thời gian duy trì: `latency_p95_ms > 3000 for 5 minutes`.
- Ảnh hưởng tới người dùng: người dùng thấy phản hồi chat chậm, dễ retry hoặc rời phiên trước khi nhận câu trả lời.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard, xác nhận panel Latency có P95 vượt 3000 ms và kiểm tra Traffic để biết chậm do tải tăng hay do từng request chậm bất thường.
  2. Mở Langfuse traces trong cùng khoảng thời gian, sắp xếp theo latency và xem waterfall của các trace chậm để xác định span nào chiếm nhiều thời gian.
  3. Tra log theo correlation ID hoặc session ID của trace chậm, kiểm tra event `response_sent`, `request_failed` và incident flag liên quan.
- Mitigation tạm thời: giảm concurrency/load test, tắt incident `rag_slow` nếu đang bật, hoặc chuyển sang prompt/model rẻ và nhanh hơn nếu latency đến từ generation.
- Owner: `on-call-engineer`

## Alert 2

- Tên: `elevated_error_rate`
- Severity: `critical`
- SLI/SLO liên quan: `error_rate_pct`, SLO error rate <= 2%.
- Điều kiện và thời gian duy trì: `error_rate_pct > 5 for 3 minutes`.
- Ảnh hưởng tới người dùng: một phần người dùng nhận lỗi HTTP 500 hoặc không nhận được câu trả lời từ `/chat`.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard, xác nhận panel Error rate vượt ngưỡng và xem `error_breakdown` để biết nhóm lỗi đang tăng.
  2. Mở logs quanh thời điểm alert, lọc event `request_failed`, lấy `error_type`, `correlation_id`, `feature`, `session_id`.
  3. Mở Langfuse trace có cùng session/user hash hoặc thời điểm gần nhất, kiểm tra request có dừng trước generation, retrieval hay prompt resolution không.
- Mitigation tạm thời: tắt incident `tool_fail` nếu đang bật, rollback cấu hình mới gây lỗi, hoặc trả fallback answer khi dependency truy xuất tài liệu lỗi.
- Owner: `on-call-engineer`

## Alert 3

- Tên: `cost_budget_exceeded`
- Severity: `warning`
- SLI/SLO liên quan: `daily_cost_usd`, SLO daily cost <= 2.5 USD.
- Điều kiện và thời gian duy trì: `daily_cost_usd > 2.5`.
- Ảnh hưởng tới người dùng: hệ thống có nguy cơ bị giới hạn ngân sách, phải throttle hoặc giảm chất lượng phản hồi nếu không kiểm soát kịp.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard, xác nhận panel Cost vượt 2.5 USD và so sánh với Traffic để phân biệt do nhiều request hay do cost/request tăng.
  2. Kiểm tra panel Tokens để xem `tokens_in_total` hay `tokens_out_total` tăng bất thường.
  3. Mở Langfuse traces có cost/tokens cao, xem prompt metadata (`prompt_name`, `prompt_label`, `prompt_version`) và waterfall generation để xác định prompt/model nào gây tăng chi phí.
- Mitigation tạm thời: tắt incident `cost_spike` nếu đang bật, giới hạn `max_tokens`, rollback prompt label tạo output quá dài, hoặc tạm throttle traffic không quan trọng.
- Owner: `team-lead`

## Câu hỏi phản biện

Alert nên symptom-based vì người dùng và SLO chỉ quan tâm hệ thống có chậm, lỗi, tốn quá ngân sách hoặc giảm chất lượng hay không. Nếu alert gắn với tên hàm cụ thể, hệ thống có thể đổi implementation mà alert hỏng, hoặc báo động khi lỗi nội bộ chưa gây ảnh hưởng thật. Alert theo triệu chứng ổn định hơn, giảm nhiễu, và giúp on-call bắt đầu điều tra từ tác động thực tế rồi lần ngược bằng metrics, traces và logs.

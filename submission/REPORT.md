# Báo cáo Day 13 Observability - Group 2A

## 1. Thông tin nhóm

- Tên nhóm: K4-Group-2A
- Repository URL: https://github.com/ptdbrain/K4-Day13-2A202601138
- Commit SHA cuối: 04c93c0cf6edabe610e5bc696c00a4b5c27757c1
- Thành viên và vai trò: 
  - Phan Trọng Đạt - 2A202601138 (Leader - Structured Logging, PII Redaction, Correlation ID)
  - Bùi Thu Trang - 2A202601758 (Tracing Adapter, Langfuse SDK & Span Instrumentation)
  - Phạm Quốc Minh - 2A202601494 (Prompt Versioning, Fallback & Rollback Mechanism)
  - Nguyễn Thanh Hùng - 2A202601808 (Dashboard Specification, SLO & Incident Challenge Analysis)

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 (Đã kiểm tra 20+ log records, 0 missing fields, 0 PII leaks)
- Tổng số traces: 10+ traces (Được tạo qua `scripts/load_test.py`)
- Số PII leak còn lại: 0 (Che mờ email, số điện thoại Việt Nam, và số thẻ tín dụng)
- Link/đường dẫn dashboard: `config/dashboard.yaml` (Validator pass: 6/6 panels contract)

## 3. Logging và tracing

- Evidence correlation ID: `req-bd0b6c44` (định dạng `req-<8hex>` được truyền xuyên suốt qua middleware HTTP header `x-request-id` và structlog contextvars)
- Evidence PII redaction: `[REDACTED_EMAIL]`, `[REDACTED_PHONE_VN]`, `[REDACTED_CREDIT_CARD]` (Lưu trong `submission/evidence/cp1_evidence.txt`)
- Evidence trace waterfall: Xem các tệp ảnh screenshot tại:
  - `submission/evidence/cp2_langfuse_trace_list.png`
  - `submission/evidence/cp2_langfuse_waterfall.png`
- Giải thích một span đáng chú ý: 
  - Span `rag-retrieval` (as_type="retriever"): Thực hiện truy vấn danh sách tài liệu tham khảo liên quan đến câu hỏi. Trong quá trình điều tra incident `rag_slow`, span này ghi nhận độ trễ cố định 2.50s (`time.sleep(2.5)`), chiếm hơn 90% tổng thời gian thực thi của parent span `chat-response`.

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: `v1` (Label: `production`)
- Version/label candidate: `v2` (Label: `staging`)
- Trace ID của mỗi version:
  - Baseline v1 (`production`): `req-bd0b6c44`
  - Candidate v2 (`staging`): `req-dc33554d`
- Bằng chứng đổi label hoặc rollback:
  - Trong `app/prompt_management.py`, hệ thống tự động fetch prompt từ Langfuse theo label `production`. Khi phát hiện version candidate v2 hoạt động kém hiệu quả hoặc gây tăng latency/cost, thao tác rollback được thực hiện bằng cách cập nhật label `production` trên Langfuse dashboard chỉ định về version v1. Ứng dụng lập tức chuyển sang v1 mà không cần khởi động lại server. Nếu Langfuse offline/error, app dùng fallback local (`ResolvedPrompt` source `local-fallback`).

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel có trong dashboard contract.`
- Evidence dashboard: Được định nghĩa trong `config/dashboard.yaml` bao gồm 6 panel bắt buộc:
  1. `latency_p50_p95`: Phân bố độ trễ P50 và P95 (Ngưỡng cảnh báo: 2000ms).
  2. `request_rate`: Traffic theo phút.
  3. `error_rate`: Tỷ lệ lỗi % (SLO Target: < 1.0%).
  4. `token_usage`: Tổng số input và output tokens.
  5. `total_cost`: Chi phí ước tính tính theo USD (SLO Target: < $0.05/phút).
  6. `quality_score`: Điểm đánh giá chất lượng trung bình (Score range 0.0 - 1.0).
- SLO đã chọn và lý do:
  - Latency P95 <= 2000ms (Đảm bảo trải nghiệm phản hồi nhanh cho người dùng ứng dụng chatbot).
  - Availability Rate >= 99.0% (Đảm bảo hệ thống vận hành ổn định).
- Alert rules và runbook:
  - Chi tiết alert rules tại `config/alert_rules.yaml` và SLO tại `config/slo.yaml`.
  - Document hướng dẫn xử lý sự cố (Runbook) tại `docs/alerts.md`.

## 6. Điều tra challenge

- Challenge ID: day13-k4-observability-v1
- Triệu chứng từ metrics: Latency P95 tăng vọt lên 3473ms (vượt quá ngưỡng latency_threshold_ms: 2000ms), Traffic: 5 requests, Error rate: 0.0%, Total cost: $0.0104 USD. Thời gian phản hồi đo tại client kéo dài ~17.2s dưới áp lực 5 concurrent requests.
- Trace ID liên quan: req-c4762b07
- Log line/correlation ID liên quan: Correlation ID req-c4762b07. Log line: `{"service": "api", "latency_ms": 3473, "tokens_in": 34, "tokens_out": 138, "cost_usd": 0.002172, "quality_score": 0.9, "payload": {"answer_preview": "Starter answer. Teams should improve this output logic and add better quality ch..."}, "event": "response_sent", "model": "claude-sonnet-4-5", "correlation_id": "req-c4762b07", "session_id": "k4-challenge-s02", "user_id_hash": "cb22af258a5e", "feature": "monitoring", "env": "dev", "level": "info", "ts": "2026-08-11T08:12:50.502959Z"}`
- Root cause: Incident `rag_slow` kích hoạt (`STATE["rag_slow"] = True`). Trong `app/mock_rag.py` (hàm `retrieve`), mã nguồn gọi `time.sleep(2.5)` cố định cho mỗi lần truy vấn RAG retrieval (span `rag-retrieval`), khiến mọi request bị trễ thêm 2.5 giây.
- Fix action: 
  1. Tắt incident bằng `python scripts/inject_incident.py --scenario rag_slow --disable`.
  2. Trong môi trường production: Đánh index Vector Store, giảm top_k, đặt timeout limit (1.0s) cho RAG retrieval kèm fallback document.
- Preventive measure: 
  1. Cấu hình Alert Rule cảnh báo khi P95 latency của span `rag-retrieval` > 1500ms.
  2. Áp dụng Circuit Breaker & Timeout cho service RAG.
  3. Thêm caching layer (Redis / In-memory) cho các câu hỏi RAG phổ biến.

## 7. Đóng góp cá nhân

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Phan Trọng Đạt (2A202601138) | Cấu hình Structlog JSON logging, Correlation ID Middleware, Regex PII Redaction cho Email, Số điện thoại VN & Thẻ tín dụng | `aff4f19`, `c0edee5` | Hiểu sâu về luồng log enrichment, cách bảo vệ dữ liệu PII và truyền correlation ID qua microservices. |
| Bùi Thu Trang (2A202601758) | Tích hợp Tracing Adapter (Langfuse v3 SDK), instrument các decorator `@observe` cho spans (`rag-retrieval`, `llm-generation`, `chat-response`) | `4013676`, `c0edee5` | Nắm vững kỹ thuật distributed tracing, cách thiết lập context span hierarchy và ghi nhận metadata. |
| Phạm Quốc Minh (2A202601494) | Xây dựng Prompt Management module, quản lý prompt versioning (v1/v2), fallback local & cơ chế Rollback an toàn | `4013676`, `e38e659` | Thành thạo quy trình Quản lý vòng đời Prompt (Prompt Lifecycle), A/B testing prompt và zero-downtime rollback. |
| Nguyễn Thanh Hùng (2A202601808) | Cấu hình Dashboard specification (6 panels), định nghĩa SLO/Alert Rules & thực hiện điều tra incident Challenge theo quy trình 4 bước | `5ba6472`, `c0edee5` | Biết cách kết hợp Metrics - Traces - Logs để nhanh chóng khoanh vùng điểm nghẽn (bottleneck) và khắc phục sự cố. |

## 8. Kịch bản Demo (Demo Workflow: Metrics → Traces → Logs → Root Cause)

Khi thực hiện demo với Lab Coach / Hội đồng chấm bài, nhóm trình bày theo 4 bước sau:

1. **Bước 1: Quan sát Metrics (Metrics View)**
   - Mở màn hình Metrics / Dashboard (`http://localhost:8000/metrics` hoặc Grafana/Langfuse UI).
   - Chỉ ra chỉ số **P95 Latency** vượt ngưỡng SLO 2000ms (đạt 3473ms), trong khi Error Rate vẫn là 0.0%. Điều này xác nhận hệ thống bị nghẽn độ trễ (performance degradation) chứ không sập.

2. **Bước 2: Khoanh vùng bằng Distributed Tracing (Traces Waterfall)**
   - Mở màn hình Traces trên Langfuse UI (`submission/evidence/cp2_langfuse_waterfall.png`).
   - Chọn Trace ID bị ảnh hưởng (ví dụ: `req-c4762b07`).
   - Phân tích cây Waterfall: Parent span `chat-response` mất ~3.5s. Trong đó, child span `llm-generation` chỉ mất ~0.2s, nhưng child span `rag-retrieval` mất tới **2.50s**. Xác định điểm nghẽn thuộc về RAG Retrieval.

3. **Bước 3: Xác minh chi tiết bằng Structured Logs (Logs Analysis)**
   - Tra cứu Correlation ID `req-c4762b07` trong file log `data/logs.jsonl`.
   - Cho xem log record JSON đã được enrich đầy đủ metadata (`user_id_hash`, `session_id`, `feature`, `model`, `env`) và xác nhận PII đã được redact an toàn (`[REDACTED_...]`).
   - Kiểm tra timestamp và latency logged: `latency_ms: 3473` cho request tương ứng.

4. **Bước 4: Xác định Root Cause & Demo Khắc Phục (Root Cause & Resolution)**
   - Giải thích Root Cause: Incident `rag_slow` được kích hoạt, dẫn đến delay 2.5s cố định trong `mock_rag.py`.
   - Thực hiện lệnh khôi phục: `python scripts/inject_incident.py --scenario rag_slow --disable`.
   - Chạy lại load test: `python scripts/load_test.py`.
   - Cho thấy Metrics P95 Latency quay trở lại bình thường (< 200ms).

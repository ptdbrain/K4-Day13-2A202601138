# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: K4-Group-2A
- Repository URL: https://github.com/ptdbrain/K4-Day13-2A202601138
- Commit SHA cuối: e38e659673553a0e2b66a171157847ea6d4d332e
- Thành viên và vai trò: 
  - Phan Trọng Đạt - 2A202601138
  - Bùi Thu Trang - 2A202601758
  - Phạm Quốc Minh - 2A202601494
  - Nguyễn Thanh Hùng - 2A202601808

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 (CP1 Validation)
- Tổng số traces:
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard:


## 3. Logging và tracing

- Evidence correlation ID: `req-3000c6d3` (định dạng `req-<8hex>`)
- Evidence PII redaction: `[REDACTED_EMAIL]`, `[REDACTED_PHONE_VN]`, `[REDACTED_CREDIT_CARD]` (Lưu trong `submission/evidence/cp1_evidence.txt`)
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:


## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`:
- Evidence dashboard:
- SLO đã chọn và lý do:
- Alert rules và runbook:

## 6. Điều tra challenge

- Challenge ID: day13-k4-observability-v1
- Triệu chứng từ metrics: Latency P95 tăng vọt lên 3473ms (vượt quá ngưỡng latency_threshold_ms: 2000ms), Traffic: 5 requests, Error rate: 0.0%, Total cost: $0.0104 USD. Thời gian phản hồi đo tại client kéo dài ~17.2s dưới áp lực 5 concurrent requests.
- Trace ID liên quan: req-c4762b07
- Log line/correlation ID liên quan: Correlation ID req-c4762b07. Log line: `{"service": "api", "latency_ms": 3473, "tokens_in": 34, "tokens_out": 138, "cost_usd": 0.002172, "quality_score": 0.9, "payload": {"answer_preview": "Starter answer. Teams should improve this output logic and add better quality ch..."}, "event": "response_sent", "model": "claude-sonnet-4-5", "correlation_id": "req-c4762b07", "session_id": "k4-challenge-s02", "user_id_hash": "cb22af258a5e", "feature": "monitoring", "env": "dev", "level": "info", "ts": "2026-08-11T08:12:50.502959Z"}`
- Root cause: Incident rag_slow kích hoạt (STATE["rag_slow"] = True). Trong app/mock_rag.py (hàm retrieve), mã nguồn gọi time.sleep(2.5) cố định cho mỗi lần truy vấn RAG retrieval (span rag-retrieval), khiến mọi request bị trễ thêm 2.5 giây.
- Fix action: 1. Tắt incident bằng `python scripts/inject_incident.py --scenario rag_slow --disable`. 2. Trong production: Đánh index Vector Store, giảm top_k, đặt timeout limit (1.0s) cho RAG retrieval kèm fallback document.
- Preventive measure: 1. Cấu hình Alert Rule cảnh báo khi P95 latency của span rag-retrieval > 1500ms. 2. Áp dụng Circuit Breaker & Timeout cho service RAG. 3. Thêm caching layer (Redis / In-memory) cho các câu hỏi RAG phổ biến.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| | | | |

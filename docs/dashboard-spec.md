# Yêu cầu dashboard

Dashboard chính dùng dữ liệu runtime từ endpoint `/metrics` của API và contract kiểm tra bằng máy tại `config/dashboard.yaml`. Nếu dựng bằng Grafana, Streamlit hoặc dashboard nội bộ, các panel bên dưới phải giữ cùng tên, đơn vị, ngưỡng và khoảng thời gian mặc định.

- Công cụ sử dụng: dashboard spec theo `config/dashboard.yaml`; có thể hiện thực bằng Grafana/Streamlit/Langfuse dashboard tương đương.
- Khoảng thời gian mặc định: 60 phút gần nhất.
- Tự refresh: 30 giây.
- Evidence: lưu screenshot dashboard hoặc file spec đã hoàn thiện vào `submission/evidence/`.

| # | Nhóm | Panel | Nguồn dữ liệu | Đơn vị | Hiển thị | Threshold/SLO line |
|---|---|---|---|---|---|---|
| 1 | Latency | Latency percentiles | `/metrics`: `latency_p50`, `latency_p95`, `latency_p99` | ms | Line chart hoặc single value P50/P95/P99 | P95 <= 3000 ms |
| 2 | Traffic | Request traffic | `/metrics`: `traffic` | requests, requests/min | Counter tổng request và QPS/RPM gauge | RPM >= 1 trong lúc load test |
| 3 | Error | Error rate and breakdown | `/metrics`: `error_rate_pct`, `error_breakdown` | %, count | Single value error rate và bảng breakdown theo loại lỗi | Error rate <= 2% |
| 4 | Cost | Cost over time | `/metrics`: `total_cost_usd`, `avg_cost_usd` | USD | Tổng chi phí, chi phí trung bình/request, trend theo thời gian nếu có | Daily cost <= 2.5 USD |
| 5 | Tokens | Input and output tokens | `/metrics`: `tokens_in_total`, `tokens_out_total` | tokens | Two-value counter hoặc stacked bar input/output | Total tokens <= 50000 trong cửa sổ lab |
| 6 | Quality | Quality proxy | `/metrics`: `quality_avg` | score 0-1 | Single value hoặc line chart điểm trung bình | Quality avg >= 0.75 |

## Runtime query

Gọi dữ liệu hiện tại:

```bash
curl http://localhost:8000/metrics | python -m json.tool
```

Các trường bắt buộc từ `/metrics`:

- `latency_p50`, `latency_p95`, `latency_p99`
- `traffic`
- `error_rate_pct`, `error_breakdown`
- `total_cost_usd`, `avg_cost_usd`
- `tokens_in_total`, `tokens_out_total`
- `quality_avg`

## Kiểm tra contract

Trước khi chụp evidence, chạy:

```bash
python scripts/validate_dashboard.py
```

Kết quả hợp lệ cần báo có đủ `6/6 panel`. Screenshot dashboard phải nhìn được tên panel, time range 60 phút, đơn vị và threshold/SLO line.

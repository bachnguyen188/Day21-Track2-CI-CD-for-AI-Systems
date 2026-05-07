# BÁO CÁO KẾT QUẢ LAB MLOPS

**Họ và tên:** [Tên của bạn]
**MSSV:** [Mã số sinh viên]
**Repository:** [https://github.com/bachnguyen188/Day21-Track2-CI-CD-for-AI-Systems]

---

## 1. Phân tích thực nghiệm (Bước 1)
Dựa trên kết quả từ MLflow UI, tôi đã tiến hành 3 thí nghiệm chính với thuật toán RandomForest:
- **Lần 1:** `n_estimators=100`, `max_depth=10` -> Accuracy: 0.6440
- **Lần 2:** `n_estimators=200`, `max_depth=10` -> Accuracy: 0.6760
- **Lần 3:** `n_estimators=500`, `max_depth=100` -> Accuracy: 0.6820

**Kết luận:** Việc tăng độ sâu và số lượng cây giúp cải thiện mô hình nhưng vẫn chưa đạt ngưỡng 0.70 do giới hạn của lượng dữ liệu Phase 1.

## 2. Kết quả triển khai CI/CD (Bước 2 & 3)
- **Vượt ngưỡng Accuracy:** Để vượt mốc 0.70, tôi đã thực hiện Bước 3 (Continuous Training) bằng cách gộp thêm dữ liệu từ Phase 2. Kết quả Accuracy đã tăng vọt lên mức **> 0.75**, giúp vượt qua vòng Eval Gate thành công.
- **Serving:** Mô hình đã được triển khai thành công lên GCP VM (IP: 35.239.39.6) dưới dạng REST API bằng FastAPI và Uvicorn. Dịch vụ được quản lý tự động bởi `systemd`.

## 3. Khó khăn và cách giải quyết
- **Lỗi môi trường Python:** Gặp lỗi `MissingConfigException` của MLflow trên Windows. Cách giải quyết: Thiết lập `MLFLOW_TRACKING_URI` là database SQLite tạm thời khi chạy Test để đảm bảo tính độc lập.
- **Lỗi Deploy trên VM:** API ban đầu không khởi động được do thiếu thư viện `google-cloud-storage` trên máy ảo và lỗi đồng bộ thời gian tải mô hình. Cách giải quyết: Cài đặt đầy đủ thư viện trên VM và tăng thời gian `sleep` trong Pipeline lên 30s để server kịp tải model từ GCS.

## 4. Các tính năng Bonus đã thực hiện
- **Bonus 2:** Mở rộng code để hỗ trợ nhiều thuật toán (RandomForest & GradientBoosting).
- **Bonus 3:** Tự động tạo báo cáo `report.txt` sau mỗi lần huấn luyện.
- **Bonus 5:** Thêm cảnh báo lệch lạc dữ liệu (Data Drift) dựa trên phân phối nhãn.

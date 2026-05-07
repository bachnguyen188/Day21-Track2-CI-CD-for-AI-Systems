# Tổng Kết Lab MLOps - Tiến Độ Hiện Tại

## ✅ Đã Hoàn Thành

### Bước 1: Thực Nghiệm Cục Bộ và Theo Dõi Thí Nghiệm (100%)

**Files đã tạo:**
- ✅ `data/train_phase1.csv` (2998 mẫu)
- ✅ `data/eval.csv` (500 mẫu)
- ✅ `data/train_phase2.csv` (2998 mẫu)
- ✅ `src/train.py` (hoàn chỉnh, tất cả 12 TODOs)
- ✅ `params.yaml` (với siêu tham số tốt nhất)
- ✅ `outputs/metrics.json`
- ✅ `models/model.pkl`
- ✅ `mlflow.db` (MLflow tracking database)

**Kết quả thí nghiệm:**

| Lần | n_estimators | max_depth | min_samples_split | Accuracy | F1 Score |
|-----|--------------|-----------|-------------------|----------|----------|
| 1   | 100          | 5         | 2                 | 0.5640   | 0.5534   |
| 2   | 200          | 10        | 2                 | 0.6480   | 0.6464   |
| 3   | 150          | 15        | 5                 | **0.6760** | **0.6744** |

**Bộ siêu tham số tốt nhất:** n_estimators=150, max_depth=15, min_samples_split=5

---

### Bước 2: CI/CD Pipeline (Code hoàn thành 100%, cần GCP setup)

**Files đã tạo:**

1. ✅ **src/serve.py** (hoàn chỉnh)
   - Download model từ GCS khi khởi động
   - Endpoint `/health` để health check
   - Endpoint `/predict` để inference
   - Validation 12 features
   - Label mapping (0→thấp, 1→trung_bình, 2→cao)

2. ✅ **tests/test_train.py** (hoàn chỉnh, 3/3 tests pass)
   - `test_train_returns_float()` - kiểm tra hàm train trả về float [0,1]
   - `test_metrics_file_created()` - kiểm tra file metrics.json
   - `test_model_file_created()` - kiểm tra file model.pkl

3. ✅ **.github/workflows/mlops.yml** (hoàn chỉnh)
   - **Job 1: Test** - chạy unit tests
   - **Job 2: Train** - huấn luyện model, upload lên GCS
   - **Job 3: Eval** - kiểm tra accuracy >= 0.70
   - **Job 4: Deploy** - restart service trên VM, health check

4. ✅ **GCP_SETUP_GUIDE.md** - hướng dẫn chi tiết từng bước

**Cấu trúc thư mục hiện tại:**
```
Lab21/
├── .github/
│   └── workflows/
│       └── mlops.yml          ✅ CI/CD pipeline
├── .dvc/
│   └── .gitignore             ✅ DVC config
├── data/
│   ├── train_phase1.csv       ✅ (2998 mẫu)
│   ├── eval.csv               ✅ (500 mẫu)
│   └── train_phase2.csv       ✅ (2998 mẫu)
├── src/
│   ├── __init__.py            ✅
│   ├── train.py               ✅ Hoàn chỉnh
│   └── serve.py               ✅ Hoàn chỉnh
├── tests/
│   ├── __init__.py            ✅
│   └── test_train.py          ✅ Hoàn chỉnh (3/3 pass)
├── models/
│   └── model.pkl              ✅
├── outputs/
│   └── metrics.json           ✅
├── mlartifacts/               ✅ MLflow artifacts
├── mlflow.db                  ✅ MLflow tracking
├── params.yaml                ✅ Best hyperparameters
├── requirements.txt           ✅
├── .gitignore                 ✅
├── generate_data.py           ✅
├── add_new_data.py            ✅
├── GCP_SETUP_GUIDE.md         ✅ Hướng dẫn setup GCP
└── README.md                  ✅
```

---

## 🔄 Cần Thực Hiện (Yêu Cầu GCP Account)

### Checklist Bước 2 - GCP Setup

Làm theo hướng dẫn trong file `GCP_SETUP_GUIDE.md`:

- [ ] **2.1** Tạo GCS bucket
- [ ] **2.2** Tạo Service Account và tải `sa-key.json`
- [ ] **2.3** Cấu hình DVC với GCS remote
  - [ ] `dvc init`
  - [ ] `dvc remote add -d myremote gs://$BUCKET/dvc`
  - [ ] `dvc add data/*.csv`
  - [ ] `dvc push`
- [ ] **2.4** Tạo VM trên GCP và lấy IP công khai
- [ ] **2.5** Cấu hình VM (cài Python, thư viện)
- [ ] **2.6** Copy `sa-key.json` và `serve.py` lên VM
- [ ] **2.7** Tạo systemd service trên VM
- [ ] **2.8** Tạo SSH key cho GitHub Actions
- [ ] **2.9** Thêm 5 GitHub Secrets:
  - [ ] `CLOUD_CREDENTIALS`
  - [ ] `CLOUD_BUCKET`
  - [ ] `VM_HOST`
  - [ ] `VM_USER`
  - [ ] `VM_SSH_KEY`
- [ ] **2.12** Push code lên GitHub và xem pipeline chạy
- [ ] **2.12** Start service trên VM: `sudo systemctl start mlops-serve`
- [ ] **2.12** Test endpoints:
  - [ ] `curl http://VM_IP:8000/health`
  - [ ] `curl http://VM_IP:8000/predict`

---

## 📋 Bước 3: Huấn Luyện Liên Tục (Chưa bắt đầu)

Sau khi hoàn thành Bước 2, bạn sẽ:

1. Chạy `python add_new_data.py` để thêm dữ liệu mới
2. Cập nhật DVC: `dvc add data/train_phase1.csv`
3. Commit và push: `git add data/train_phase1.csv.dvc && git commit -m "data: add new data"`
4. Push dữ liệu: `dvc push`
5. Push git: `git push origin main`
6. Pipeline tự động chạy lại và deploy model mới

---

## 🎯 Mục Tiêu Cuối Cùng

Khi hoàn thành cả 3 bước, bạn sẽ có:

1. ✅ **Bước 1:** Quy trình thực nghiệm có tổ chức với MLflow
2. 🔄 **Bước 2:** CI/CD pipeline tự động (code sẵn sàng, cần GCP setup)
3. ⏳ **Bước 3:** Huấn luyện liên tục khi có dữ liệu mới

**Hệ thống MLOps hoàn chỉnh:**
- Theo dõi thí nghiệm với MLflow
- Quản lý phiên bản dữ liệu với DVC
- CI/CD tự động với GitHub Actions
- Eval gate đảm bảo chất lượng (accuracy >= 0.70)
- REST API serving trên cloud VM
- Tự động huấn luyện lại khi có dữ liệu mới

---

## 📚 Tài Liệu Tham Khảo

- **GCP_SETUP_GUIDE.md** - Hướng dẫn chi tiết setup GCP từng bước
- **tasks/buoc-1.md** - Hướng dẫn Bước 1 (đã hoàn thành)
- **tasks/buoc-2.md** - Hướng dẫn Bước 2 (code hoàn thành, cần GCP)
- **tasks/buoc-3.md** - Hướng dẫn Bước 3 (chưa bắt đầu)
- **README.md** - Tổng quan lab

---

## 🚀 Bước Tiếp Theo

1. **Nếu bạn có GCP account:**
   - Mở file `GCP_SETUP_GUIDE.md`
   - Làm theo từng bước trong checklist
   - Chạy pipeline lần đầu tiên

2. **Nếu chưa có GCP account:**
   - Đăng ký GCP free trial ($300 credit)
   - Cài đặt Google Cloud SDK
   - Quay lại làm theo `GCP_SETUP_GUIDE.md`

3. **Để xem MLflow UI (local):**
   ```bash
   mlflow ui --backend-store-uri sqlite:///mlflow.db
   ```
   Truy cập: http://localhost:5000

---

## 💡 Lưu Ý Quan Trọng

- ⚠️ **KHÔNG commit** `sa-key.json` vào git (đã có trong .gitignore)
- ⚠️ **KHÔNG commit** các file CSV vào git (chỉ commit file .dvc)
- ✅ Model phải đạt accuracy >= 0.70 mới được deploy
- ✅ Pipeline tự động chạy khi:
  - Push thay đổi vào `src/*.py`
  - Push thay đổi vào `params.yaml`
  - Push thay đổi vào `data/*.dvc` (dữ liệu mới)

---

## 📊 Tiến Độ Tổng Thể

```
Bước 1: ████████████████████ 100% ✅
Bước 2: ████████████░░░░░░░░  60% 🔄 (code 100%, cần GCP setup)
Bước 3: ░░░░░░░░░░░░░░░░░░░░   0% ⏳
```

**Tổng tiến độ:** ~53% hoàn thành

---

Bạn đã sẵn sàng để setup GCP chưa? Nếu có câu hỏi gì về các bước tiếp theo, hãy hỏi tôi!

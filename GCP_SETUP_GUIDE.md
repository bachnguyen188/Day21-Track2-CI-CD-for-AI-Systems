# Hướng Dẫn Thiết Lập GCP cho Lab MLOps

## Yêu Cầu Trước Khi Bắt Đầu

- Tài khoản GCP (có thể dùng free trial $300)
- Google Cloud SDK đã cài đặt (`gcloud` CLI)
- Đã đăng nhập: `gcloud auth login`

---

## Bước 2.1: Tạo GCS Bucket

```bash
# Đặt biến môi trường
export PROJECT=<YOUR_GCP_PROJECT_ID>
export BUCKET=<YOUR_UNIQUE_BUCKET_NAME>

# Tạo bucket
gsutil mb -p $PROJECT -l us-central1 gs://$BUCKET

# Kích hoạt Cloud Storage API
gcloud services enable storage.googleapis.com --project $PROJECT
```

**Lưu ý:** Tên bucket phải là duy nhất trên toàn bộ GCP. Gợi ý: `mlops-lab-<your-name>-<random-number>`

---

## Bước 2.2: Tạo Service Account và Credentials

```bash
# Tạo service account
gcloud iam service-accounts create mlops-lab-sa \
  --display-name "MLOps Lab SA" \
  --project $PROJECT

# Cấp quyền objectAdmin chỉ trên bucket
gsutil iam ch \
  serviceAccount:mlops-lab-sa@$PROJECT.iam.gserviceaccount.com:roles/storage.objectAdmin \
  gs://$BUCKET

# Xuất file key JSON
gcloud iam service-accounts keys create sa-key.json \
  --iam-account mlops-lab-sa@$PROJECT.iam.gserviceaccount.com
```

**Quan trọng:** File `sa-key.json` đã có trong `.gitignore`, tuyệt đối không commit vào git!

---

## Bước 2.3: Cài Đặt DVC và Cấu Hình GCS Remote

```bash
# Khởi tạo DVC
dvc init

# Trỏ DVC đến GCS
dvc remote add -d myremote gs://$BUCKET/dvc

# Cấu hình credentials
dvc remote modify myremote credentialpath sa-key.json

# Theo dõi các file dữ liệu bằng DVC
dvc add data/train_phase1.csv
dvc add data/eval.csv
dvc add data/train_phase2.csv

# Commit các file con trỏ DVC vào git (KHÔNG phải file CSV)
git add data/train_phase1.csv.dvc data/eval.csv.dvc data/train_phase2.csv.dvc \
        .gitignore .dvc/config
git commit -m "feat: track datasets with DVC"

# Đẩy các file CSV lên GCS
dvc push
```

**Xác nhận:** Vào GCS Console và kiểm tra các file đã xuất hiện dưới prefix `dvc/`

---

## Bước 2.4: Tạo VM Trên GCP

```bash
# Tạo VM
gcloud compute instances create mlops-serve \
  --zone=us-central1-a \
  --machine-type=e2-small \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --tags=mlops-serve \
  --project $PROJECT

# Mở cổng 8000 cho inference API
gcloud compute firewall-rules create allow-mlops-serve \
  --allow=tcp:8000 \
  --target-tags=mlops-serve \
  --project $PROJECT

# Lấy IP công khai của VM (lưu lại để dùng cho GitHub Secrets)
gcloud compute instances describe mlops-serve \
  --zone=us-central1-a \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

**Lưu IP này lại!** Bạn sẽ cần nó cho GitHub Secret `VM_HOST`

---

## Bước 2.5: Cấu Hình VM

### SSH vào VM:

```bash
gcloud compute ssh mlops-serve --zone=us-central1-a
```

### Bên trong VM, chạy các lệnh sau:

```bash
# Cài đặt Python và các thư viện
sudo apt update && sudo apt install -y python3-pip
pip3 install fastapi uvicorn scikit-learn joblib google-cloud-storage

# Tạo thư mục
mkdir -p ~/models ~/src

# Thoát khỏi VM
exit
```

### Copy file key lên VM:

```bash
gcloud compute scp sa-key.json mlops-serve:~/sa-key.json \
  --zone=us-central1-a
```

### Copy file serve.py lên VM:

```bash
gcloud compute scp src/serve.py mlops-serve:~/src/serve.py \
  --zone=us-central1-a
```

---

## Bước 2.7: Cấu Hình Systemd Service Trên VM

### SSH lại vào VM:

```bash
gcloud compute ssh mlops-serve --zone=us-central1-a
```

### Tạo systemd service:

```bash
sudo tee /etc/systemd/system/mlops-serve.service > /dev/null <<EOF
[Unit]
Description=MLOps Model Inference Server
After=network.target

[Service]
User=$USER
WorkingDirectory=/home/$USER
Environment="GCS_BUCKET=<YOUR_BUCKET_NAME>"
Environment="GOOGLE_APPLICATION_CREDENTIALS=/home/$USER/sa-key.json"
ExecStart=/usr/bin/python3 /home/$USER/src/serve.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Thay <YOUR_BUCKET_NAME> bằng tên bucket thực của bạn
# Ví dụ: sed -i 's/<YOUR_BUCKET_NAME>/mlops-lab-yourname-123/g' /etc/systemd/system/mlops-serve.service

sudo systemctl daemon-reload
sudo systemctl enable mlops-serve
```

**Lưu ý:** Chưa start service ngay. Model chưa có trên GCS cho đến khi pipeline CI/CD chạy lần đầu.

---

## Bước 2.8: Tạo SSH Key Cho GitHub Actions

### Trên máy tính cá nhân (không phải VM):

```bash
# Tạo SSH key
ssh-keygen -t ed25519 -f ~/.ssh/mlops_deploy -N "" -C "github-actions-deploy"

# Thêm public key vào VM
gcloud compute ssh mlops-serve --zone=us-central1-a \
  --command "echo '$(cat ~/.ssh/mlops_deploy.pub)' >> ~/.ssh/authorized_keys"
```

---

## Bước 2.9: Thêm GitHub Secrets

Vào repo GitHub: **Settings > Secrets and variables > Actions > New repository secret**

Thêm chính xác 5 secrets sau:

| Tên Secret | Giá Trị | Cách Lấy |
|------------|---------|----------|
| `CLOUD_CREDENTIALS` | Toàn bộ nội dung file `sa-key.json` | `cat sa-key.json` |
| `CLOUD_BUCKET` | Tên bucket (ví dụ: `mlops-lab-yourname-123`) | Biến `$BUCKET` ở trên |
| `VM_HOST` | IP công khai của VM | Từ bước 2.4 |
| `VM_USER` | Username trên VM | Chạy `echo $USER` trong SSH session trên VM |
| `VM_SSH_KEY` | Toàn bộ nội dung private key | `cat ~/.ssh/mlops_deploy` |

**Quan trọng:** 
- `CLOUD_CREDENTIALS` phải là JSON hợp lệ (bắt đầu bằng `{` và kết thúc bằng `}`)
- `VM_SSH_KEY` phải bắt đầu bằng `-----BEGIN OPENSSH PRIVATE KEY-----`

---

## Bước 2.12: Chạy Pipeline Lần Đầu Tiên

### Tạo file __init__.py nếu chưa có:

```bash
touch src/__init__.py tests/__init__.py
```

### Push tất cả lên GitHub:

```bash
git add .
git commit -m "feat: add CI/CD pipeline, tests, and serving API"
git push origin main
```

### Theo dõi pipeline:

1. Vào tab **Actions** trên repo GitHub
2. Xem pipeline chạy qua 4 jobs: Test → Train → Eval → Deploy
3. Nếu có lỗi, xem logs để debug

### Sau khi pipeline hoàn thành, khởi động service trên VM:

```bash
gcloud compute ssh mlops-serve --zone=us-central1-a \
  --command "sudo systemctl start mlops-serve"
```

### Kiểm tra service:

```bash
VM_IP=<YOUR_VM_IP>

# Kiểm tra health
curl http://$VM_IP:8000/health

# Dự đoán
curl -X POST http://$VM_IP:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [7.4, 0.70, 0.00, 1.9, 0.076, 11.0, 34.0, 0.9978, 3.51, 0.56, 9.4, 0]}'
```

Kết quả mong đợi:
```json
{"prediction": 0, "label": "thap"}
```

---

## Xử Lý Sự Cố

### `dvc push` thất bại với lỗi xác thực

```bash
# Kiểm tra config
cat .dvc/config

# Nếu thiếu credentialpath, thêm lại
dvc remote modify myremote credentialpath sa-key.json
```

### GitHub Actions `dvc pull` thất bại

- Kiểm tra secret `CLOUD_CREDENTIALS` có phải JSON hợp lệ không
- Mở secret trong GitHub Settings và xác nhận nội dung

### Service trên VM không khởi động

```bash
# Xem log
sudo journalctl -u mlops-serve -n 50

# Nguyên nhân phổ biến:
# - Biến GCS_BUCKET sai trong file service
# - sa-key.json chưa được copy lên VM
# - Model chưa tồn tại trên GCS (chạy pipeline trước)
```

### Job Deploy thất bại

- Kiểm tra accuracy có >= 0.70 không (xem log job Train)
- Kiểm tra SSH key đã được thêm vào VM chưa
- Kiểm tra VM_HOST, VM_USER, VM_SSH_KEY trong GitHub Secrets

---

## Checklist Hoàn Thành Bước 2

- [ ] GCS bucket đã được tạo
- [ ] Service account và sa-key.json đã được tạo
- [ ] DVC đã được cấu hình và `dvc push` thành công
- [ ] VM đã được tạo và cấu hình
- [ ] Systemd service đã được tạo trên VM
- [ ] SSH key đã được tạo và thêm vào VM
- [ ] 5 GitHub Secrets đã được thêm
- [ ] Pipeline chạy thành công (4 jobs màu xanh)
- [ ] `curl http://VM_IP:8000/health` trả về `{"status": "ok"}`
- [ ] `curl http://VM_IP:8000/predict` trả về kết quả dự đoán

---

## Tiếp Theo: Bước 3

Sau khi hoàn thành Bước 2, bạn có thể chuyển sang Bước 3 để thêm dữ liệu mới và xem pipeline tự động chạy lại.

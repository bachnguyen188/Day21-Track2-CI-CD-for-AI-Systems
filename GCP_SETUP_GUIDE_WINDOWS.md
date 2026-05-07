# Hướng Dẫn Thiết Lập GCP cho Lab MLOps (Bản chuẩn cho Windows - CMD)

## Yêu Cầu Trước Khi Bắt Đầu

- Tài khoản GCP (Project ID của bạn là: `k109-494403`)
- Google Cloud SDK đã cài đặt (`gcloud` CLI)
- Đã đăng nhập: `gcloud auth login`

---

## Bước 2.1: Thiết lập Biến và Tạo Bucket

```cmd
:: 1. Đặt biến môi trường (Lưu ý: Không được có khoảng trắng quanh dấu =)
set PROJECT=k109-494403
set BUCKET=mlops-lab-bach-unique-id

:: 2. Tạo bucket
gsutil mb -p %PROJECT% -l us-central1 gs://%BUCKET%

:: 3. Kích hoạt Cloud Storage API
gcloud services enable storage.googleapis.com --project %PROJECT%
```

---

## Bước 2.2: Tạo Service Account và Credentials

```cmd
:: 1. Tạo service account
gcloud iam service-accounts create mlops-lab-sa ^
  --display-name "MLOps Lab SA" ^
  --project %PROJECT%

:: 2. Cấp quyền objectAdmin
gsutil iam ch ^
  serviceAccount:mlops-lab-sa@%PROJECT%.iam.gserviceaccount.com:roles/storage.objectAdmin ^
  gs://%BUCKET%

:: 3. Xuất file key JSON
gcloud iam service-accounts keys create sa-key.json ^
  --iam-account mlops-lab-sa@%PROJECT%.iam.gserviceaccount.com
```

---

## Bước 2.3: Cài Đặt DVC và Cấu Hình GCS Remote

```cmd
:: 1. Cài đặt thư viện hỗ trợ (Nếu chưa cài)
pip install dvc dvc-gs gcsfs

:: 2. Thiết lập xác thực cho DVC (Dùng biến môi trường để tránh lỗi 'unhashable type')
set GOOGLE_APPLICATION_CREDENTIALS=sa-key.json

:: 3. Khởi tạo và cấu hình DVC
dvc init -f
dvc remote add -d myremote gs://%BUCKET%/dvc
dvc remote modify myremote --unset credentialpath

:: 4. Thêm dữ liệu và đẩy lên Cloud
dvc add data/train_phase1.csv
dvc add data/eval.csv
dvc add data/train_phase2.csv

:: 5. Commit vào git
git add data/*.dvc .gitignore .dvc/config
git commit -m "feat: track datasets with DVC"

:: 6. Đẩy dữ liệu
dvc push
```

---

## Bước 2.4: Tạo VM Trên GCP

```cmd
:: 1. Kích hoạt Compute Engine API (Bắt buộc phải làm trước khi tạo VM)
gcloud services enable compute.googleapis.com --project %PROJECT%

:: 2. Tạo VM
gcloud compute instances create mlops-serve ^
  --zone=us-central1-a ^
  --machine-type=e2-small ^
  --image-family=ubuntu-2204-lts ^
  --image-project=ubuntu-os-cloud ^
  --tags=mlops-serve ^
  --project %PROJECT%

:: 3. Mở cổng 8000
gcloud compute firewall-rules create allow-mlops-serve ^
  --allow=tcp:8000 ^
  --target-tags=mlops-serve ^
  --project %PROJECT%

:: 4. Lấy IP công khai của VM (Lưu lại số này!)
gcloud compute instances describe mlops-serve ^
  --zone=us-central1-a ^
  --format="get(networkInterfaces[0].accessConfigs[0].natIP)"
```

---

## Bước 2.5: Cấu Hình VM (Copy file)

```cmd
:: Copy file key lên VM
gcloud compute scp sa-key.json mlops-serve:sa-key.json --zone=us-central1-a

:: Tạo folder src trên VM và copy code
gcloud compute ssh mlops-serve --zone=us-central1-a --command "mkdir -p ~/src"
gcloud compute scp src/serve.py mlops-serve:src/serve.py --zone=us-central1-a
```

---

## Bước 2.8: Tạo SSH Key Cho GitHub Actions

```cmd
:: 1. Tạo thư mục .ssh nếu chưa có
if not exist "%USERPROFILE%\.ssh" mkdir "%USERPROFILE%\.ssh"

:: 2. Tạo SSH key (Nhấn Enter cho các câu hỏi)
ssh-keygen -t ed25519 -f "%USERPROFILE%\.ssh\mlops_deploy" -N "" -C "github-actions-deploy"

:: 3. Thêm public key vào VM (Dùng lệnh này để tránh lỗi ký tự)
for /f "delims=" %i in ('type "%USERPROFILE%\.ssh\mlops_deploy.pub"') do set PUB_KEY=%i
gcloud compute ssh mlops-serve --zone=us-central1-a --command "echo %PUB_KEY% >> ~/.ssh/authorized_keys"
```

---

## Bước 2.9: Thêm GitHub Secrets

Dùng các lệnh sau để lấy giá trị copy vào GitHub:

| Tên Secret | Lệnh CMD để lấy giá trị |
|------------|-------------------------|
| `CLOUD_CREDENTIALS` | `type sa-key.json` |
| `CLOUD_BUCKET` | `echo %BUCKET%` |
| `VM_HOST` | (IP lấy từ bước 2.4) |
| `VM_USER` | `echo %USERNAME%` |
| `VM_SSH_KEY` | `type "%USERPROFILE%\.ssh\mlops_deploy"` |

---

## Bước 2.12: Chạy Pipeline Lần Đầu

```cmd
:: Tạo file __init__.py trống
type nul > src\__init__.py
type nul > tests\__init__.py

:: Push lên GitHub
git add .
git commit -m "feat: add CI/CD pipeline, tests, and serving API"
git push origin main
```

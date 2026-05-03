# 🏠 HouseSellWeb Backend - Hướng dẫn cài đặt & chạy dự án

## Yêu cầu hệ thống
- Python >= 3.10
- MySQL >= 8.0 (đang chạy)
- pip hoặc venv

---

## Bước 1: Di chuyển vào thư mục Backend

```bash
cd d:\PythonWeb\HouseSellWeb\Be
```

---

## Bước 2: Tạo môi trường ảo (Virtual Environment)

```bash
# Tạo môi trường ảo tên là "venv"
python -m venv venv
```

### Kích hoạt môi trường ảo

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

> Sau khi kích hoạt, terminal sẽ hiển thị `(venv)` ở đầu dòng.

---

## Bước 3: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### Danh sách thư viện sẽ được cài:
| Thư viện | Mục đích |
|---|---|
| Django | Framework web chính |
| djangorestframework | Xây dựng REST API |
| djangorestframework-simplejwt | Xác thực JWT |
| django-cors-headers | Xử lý CORS (FE gọi BE) |
| drf-yasg | Swagger UI / Redoc docs |
| Pillow | Xử lý ảnh |
| PyMySQL | Kết nối MySQL |
| django-filter | Lọc dữ liệu API |
| scikit-learn | ML / gợi ý BĐS |
| numpy | Tính toán số |
| pandas | Xử lý dữ liệu |
| python-decouple | Quản lý biến môi trường (.env) |

---

## Bước 4: Tạo database MySQL

Mở MySQL Workbench hoặc dùng CLI:

```sql
CREATE DATABASE housesell_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## Bước 5: Cấu hình biến môi trường (tùy chọn)

Tạo file `.env` trong thư mục `Be/`:

```env
SECRET_KEY=django-insecure-your-secret-key-here
DEBUG=True
DB_NAME=housesell_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

> Nếu dùng `.env`, cần cập nhật `settings.py` để đọc từ `decouple`.
> Nếu chưa dùng, chỉnh `PASSWORD` trực tiếp trong `core/settings.py` dòng 84.

---

## Bước 6: Kích hoạt PyMySQL (bắt buộc với MySQL)

Mở file `Be/core/__init__.py`, thêm vào:

```python
import pymysql
pymysql.install_as_MySQLdb()
```

---

## Bước 7: Chạy Migrations (tạo bảng trong DB)

```bash
# Tạo file migration từ các model
python manage.py makemigrations

# Áp dụng migration lên database
python manage.py migrate
```

---

## Bước 8: Tạo tài khoản Admin (Super User)

```bash
python manage.py createsuperuser
```

Nhập thông tin:
```
Username: admin
Email: admin@example.com
Password: ****
Password (again): ****
```

---

## Bước 9: Thu thập Static Files (dùng cho production)

```bash
python manage.py collectstatic
```

> Bước này không bắt buộc khi dev local.

---

## Bước 10: Chạy Server

```bash
python manage.py runserver
```

Mặc định chạy tại: **http://127.0.0.1:8000**

Chạy với port khác:
```bash
python manage.py runserver 8080
```

---

## Các đường dẫn quan trọng

| URL | Mô tả |
|---|---|
| http://127.0.0.1:8000/admin/ | Trang quản trị Django |
| http://127.0.0.1:8000/swagger/ | Swagger UI - xem/test API |
| http://127.0.0.1:8000/redoc/ | Redoc - tài liệu API |
| http://127.0.0.1:8000/swagger.json | Swagger JSON spec |

---

## Tóm tắt - Chạy nhanh (lần đầu)

```bash
cd d:\PythonWeb\HouseSellWeb\Be
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Tạo DB MySQL: housesell_db

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Tóm tắt - Chạy lại (từ lần 2 trở đi)

```bash
cd d:\PythonWeb\HouseSellWeb\Be
venv\Scripts\activate
python manage.py runserver
```

---

## Lỗi thường gặp

### ❌ `django.db.utils.OperationalError: (1045, "Access denied for user 'root'@'localhost'")`
→ Sai mật khẩu MySQL. Kiểm tra lại `PASSWORD` trong `settings.py`.

### ❌ `ModuleNotFoundError: No module named 'MySQLdb'`
→ Chưa thêm PyMySQL vào `__init__.py`. Xem Bước 6.

### ❌ `django.core.exceptions.ImproperlyConfigured: ...`
→ Kiểm tra `INSTALLED_APPS` và `settings.py`.

### ❌ `No module named 'venv'`
→ Dùng: `python -m pip install virtualenv` rồi `virtualenv venv`.

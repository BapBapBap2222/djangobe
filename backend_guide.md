# 🏠 Hướng Dẫn Làm Backend Django REST cho HousePriceWeb

> **Dành cho:** Người mới bắt đầu làm Backend, chưa biết Django  
> **Mục tiêu:** Xây dựng API để frontend React (Vite + TypeScript) gọi đến  
> **Tech stack:** Django 4.2 · Django REST Framework · MySQL · JWT · Swagger

---

## 📖 Mục Lục

1. [Hiểu cơ bản: Backend là gì, API là gì?](#1-hiểu-cơ-bản)
2. [Cấu trúc dự án hiện tại](#2-cấu-trúc-dự-án)
3. [Checklist công việc cần làm](#3-checklist-công-việc)
4. [Danh sách API cần xây dựng](#4-danh-sách-api)
5. [Hướng dẫn từng bước](#5-hướng-dẫn-từng-bước)
6. [Kết nối Frontend ↔ Backend](#6-kết-nối-frontend)
7. [Kiểm thử API với Swagger](#7-swagger)
8. [Lỗi thường gặp và cách sửa](#8-lỗi-thường-gặp)

---

## 1. Hiểu Cơ Bản

### 🤔 Backend là gì?

Hãy tưởng tượng một nhà hàng:
- **Frontend** = Bàn ăn, menu, giao diện cho khách (React/Vite - đã có rồi)
- **Backend** = Nhà bếp, nấu ăn và phục vụ món ra
- **Database (MySQL)** = Kho lưu trữ nguyên liệu
- **API** = Người phục vụ đưa món từ bếp ra bàn

```
Người dùng click nút "Xem nhà" trên web (FE)
    → FE gửi yêu cầu đến API: GET /api/properties/
    → Backend xử lý, lấy dữ liệu từ MySQL
    → Backend trả về JSON
    → FE hiển thị lên màn hình
```

### 🔑 Các khái niệm cần nhớ

| Khái niệm | Giải thích đơn giản |
|-----------|---------------------|
| **Model** | Bản thiết kế cho 1 bảng trong database |
| **Serializer** | Công cụ chuyển đổi dữ liệu Python ↔ JSON |
| **View** | Nơi xử lý logic của 1 API endpoint |
| **URL** | Địa chỉ để FE gọi API (vd: `/api/properties/`) |
| **JWT Token** | Chìa khoá để xác nhận người dùng đã đăng nhập |
| **CORS** | Cho phép FE (localhost:5173) gọi BE (localhost:8000) |

### 📦 HTTP Methods

```
GET    → Lấy dữ liệu     (đọc danh sách nhà)
POST   → Tạo mới         (đăng nhà mới)
PUT    → Cập nhật toàn bộ (sửa thông tin nhà)
PATCH  → Cập nhật 1 phần (chỉ sửa giá)
DELETE → Xóa             (xóa nhà)
```

---

## 2. Cấu Trúc Dự Án

```
HousePriceWeb/
├── FE/                        ← Frontend React (đã có, đang chạy port 5173)
│   └── src/
│       ├── pages/             ← Các trang: Login, Listings, PropertyDetail...
│       └── hooks/             ← Nơi sẽ gọi API từ FE
│
├── Be/                        ← Backend Django (bạn sẽ làm ở đây)
│   ├── core/                  ← Project config chính
│   │   ├── settings.py        ← Cấu hình toàn dự án
│   │   └── urls.py            ← URL gốc (đã có Swagger)
│   ├── manage.py              ← Lệnh quản lý Django
│   └── requirements.txt       ← Danh sách thư viện
│
└── LinearRegressionModel/     ← Model AI dự đoán giá nhà
```

### Cấu trúc BE sau khi hoàn thiện

```
Be/
├── core/
│   ├── settings.py
│   └── urls.py
├── accounts/           ← App quản lý tài khoản người dùng
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── properties/         ← App quản lý bất động sản
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── appointments/       ← App quản lý lịch xem nhà
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── news/               ← App quản lý tin tức
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── predictions/        ← App dự đoán giá nhà (AI)
│   ├── views.py
│   └── urls.py
├── manage.py
└── requirements.txt
```

---

## 3. Checklist Công Việc

### Giai đoạn 1: Setup môi trường ⚙️

- [ ] Cài MySQL và tạo database `housesell_db`
- [ ] Kích hoạt virtual environment
- [ ] Cài thư viện từ [requirements.txt](file:///c:/Users/minht/OneDrive/Desktop/HousePriceWeb/Be/requirements.txt)
- [ ] Kiểm tra cài `corsheaders` (nếu chưa có)
- [ ] Chạy `python manage.py migrate` lần đầu

### Giai đoạn 2: App Accounts (Tài khoản) 👤

- [ ] Tạo app: `python manage.py startapp accounts`
- [ ] Thêm `accounts` vào `INSTALLED_APPS`
- [ ] Tạo model `UserProfile` (mở rộng từ User của Django)
- [ ] Viết serializer: `RegisterSerializer`, `LoginSerializer`, `UserProfileSerializer`
- [ ] Viết views: Register, Login, Refresh Token, Get/Update Profile, Change Password
- [ ] Khai báo URL trong `accounts/urls.py`
- [ ] Include vào [core/urls.py](file:///c:/Users/minht/OneDrive/Desktop/HousePriceWeb/Be/core/urls.py)
- [ ] Chạy `makemigrations` và `migrate`
- [ ] Test trên Swagger

### Giai đoạn 3: App Properties (Bất động sản) 🏠

- [ ] Tạo app: `python manage.py startapp properties`
- [ ] Thêm `properties` vào `INSTALLED_APPS`
- [ ] Tạo models: `Property`, `PropertyImage`, `PropertyFavorite`
- [ ] Viết serializers
- [ ] Viết views: List, Detail, Create, Update, Delete, Search, Filter
- [ ] Khai báo URLs
- [ ] Migrate và test

### Giai đoạn 4: App Appointments (Lịch hẹn) 📅

- [ ] Tạo app: `python manage.py startapp appointments`
- [ ] Tạo model `Appointment`
- [ ] Viết serializers và views
- [ ] Khai báo URLs, migrate, test

### Giai đoạn 5: App News (Tin tức) 📰

- [ ] Tạo app: `python manage.py startapp news`
- [ ] Tạo model `News`
- [ ] Viết serializers và views
- [ ] Khai báo URLs, migrate, test

### Giai đoạn 6: Tính năng AI dự đoán giá 🤖

- [ ] Tạo app: `python manage.py startapp predictions`
- [ ] Load model LinearRegression từ `LinearRegressionModel/`
- [ ] Viết view nhận input → dự đoán → trả về giá
- [ ] Khai báo URL và test

### Giai đoạn 7: Cấu hình CORS & kết nối FE 🔗

- [ ] Cài `django-cors-headers`
- [ ] Cấu hình CORS trong [settings.py](file:///c:/Users/minht/OneDrive/Desktop/HousePriceWeb/Be/core/settings.py)
- [ ] Test gọi API từ FE (không bị lỗi CORS)
- [ ] Tạo file `.env` để lưu biến môi trường

### Giai đoạn 8: Media Files (Ảnh) 🖼️

- [ ] Cấu hình `MEDIA_URL` và `MEDIA_ROOT` trong settings
- [ ] Xử lý upload ảnh trong Property
- [ ] Cấu hình URL phục vụ ảnh

### Giai đoạn 9: Hoàn thiện & Deploy 🚀

- [ ] Thêm Admin panel cho tất cả models
- [ ] Tạo superuser: `python manage.py createsuperuser`
- [ ] Viết tài liệu API (tự động qua Swagger)
- [ ] Review bảo mật (SECRET_KEY, DEBUG=False khi deploy)

---

## 4. Danh Sách API

> **Base URL:** `http://localhost:8000/api/`  
> 🔒 = Cần JWT token trong header: `Authorization: Bearer <token>`

### 🔐 Auth (Xác thực)

| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| POST | `/api/auth/register/` | Đăng ký tài khoản mới | ❌ |
| POST | `/api/auth/login/` | Đăng nhập, nhận JWT token | ❌ |
| POST | `/api/auth/token/refresh/` | Làm mới access token | ❌ |
| POST | `/api/auth/logout/` | Đăng xuất (blacklist token) | 🔒 |

### 👤 User Profile (Thông tin người dùng)

| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| GET | `/api/users/me/` | Xem thông tin của mình | 🔒 |
| PATCH | `/api/users/me/` | Cập nhật thông tin cá nhân | 🔒 |
| POST | `/api/users/change-password/` | Đổi mật khẩu | 🔒 |
| POST | `/api/users/upload-avatar/` | Upload ảnh đại diện | 🔒 |

### 🏠 Properties (Bất động sản)

| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| GET | `/api/properties/` | Danh sách nhà (có filter, paginate) | ❌ |
| GET | `/api/properties/{id}/` | Chi tiết 1 căn nhà | ❌ |
| POST | `/api/properties/` | Đăng nhà mới | 🔒 |
| PUT | `/api/properties/{id}/` | Cập nhật toàn bộ thông tin nhà | 🔒 |
| PATCH | `/api/properties/{id}/` | Cập nhật 1 phần thông tin | 🔒 |
| DELETE | `/api/properties/{id}/` | Xóa nhà | 🔒 |
| GET | `/api/properties/my-listings/` | Nhà của tôi đã đăng | 🔒 |
| POST | `/api/properties/{id}/favorite/` | Yêu thích / bỏ yêu thích | 🔒 |
| GET | `/api/properties/favorites/` | Danh sách nhà yêu thích | 🔒 |
| GET | `/api/properties/search/` | Tìm kiếm theo từ khóa | ❌ |

**Params filter cho GET /api/properties/:**
```
?city=HCM              → Lọc theo thành phố
?min_price=1000000000  → Giá tối thiểu
?max_price=5000000000  → Giá tối đa
?bedrooms=3            → Số phòng ngủ
?property_type=house   → Loại: house/apartment/land
?ordering=-created_at  → Sắp xếp (- = giảm dần)
?page=1&page_size=12   → Phân trang
```

### 📅 Appointments (Lịch xem nhà)

| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| GET | `/api/appointments/` | Danh sách lịch hẹn của tôi | 🔒 |
| GET | `/api/appointments/{id}/` | Chi tiết 1 lịch hẹn | 🔒 |
| POST | `/api/appointments/` | Đặt lịch xem nhà | 🔒 |
| PATCH | `/api/appointments/{id}/status/` | Cập nhật trạng thái (confirm/cancel) | 🔒 |
| DELETE | `/api/appointments/{id}/` | Hủy lịch hẹn | 🔒 |

### 📰 News (Tin tức)

| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| GET | `/api/news/` | Danh sách bài viết | ❌ |
| GET | `/api/news/{id}/` | Chi tiết bài viết | ❌ |
| POST | `/api/news/` | Tạo bài viết (admin) | 🔒 |
| PUT | `/api/news/{id}/` | Chỉnh sửa bài viết (admin) | 🔒 |
| DELETE | `/api/news/{id}/` | Xóa bài viết (admin) | 🔒 |

### 🤖 Predictions (Dự đoán giá)

| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| POST | `/api/predict/` | Dự đoán giá nhà bằng AI | ❌ |

**Request body:**
```json
{
  "area": 80,
  "bedrooms": 3,
  "bathrooms": 2,
  "district": "Quận 1",
  "city": "TP.HCM",
  "floor": 5,
  "year_built": 2015
}
```

**Response:**
```json
{
  "predicted_price": 4500000000,
  "unit": "VND",
  "confidence": 0.87
}
```

---

## 5. Hướng Dẫn Từng Bước

### Bước 1: Cài đặt MySQL & Môi trường

```bash
# 1. Mở MySQL Workbench hoặc terminal MySQL
# Tạo database:
CREATE DATABASE housesell_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 2. Mở terminal trong thư mục Be/
cd "c:\Users\minht\OneDrive\Desktop\HousePriceWeb\Be"

# 3. Kích hoạt virtual environment
venv\Scripts\activate      # Windows

# 4. Cài thiếu (nếu chưa có)
pip install django-cors-headers python-decouple

# 5. Cập nhật requirements.txt
pip freeze > requirements.txt
```

### Bước 2: Cập nhật settings.py

Thêm vào [core/settings.py](file:///c:/Users/minht/OneDrive/Desktop/HousePriceWeb/Be/core/settings.py):

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================
# CORS - Cho phép FE gọi API từ localhost:5173
# ============================================================
INSTALLED_APPS = [
    ...
    'corsheaders',        # Thêm dòng này
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_yasg',
    'accounts',           # Thêm khi tạo app
    'properties',         # Thêm khi tạo app
    'appointments',       # Thêm khi tạo app
    'news',               # Thêm khi tạo app
    'predictions',        # Thêm khi tạo app
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Phải đặt ĐẦU TIÊN
    'django.middleware.security.SecurityMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",   # Vite dev server
    "http://127.0.0.1:5173",
]

# ============================================================
# JWT Settings
# ============================================================
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),   # Token hết hạn sau 1 giờ
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),   # Refresh sau 7 ngày
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# ============================================================
# Media files (để lưu ảnh upload)
# ============================================================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

> **⚠️ Lưu ý:** Sau khi thêm `rest_framework_simplejwt.token_blacklist`, phải chạy migrate lại!

### Bước 3: Tạo App Accounts

```bash
# Trong thư mục Be/
python manage.py startapp accounts
```

**`accounts/models.py`** – Model thông tin người dùng:

```python
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Mở rộng thông tin của User mặc định Django
    - User mặc định có: username, email, password, first_name, last_name
    - Ta thêm: phone, avatar, address, ...
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile của {self.user.username}"
```

**`accounts/serializers.py`** – Chuyển đổi dữ liệu:

```python
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer cho đăng ký tài khoản"""
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']

    def validate(self, data):
        # Kiểm tra 2 mật khẩu có khớp không
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Mật khẩu không khớp!")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        # Tự động tạo profile cho user mới
        UserProfile.objects.create(user=user)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer cho thông tin profile"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'avatar', 'address', 'bio']

    def update(self, instance, validated_data):
        # Cập nhật cả User và UserProfile
        user_data = validated_data.pop('user', {})
        instance.user.first_name = user_data.get('first_name', instance.user.first_name)
        instance.user.last_name = user_data.get('last_name', instance.user.last_name)
        instance.user.save()
        return super().update(instance, validated_data)
```

**`accounts/views.py`** – Xử lý logic:

```python
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, UserProfileSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]  # Không cần đăng nhập

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Tạo JWT token ngay sau khi đăng ký
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Đăng ký thành công!',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                }
            })
        return Response({'error': 'Sai tài khoản hoặc mật khẩu!'}, status=status.HTTP_401_UNAUTHORIZED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]  # Phải đăng nhập
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user.profile  # Lấy profile của user đang đăng nhập
```

**`accounts/urls.py`** – Khai báo địa chỉ:

```python
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/me/', views.UserProfileView.as_view(), name='user-profile'),
]
```

**[core/urls.py](file:///c:/Users/minht/OneDrive/Desktop/HousePriceWeb/Be/core/urls.py)** – Thêm vào file URL chính:

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),       # ← Thêm dòng này
    path('api/', include('properties.urls')),           # ← Thêm sau
    path('api/', include('appointments.urls')),         # ← Thêm sau
    path('api/', include('news.urls')),                 # ← Thêm sau
    path('api/', include('predictions.urls')),          # ← Thêm sau
    # Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### Bước 4: Tạo App Properties

```bash
python manage.py startapp properties
```

**`properties/models.py`:**

```python
from django.db import models
from django.contrib.auth.models import User

class Property(models.Model):
    PROPERTY_TYPES = [
        ('house', 'Nhà riêng'),
        ('apartment', 'Căn hộ chung cư'),
        ('land', 'Đất nền'),
        ('villa', 'Biệt thự'),
        ('office', 'Văn phòng'),
    ]
    STATUS_CHOICES = [
        ('available', 'Còn trống'),
        ('sold', 'Đã bán'),
        ('rented', 'Đã thuê'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=200)            # Tiêu đề
    description = models.TextField()                   # Mô tả
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES, default='house')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    price = models.BigIntegerField()                    # Giá (VND)
    area = models.FloatField()                          # Diện tích (m²)
    bedrooms = models.IntegerField(default=0)
    bathrooms = models.IntegerField(default=0)
    floors = models.IntegerField(default=1)
    year_built = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=300)
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']  # Mới nhất lên đầu

    def __str__(self):
        return self.title


class PropertyImage(models.Model):
    """Ảnh của căn nhà (1 nhà có nhiều ảnh)"""
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/')
    is_thumbnail = models.BooleanField(default=False)   # Ảnh bìa
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"Ảnh {self.id} của {self.property.title}"


class PropertyFavorite(models.Model):
    """Danh sách nhà yêu thích của user"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'property')  # Mỗi user chỉ yêu thích 1 lần
```

**`properties/serializers.py`:**

```python
from rest_framework import serializers
from .models import Property, PropertyImage, PropertyFavorite

class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'is_thumbnail', 'order']

class PropertyListSerializer(serializers.ModelSerializer):
    """Dùng cho danh sách (ít trường hơn để nhẹ hơn)"""
    thumbnail = serializers.SerializerMethodField()
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = ['id', 'title', 'price', 'area', 'bedrooms', 'bathrooms',
                  'property_type', 'status', 'district', 'city',
                  'thumbnail', 'owner_name', 'is_favorited', 'view_count', 'created_at']

    def get_thumbnail(self, obj):
        # Lấy ảnh thumbnail
        thumb = obj.images.filter(is_thumbnail=True).first()
        if thumb:
            request = self.context.get('request')
            return request.build_absolute_uri(thumb.image.url) if request else thumb.image.url
        return None

    def get_is_favorited(self, obj):
        # Kiểm tra user hiện tại có yêu thích không
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False

class PropertyDetailSerializer(PropertyListSerializer):
    """Dùng cho chi tiết (đầy đủ trường hơn)"""
    images = PropertyImageSerializer(many=True, read_only=True)

    class Meta(PropertyListSerializer.Meta):
        fields = PropertyListSerializer.Meta.fields + [
            'description', 'floors', 'year_built', 'address',
            'latitude', 'longitude', 'images', 'updated_at'
        ]
```

**`properties/views.py`:**

```python
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Property, PropertyFavorite
from .serializers import PropertyListSerializer, PropertyDetailSerializer

class PropertyListCreateView(generics.ListCreateAPIView):
    """GET: Danh sách | POST: Tạo mới"""
    queryset = Property.objects.filter(status='available')
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'district', 'property_type', 'bedrooms', 'bathrooms']
    search_fields = ['title', 'description', 'address']
    ordering_fields = ['price', 'area', 'created_at', 'view_count']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PropertyListSerializer
        return PropertyDetailSerializer

    def perform_create(self, serializer):
        # Tự động gán owner là user đang đăng nhập
        serializer.save(owner=self.request.user)


class PropertyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET: Chi tiết | PUT/PATCH: Sửa | DELETE: Xóa"""
    queryset = Property.objects.all()
    serializer_class = PropertyDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count += 1  # Tăng lượt xem
        instance.save(update_fields=['view_count'])
        return super().retrieve(request, *args, **kwargs)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, pk):
    """Yêu thích / bỏ yêu thích nhà"""
    property_obj = Property.objects.get(pk=pk)
    favorite, created = PropertyFavorite.objects.get_or_create(
        user=request.user, property=property_obj
    )
    if not created:
        favorite.delete()
        return Response({'status': 'removed', 'message': 'Đã bỏ yêu thích'})
    return Response({'status': 'added', 'message': 'Đã thêm vào yêu thích'})
```

### Bước 5: Chạy Migration

```bash
# Mỗi khi thêm/sửa model, phải chạy 2 lệnh này:
python manage.py makemigrations    # Tạo file migration
python manage.py migrate           # Áp dụng vào database

# Tạo admin để vào trang /admin/
python manage.py createsuperuser
```

### Bước 6: Đăng ký Admin Panel

**`accounts/admin.py`:**
```python
from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'created_at']
    search_fields = ['user__username', 'user__email']
```

**`properties/admin.py`:**
```python
from django.contrib import admin
from .models import Property, PropertyImage

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'price', 'city', 'status', 'created_at']
    list_filter = ['status', 'property_type', 'city']
    search_fields = ['title', 'address', 'owner__username']
    inlines = [PropertyImageInline]
```

### Bước 7: Tạo App Appointments

```bash
python manage.py startapp appointments
```

**`appointments/models.py`:**

```python
from django.db import models
from django.contrib.auth.models import User
from properties.models import Property

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('cancelled', 'Đã hủy'),
        ('completed', 'Đã xem xong'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='appointments')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_buyer')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_seller')
    scheduled_time = models.DateTimeField()
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyer.username} - {self.property.title} ({self.get_status_display()})"
```

### Bước 8: App Predictions (AI dự đoán giá)

```bash
python manage.py startapp predictions
```

**`predictions/views.py`:**

```python
import pickle
import os
import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

# Load model AI từ thư mục LinearRegressionModel
MODEL_PATH = os.path.join(settings.BASE_DIR.parent, 'LinearRegressionModel', 'model.pkl')

class PredictPriceView(APIView):
    def post(self, request):
        try:
            # Nhận dữ liệu từ FE
            data = request.data
            area = float(data.get('area', 0))
            bedrooms = int(data.get('bedrooms', 0))
            bathrooms = int(data.get('bathrooms', 0))

            # Load model và dự đoán
            with open(MODEL_PATH, 'rb') as f:
                model = pickle.load(f)

            features = np.array([[area, bedrooms, bathrooms]])
            predicted_price = model.predict(features)[0]

            return Response({
                'predicted_price': int(predicted_price),
                'unit': 'VND',
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
```

---

## 6. Kết Nối Frontend

### Cấu hình base URL trong FE

Tạo file `FE/src/lib/api.ts`:

```typescript
// Địa chỉ backend
const BASE_URL = 'http://localhost:8000/api';

// Hàm gọi API có kèm JWT token
async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const token = localStorage.getItem('access_token');
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  // Nếu token hết hạn, tự động refresh
  if (response.status === 401) {
    await refreshToken();
    // Gọi lại request
    return apiFetch(endpoint, options);
  }

  return response.json();
}

// Refresh token tự động
async function refreshToken() {
  const refresh = localStorage.getItem('refresh_token');
  const res = await fetch(`${BASE_URL}/auth/token/refresh/`, {
    method: 'POST',
    body: JSON.stringify({ refresh }),
    headers: { 'Content-Type': 'application/json' },
  });
  const data = await res.json();
  localStorage.setItem('access_token', data.access);
}

export { apiFetch };
```

### Ví dụ gọi API từ FE

```typescript
// Lấy danh sách nhà
const properties = await apiFetch('/properties/');

// Đăng nhập
const loginData = await apiFetch('/auth/login/', {
  method: 'POST',
  body: JSON.stringify({ username: 'abc', password: '123456' }),
});
localStorage.setItem('access_token', loginData.access);
localStorage.setItem('refresh_token', loginData.refresh);

// Tạo nhà mới (cần đăng nhập)
const newProperty = await apiFetch('/properties/', {
  method: 'POST',
  body: JSON.stringify({
    title: 'Nhà đẹp Quận 1',
    price: 3500000000,
    area: 75,
    ...
  }),
});
```

---

## 7. Kiểm Thử API với Swagger

### Truy cập Swagger UI

Sau khi chạy BE (`python manage.py runserver`), mở trình duyệt:

```
http://localhost:8000/swagger/
```

### Cách test API có Auth trên Swagger

1. Vào `POST /api/auth/login/` → nhập username/password → nhận `access` token
2. Click nút **Authorize 🔒** ở góc phải trên
3. Nhập: `Bearer <access_token_của_bạn>`
4. Giờ bạn có thể test các API cần đăng nhập

---

## 8. Lỗi Thường Gặp

### ❌ CORS Error (Frontend không gọi được BE)

```
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:5173' 
has been blocked by CORS policy
```

**Cách sửa:** Kiểm tra [settings.py](file:///c:/Users/minht/OneDrive/Desktop/HousePriceWeb/Be/core/settings.py) đã có:
```python
CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]
# VÀ corsheaders ở đầu MIDDLEWARE
```

---

### ❌ 401 Unauthorized

Frontend gọi API nhưng bị báo 401.

**Cách sửa:** Kiểm tra header gửi lên có đúng format chưa:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```
Không phải `Token ...` hay chỉ là token thuần.

---

### ❌ No module named 'corsheaders'

```bash
pip install django-cors-headers
```

---

### ❌ django.db.utils.OperationalError: (1049) Unknown database 'housesell_db'

→ Chưa tạo database MySQL. Chạy lệnh SQL:
```sql
CREATE DATABASE housesell_db CHARACTER SET utf8mb4;
```

---

### ❌ makemigrations không tạo file mới

→ Chưa thêm app vào `INSTALLED_APPS` trong [settings.py](file:///c:/Users/minht/OneDrive/Desktop/HousePriceWeb/Be/core/settings.py).

---

### ❌ Image field cần Pillow

```bash
pip install Pillow
```

---

## 🎯 Thứ Tự Làm Từng Ngày

| Ngày | Mục tiêu |
|------|-----------|
| **Ngày 1** | Setup MySQL, cấu hình settings.py, chạy server thành công |
| **Ngày 2** | Xây dựng app `accounts`: Register, Login, JWT token |
| **Ngày 3** | Xây dựng app `properties`: CRUD nhà, upload ảnh |
| **Ngày 4** | Filter, search, phân trang cho danh sách nhà |
| **Ngày 5** | App `appointments`: đặt lịch xem nhà |
| **Ngày 6** | App `news`: tin tức |
| **Ngày 7** | App `predictions`: dự đoán giá bằng AI |
| **Ngày 8** | Kết nối FE ↔ BE, test E2E toàn bộ luồng |
| **Ngày 9** | Admin panel, review bảo mật, hoàn thiện |

---

## 📚 Tài Liệu Tham Khảo

- [Django REST Framework Docs](https://www.django-rest-framework.org/)
- [Simple JWT Docs](https://django-rest-framework-simplejwt.readthedocs.io/)
- [drf-yasg (Swagger) Docs](https://drf-yasg.readthedocs.io/)
- [Django Docs (Tiếng Anh)](https://docs.djangoproject.com/en/4.2/)
- Swagger UI của dự án: `http://localhost:8000/swagger/`
- Admin panel: `http://localhost:8000/admin/`

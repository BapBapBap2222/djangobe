from django.urls import path
from . import views

urlpatterns = [
    # Danh sách & tạo mới BĐS
    path('', views.PropertyListCreateView.as_view(), name='property-list-create'),

    # BĐS của tôi
    path('my/', views.MyPropertiesView.as_view(), name='my-properties'),

    # Chi tiết, cập nhật, xóa
    path('<int:pk>/', views.PropertyDetailView.as_view(), name='property-detail'),

    # Ảnh BĐS
    path('<int:pk>/images/', views.PropertyImageUploadView.as_view(), name='property-image-upload'),
    path('images/<int:pk>/', views.PropertyImageDeleteView.as_view(), name='property-image-delete'),

    # Yêu thích
    path('favorites/', views.FavoriteListView.as_view(), name='favorite-list'),
    path('<int:pk>/favorite/', views.FavoriteToggleView.as_view(), name='favorite-toggle'),
]

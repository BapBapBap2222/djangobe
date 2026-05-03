from django.urls import path
from . import views

urlpatterns = [
    # Lịch hẹn của người đi thuê/mua (User)
    path('', views.AppointmentListView.as_view(), name='appointment-list'),
    
    # Lịch hẹn khách đặt vào nhà của mình (Chủ nhà)
    path('owner/', views.OwnerAppointmentListView.as_view(), name='owner-appointment-list'),
    
    # Các thao tác chi tiết (Xem, Hủy)
    path('<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment-detail'),
    
    # Đổi trạng thái lịch hẹn
    path('<int:pk>/status/', views.AppointmentStatusUpdateView.as_view(), name='appointment-status-update'),
]

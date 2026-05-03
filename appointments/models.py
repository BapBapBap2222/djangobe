from django.db import models
from django.contrib.auth.models import User
from properties.models import Property


class AppointmentStatus(models.TextChoices):
    PENDING   = 'pending',   'Chờ xác nhận'
    CONFIRMED = 'confirmed', 'Đã xác nhận'
    REJECTED  = 'rejected',  'Bị từ chối'
    COMPLETED = 'completed', 'Đã hoàn thành'
    CANCELLED = 'cancelled', 'Đã hủy'


class Appointment(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments', verbose_name='Người đăng ký')
    property   = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='appointments', verbose_name='Bất động sản')
    
    # Lịch hẹn
    date       = models.DateField(verbose_name='Ngày hẹn')
    time       = models.TimeField(verbose_name='Giờ hẹn')
    
    # Thông tin liên hệ phụ (nếu họ khác thông tin trên Profile)
    name       = models.CharField(max_length=150, verbose_name='Tên người liên hệ')
    phone      = models.CharField(max_length=15, verbose_name='Số điện thoại')
    message    = models.TextField(blank=True, null=True, verbose_name='Lời nhắn bổ sung')
    
    status     = models.CharField(max_length=20, choices=AppointmentStatus.choices, default=AppointmentStatus.PENDING, verbose_name='Trạng thái')

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Lịch hẹn'
        verbose_name_plural = 'Lịch hẹn'
        ordering = ['-date', '-time']

    def __str__(self):
        return f"{self.user.username} xem {self.property.title} lúc {self.time} {self.date}"

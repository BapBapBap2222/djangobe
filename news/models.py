from django.db import models
from django.contrib.auth.models import User

class News(models.Model):
    title       = models.CharField(max_length=255, verbose_name='Tiêu đề')
    content     = models.TextField(verbose_name='Nội dung')
    thumbnail   = models.ImageField(upload_to='news/%Y/%m/', null=True, blank=True, verbose_name='Ảnh đại diện')
    author      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_news', verbose_name='Tác giả')
    
    views_count = models.PositiveIntegerField(default=0, verbose_name='Lượt xem')
    is_published = models.BooleanField(default=True, verbose_name='Được xuất bản')
    
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tin tức'
        verbose_name_plural = 'Tin tức'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

"""
信号 — 自动同步 is_staff 字段

当用户角色为 teacher/admin 时，自动将 is_staff 设为 True。
"""

from django.db.models.signals import pre_save
from django.dispatch import receiver


@receiver(pre_save, sender='accounts.User')
def sync_staff_on_save(sender, instance, **kwargs):
    """保存用户时，根据角色自动设置 is_staff。"""
    if instance.role in ('teacher', 'admin') or instance.is_superuser:
        instance.is_staff = True

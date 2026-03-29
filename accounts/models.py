"""
用户模型 — 支持三角色：student / ta / teacher
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """自定义用户模型，在 Django 原生 User 基础上增加角色和学号。"""

    ROLE_CHOICES = [
        ('student', '学生'),
        ('ta', '助教'),
        ('teacher', '教师'),
        ('admin', '管理员'),
    ]

    role = models.CharField('角色', max_length=10, choices=ROLE_CHOICES, default='student')
    display_name = models.CharField('显示名称', max_length=50, blank=True, default='')
    student_id = models.CharField('学号', max_length=20, blank=True, default='')

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return f"{self.display_name or self.username} ({self.get_role_display()})"

    # ── 便捷属性：角色判断 ──
    @property
    def is_teacher(self):
        return self.role in ('teacher', 'admin')

    @property
    def is_ta(self):
        return self.role == 'ta'

    @property
    def is_student(self):
        return self.role == 'student'

    @property
    def is_teacher_or_ta(self):
        return self.role in ('teacher', 'ta', 'admin')

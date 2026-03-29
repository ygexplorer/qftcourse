"""
用户管理 — Django Admin 配置
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.html import format_html
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """自定义用户管理后台"""

    list_display = ('username', 'display_name', 'role', 'student_id', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'display_name', 'student_id')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('课程信息', {
            'fields': ('role', 'display_name', 'student_id')
        }),
    )

    # 添加用户时的字段
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('课程信息', {
            'fields': ('role', 'display_name', 'student_id')
        }),
    )

    def changelist_view(self, request, extra_context=None):
        """在用户列表页顶部添加「批量导入学生」按钮"""
        extra_context = extra_context or {}
        extra_context['import_students_url'] = reverse('import_students')
        return super().changelist_view(request, extra_context)

    # ── 教师权限：允许教师（非 superuser）管理用户 ──
    def _is_teacher_or_admin(self, request):
        """安全判断用户是否为教师/管理员（兼容 AnonymousUser）"""
        u = request.user
        if not u.is_authenticated:
            return False
        return getattr(u, 'role', None) in ('teacher', 'admin') or u.is_superuser

    def has_module_permission(self, request):
        return self._is_teacher_or_admin(request)

    def has_view_permission(self, request, obj=None):
        return self._is_teacher_or_admin(request)

    def has_add_permission(self, request):
        return self._is_teacher_or_admin(request)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not request.user.is_authenticated:
            return False
        role = getattr(request.user, 'role', None)
        if role in ('teacher', 'admin') and obj is not None:
            return getattr(obj, 'role', None) in ('student', 'ta')
        return role in ('teacher', 'admin')

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not request.user.is_authenticated:
            return False
        role = getattr(request.user, 'role', None)
        if role in ('teacher', 'admin') and obj is not None:
            return getattr(obj, 'role', None) in ('student', 'ta')
        return False

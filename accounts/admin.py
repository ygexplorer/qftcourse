"""
用户管理 — Django Admin 配置
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.urls import reverse
from django.utils.html import format_html
from .models import User


class CustomUserChangeForm(UserChangeForm):
    """编辑用户表单 — 教师只能选 student/ta 角色"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 教师角色：只能将用户设为 student 或 ta
        request = self.request if hasattr(self, 'request') else None
        if request and not request.user.is_superuser:
            self.fields['role'].choices = [
                c for c in self.fields['role'].choices
                if c[0] in ('student', 'ta')
            ]


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """自定义用户管理后台"""

    list_display = ('username', 'display_name', '_role_display', 'student_id', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'display_name', 'student_id')
    ordering = ('-date_joined',)
    form = CustomUserChangeForm

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

    def _role_display(self, obj):
        """
        智能显示角色：
        - superuser → 管理员
        - role 字段有值 → 对应角色
        - 都没有 → 未知
        """
        if obj.is_superuser:
            return format_html('<span class="badge" style="background:#dc2626;color:#fff;padding:2px 8px;border-radius:4px;">管理员</span>')
        return obj.get_role_display() or '未设置'
    _role_display.short_description = '角色'

    def get_form(self, request, obj=None, **kwargs):
        """把 request 传入表单，让表单能判断当前用户角色"""
        form = super().get_form(request, obj, **kwargs)
        form.request = request

        # 教师和非 superuser 的 admin 角色：限制可选角色
        if not request.user.is_superuser:
            if 'role' in form.base_fields:
                form.base_fields['role'].choices = [
                    c for c in form.base_fields['role'].choices
                    if c[0] in ('student', 'ta')
                ]
        return form

    def save_model(self, request, obj, form, changed):
        """
        保存用户时同步角色与 Django 权限：
        - role='admin' → is_staff=True, is_superuser=True
        - role 改为非 admin → is_staff=False, is_superuser=False
        """
        if obj.role == 'admin' and not obj.is_superuser:
            obj.is_staff = True
            obj.is_superuser = True
        elif obj.role != 'admin' and obj.is_superuser and not request.user.is_superuser:
            # 非 superuser 不能把别人的 admin 权限改掉，只在自己操作时生效
            pass
        super().save_model(request, obj, form, changed)

    def changelist_view(self, request, extra_context=None):
        """在用户列表页顶部添加「批量导入学生」按钮"""
        extra_context = extra_context or {}
        extra_context['import_students_url'] = reverse('import_students')
        return super().changelist_view(request, extra_context)

    # ── 权限控制 ──
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
        # 教师/管理员只能修改 student 和 ta
        if role in ('teacher', 'admin') and obj is not None:
            return not obj.is_superuser and getattr(obj, 'role', None) in ('student', 'ta')
        return role in ('teacher', 'admin')

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not request.user.is_authenticated:
            return False
        role = getattr(request.user, 'role', None)
        # 教师/管理员只能删除 student 和 ta
        if role in ('teacher', 'admin') and obj is not None:
            return not obj.is_superuser and getattr(obj, 'role', None) in ('student', 'ta')
        return False

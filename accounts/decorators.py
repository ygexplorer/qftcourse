"""
权限装饰器和 Mixin — 三角色权限控制

使用方式：
    @role_required('teacher')
    def my_view(request): ...

    @role_required('teacher', 'ta')
    def my_view(request): ...  # 教师和助教都能访问
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required as django_login_required
from django.contrib import messages


def role_required(*roles):
    """
    视图装饰器：限制只有指定角色才能访问。
    未登录 → 跳转登录页
    已登录但角色不对 → 跳转到无权限提示页
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # 1. 未登录 → 跳转登录页
            if not request.user.is_authenticated:
                messages.warning(request, '请先登录后再访问该页面。')
                return redirect('accounts:login')

            # 2. superuser 拥有所有权限，直接放行
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # 3. 已登录但角色不匹配 → 跳转无权限页
            if request.user.role not in roles:
                return redirect('accounts:permission_denied')

            # 4. 角色匹配 → 放行
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ── 便捷装饰器：常用角色组合 ──

def teacher_required(view_func):
    """只有教师可以访问"""
    return role_required('teacher')(view_func)


def ta_required(view_func):
    """只有助教可以访问"""
    return role_required('ta')(view_func)


def teacher_or_ta_required(view_func):
    """教师和助教都可以访问"""
    return role_required('teacher', 'ta')(view_func)


def student_required(view_func):
    """只有学生可以访问"""
    return role_required('student')(view_func)


def login_required(view_func):
    """登录即可访问（不限角色）"""
    return django_login_required(view_func)

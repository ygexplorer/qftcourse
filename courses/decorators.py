"""
权限装饰器 — 作业系统使用

注：核心的用户角色装饰器在 accounts/decorators.py 中。
这里的装饰器是 courses app 专用的（如果需要的话）。
"""

from functools import wraps
from django.shortcuts import redirect


def teacher_required(view_func):
    """要求教师角色"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if getattr(request.user, 'role', '') != 'teacher':
            return redirect('accounts:permission_denied')
        return view_func(request, *args, **kwargs)
    return wrapper


def ta_required(view_func):
    """要求助教角色"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if getattr(request.user, 'role', '') != 'ta':
            return redirect('accounts:permission_denied')
        return view_func(request, *args, **kwargs)
    return wrapper


def student_required(view_func):
    """要求学生角色"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if getattr(request.user, 'role', '') != 'student':
            return redirect('accounts:permission_denied')
        return view_func(request, *args, **kwargs)
    return wrapper

"""
用户管理视图 — 第三阶段完整实现

包含：登录（按角色跳转）、学生注册、权限拒绝页、三种角色仪表盘
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required as django_login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.urls import reverse

from .forms import CustomLoginForm, StudentRegistrationForm, CustomPasswordChangeForm
from .decorators import teacher_required, ta_required, student_required, role_required


# ──────────────────────────────────────────
# 登录
# ──────────────────────────────────────────

def login_view(request):
    """
    登录页面
    - GET：显示登录表单
    - POST：验证并登录，按角色跳转到对应仪表盘
    """
    # 如果已登录，直接跳转到对应仪表盘
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'欢迎回来，{user.display_name or user.username}！')
                # 登录成功 → 按角色跳转
                return _redirect_by_role(user)
        else:
            messages.error(request, '用户名或密码不正确。')
    else:
        form = CustomLoginForm(request)

    return render(request, 'accounts/login.html', {'form': form})


def _redirect_by_role(user):
    """根据用户角色返回对应的跳转地址"""
    if user.is_teacher:
        return redirect('accounts:teacher_dashboard')
    elif user.is_ta:
        return redirect('accounts:ta_dashboard')
    else:
        return redirect('courses:home')


# ──────────────────────────────────────────
# 学生注册（仅 student）
# ──────────────────────────────────────────

def register(request):
    """
    学生注册页面
    - TA 和 Teacher 不允许通过此页面注册，由管理员创建
    - 已登录用户不允许再注册
    """
    # 已登录用户跳转到仪表盘
    if request.user.is_authenticated:
        messages.info(request, '你已经登录，无需再注册。')
        return _redirect_by_role(request.user)

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 注册后自动登录
            login(request, user)
            messages.success(request, f'注册成功！欢迎，{user.display_name or user.username}。')
            return redirect('courses:home')
    else:
        form = StudentRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


# ──────────────────────────────────────────
# 修改密码（所有已登录角色）
# ──────────────────────────────────────────

class CustomPasswordChangeView(PasswordChangeView):
    """
    修改密码视图 — 基于 Django 内置 PasswordChangeView
    - 修改成功后保持登录状态（Django 内置 update_session_auth_hash）
    - 修改成功后跳回用户的角色仪表盘
    """
    form_class = CustomPasswordChangeForm
    template_name = 'accounts/password_change.html'

    def get_success_url(self):
        """修改成功后按角色跳回对应仪表盘"""
        user = self.request.user
        if user.is_teacher:
            return reverse('accounts:teacher_dashboard')
        elif user.is_ta:
            return reverse('accounts:ta_dashboard')
        else:
            return reverse('courses:assignment_list')

    def form_valid(self, form):
        """修改成功后给出提示"""
        messages.success(self.request, '密码修改成功！')
        return super().form_valid(form)


# ──────────────────────────────────────────
# 权限拒绝页（403 友好提示）
# ──────────────────────────────────────────

def permission_denied(request):
    """
    当用户角色不满足要求时，显示友好的无权限提示页。
    注意：返回 200 状态码而不是 403，避免被 Django 安全中间件拦截。
    """
    return render(request, 'accounts/permission_denied.html')


# ──────────────────────────────────────────
# 仪表盘 — 按角色分别实现
# ──────────────────────────────────────────

def dashboard(request):
    """
    通用仪表盘入口 → 根据角色跳转
    未登录 → 登录页
    """
    if not request.user.is_authenticated:
        messages.warning(request, '请先登录。')
        return redirect('accounts:login')
    return _redirect_by_role(request.user)


@teacher_required
def teacher_dashboard(request):
    """
    教师仪表盘 — 只有 teacher 角色能访问
    """
    return render(request, 'courses/teacher/dashboard.html', {
        'role': 'teacher',
    })


@ta_required
def ta_dashboard(request):
    """
    助教仪表盘 — 只有 ta 角色能访问
    """
    return render(request, 'courses/ta/dashboard.html', {
        'role': 'ta',
    })




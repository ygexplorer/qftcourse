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

from .models import User
from .forms import CustomLoginForm, StudentRegistrationForm, CustomPasswordChangeForm, ImportStudentsForm, ProfileEditForm
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
# 个人资料编辑
# ──────────────────────────────────────────

@django_login_required
def profile_edit(request):
    """
    个人资料编辑 — 所有已登录角色均可访问
    仅允许修改 display_name 和 student_id，不可修改 username 和 role
    """
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '个人资料已更新。')
            return _redirect_by_role(request.user)
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, 'accounts/profile_edit.html', {'form': form})


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


# ──────────────────────────────────────────
# 学生批量导入（Admin 页面）
# ──────────────────────────────────────────

def import_students_view(request):
    """
    批量导入学生 — 在 Admin 页面中上传 Excel 选课单

    导入逻辑：
    - 读取 Excel 的「学号」和「姓名」列
    - 用户名 = 学号，display_name = 姓名，student_id = 学号
    - 初始密码 = 学号后 6 位
    - 角色固定为 student
    - 如果用户名已存在则跳过
    """
    if request.method == 'POST':
        form = ImportStudentsForm(request.POST, request.FILES)
        if form.is_valid():
            result = _do_import(form.cleaned_data['excel_file'])
            return render(request, 'accounts/admin/import_result.html', {
                **result,
                'title': '导入结果',
            })
    else:
        form = ImportStudentsForm()

    return render(request, 'accounts/admin/import_students.html', {
        'form': form,
        'title': '批量导入学生',
        'opts': User._meta,
    })


def _do_import(excel_file):
    """
    执行导入，返回结果字典

    返回：
    {
        'total': int,      # 总行数
        'created': list,   # 成功创建的 [(学号, 姓名), ...]
        'skipped': list,   # 已存在跳过的 [(学号, 姓名), ...]
        'errors': list,    # 导入失败的 [(行号, 原因), ...]
    }
    """
    import pandas as pd

    created = []
    skipped = []
    errors = []

    try:
        df = pd.read_excel(excel_file, dtype={'学号': str})
    except Exception as e:
        return {
            'total': 0, 'created': created, 'skipped': skipped,
            'errors': [(0, f'读取 Excel 失败: {e}')],
        }

    # 检查必须的列
    if '学号' not in df.columns or '姓名' not in df.columns:
        return {
            'total': len(df), 'created': created, 'skipped': skipped,
            'errors': [(0, f'Excel 缺少必须的列。当前列名: {list(df.columns)}，需要「学号」和「姓名」。')],
        }

    total = len(df)
    for idx, row in df.iterrows():
        student_id = str(row.get('学号', '')).strip()
        name = str(row.get('姓名', '')).strip()

        # 跳过空行
        if not student_id or not name or student_id == 'nan' or name == 'nan':
            errors.append((idx + 2, f'学号或姓名为空（学号={student_id}, 姓名={name}）'))
            continue

        # 密码 = 学号后 6 位
        password = student_id[-6:]

        # 检查是否已存在
        if User.objects.filter(username=student_id).exists():
            skipped.append((student_id, name))
            continue

        # 创建用户
        try:
            user = User.objects.create_user(
                username=student_id,
                password=password,
                display_name=name,
                student_id=student_id,
                role='student',
            )
            created.append((student_id, name))
        except Exception as e:
            errors.append((idx + 2, f'创建失败: {e}'))

    return {
        'total': total,
        'created': created,
        'skipped': skipped,
        'errors': errors,
    }




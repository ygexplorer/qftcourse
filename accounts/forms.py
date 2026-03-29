"""
登录和注册表单
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .models import User


class CustomLoginForm(AuthenticationForm):
    """
    登录表单 — 在 Django 自带 AuthenticationForm 基础上美化字段
    """
    username = forms.CharField(
        label='用户名',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition',
            'placeholder': '请输入用户名',
        })
    )
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition',
            'placeholder': '请输入密码',
        })
    )

    error_messages = {
        'invalid_login': '用户名或密码不正确，请重试。',
        'inactive': '此账号已被禁用，请联系管理员。',
    }


class StudentRegistrationForm(forms.ModelForm):
    """
    学生注册表单 — 只有 student 角色可通过此表单注册
    """
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition',
            'placeholder': '至少 6 个字符',
        }),
        min_length=6,
        help_text='密码长度至少 6 个字符'
    )
    password_confirm = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition',
            'placeholder': '请再次输入密码',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'display_name', 'student_id']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition',
                'placeholder': '用于登录的用户名',
            }),
            'display_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition',
                'placeholder': '你的真实姓名（选填）',
            }),
            'student_id': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition',
                'placeholder': '学号（选填）',
            }),
        }

    def clean_password_confirm(self):
        """检查两次密码是否一致"""
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('两次输入的密码不一致。')
        return password_confirm

    def clean_username(self):
        """检查用户名是否已存在"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('该用户名已被注册。')
        return username

    def save(self, commit=True):
        """保存用户，密码加密，角色固定为 student"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = 'student'  # 注册固定为学生角色
        if commit:
            user.save()
        return user


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    修改密码表单 — 在 Django 自带 PasswordChangeForm 基础上美化字段和提示文字
    """
    error_messages = {
        'password_incorrect': '旧密码不正确，请重新输入。',
        'password_mismatch': '两次输入的新密码不一致。',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 美化所有字段的样式
        field_attrs = {
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition',
        }
        placeholders = {
            'old_password': '请输入当前密码',
            'new_password1': '请输入新密码（至少 6 个字符）',
            'new_password2': '请再次输入新密码',
        }
        labels = {
            'old_password': '当前密码',
            'new_password1': '新密码',
            'new_password2': '确认新密码',
        }
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update(field_attrs)
            self.fields[field_name].widget.attrs['placeholder'] = placeholders.get(field_name, '')
            self.fields[field_name].label = labels.get(field_name, self.fields[field_name].label)


class ProfileEditForm(forms.ModelForm):
    """
    个人资料编辑表单 — 仅允许修改 display_name 和 student_id
    username 和 role 不可修改，防止用户篡改身份信息
    """

    class Meta:
        model = User
        fields = ['display_name', 'student_id']
        widgets = {
            'display_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition',
                'placeholder': '你的真实姓名（选填）',
            }),
            'student_id': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition',
                'placeholder': '学号（选填）',
            }),
        }


class ImportStudentsForm(forms.Form):
    """
    上传 Excel 选课单，批量创建学生账号

    期望的 Excel 格式：
    - 必须包含「学号」和「姓名」两列
    - 支持 .xls 和 .xlsx 格式
    """

    excel_file = forms.FileField(
        label='选课单文件',
        help_text='支持 .xls / .xlsx 格式，必须包含「学号」和「姓名」列',
        widget=forms.FileInput(attrs={
            'accept': '.xls,.xlsx',
        }),
    )

    def clean_excel_file(self):
        f = self.cleaned_data.get('excel_file')
        if f and hasattr(f, 'name'):
            name = f.name.lower()
            if not (name.endswith('.xls') or name.endswith('.xlsx')):
                raise ValidationError('只支持 .xls 或 .xlsx 格式的 Excel 文件。')
        return f

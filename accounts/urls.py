"""用户管理 URL 路由"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # 登录 / 注册 / 登出
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('profile/', views.profile_edit, name='profile_edit'),

    # 通用仪表盘入口（根据角色跳转）
    path('dashboard/', views.dashboard, name='dashboard'),

    # 权限拒绝提示页
    path('permission-denied/', views.permission_denied, name='permission_denied'),

    # 角色专属仪表盘
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('ta/dashboard/', views.ta_dashboard, name='ta_dashboard'),
]

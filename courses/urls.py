"""课程 URL 路由"""

from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # 首页 / 学期 / 章节（第四阶段）
    path('', views.home, name='home'),
    path('semester/<slug:slug>/', views.semester_home, name='semester_home'),
    path('semester/<slug:semester_slug>/<slug:chapter_slug>/', views.chapter_detail, name='chapter_detail'),

    # 作业系统（第五阶段）
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignment/<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('assignment/<int:pk>/submit/', views.assignment_detail, name='assignment_submit'),  # POST 提交复用 detail
    path('submission/<int:pk>/download/', views.download_submission, name='download_submission'),
    path('assignment/<int:pk>/attachment/', views.download_attachment, name='download_attachment'),
]

"""课程 URL 路由"""

from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # 首页
    path('', views.home, name='home'),

    # 公告系统（第七阶段）— 必须在 semester_home 之前，否则 "announcements" 会被 slug 匹配吃掉
    path('semester/<slug:slug>/announcements/', views.announcement_list, name='announcement_list'),
    path('announcement/<int:pk>/', views.announcement_detail, name='announcement_detail'),

    # 学期 / 章节（第四阶段）
    path('semester/<slug:slug>/', views.semester_home, name='semester_home'),
    path('semester/<slug:semester_slug>/<slug:chapter_slug>/', views.chapter_detail, name='chapter_detail'),

    # 作业系统（第五阶段）
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignment/<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('assignment/<int:pk>/submit/', views.assignment_detail, name='assignment_submit'),  # POST 提交复用 detail
    path('assignment/<int:pk>/grading/', views.grading_workstation, name='grading_workstation'),  # 教师评分工作台
    path('submission/<int:pk>/grade/', views.grade_submission, name='grade_submission'),
    path('submission/<int:pk>/download/', views.download_submission, name='download_submission'),
    path('assignment/<int:pk>/attachment/', views.download_attachment, name='download_attachment'),

    # 章节讲义下载（第十二阶段）
    path('chapter/<int:pk>/lecture/', views.download_lecture, name='download_lecture'),
]

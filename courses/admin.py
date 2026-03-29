"""
课程管理 — Django Admin 配置
"""

from django.contrib import admin
from .models import Semester, Announcement, Chapter, Assignment, Submission
from .utils import validate_pdf


def _is_teacher_or_admin(user):
    """安全判断用户是否为教师/管理员（兼容 AnonymousUser）"""
    if not user.is_authenticated:
        return False
    return getattr(user, 'role', None) in ('teacher', 'admin') or user.is_superuser


class TeacherAdminMixin:
    """Mixin：教师和管理员都可以管理"""
    def has_module_permission(self, request):
        return _is_teacher_or_admin(request.user)

    def has_view_permission(self, request, obj=None):
        return _is_teacher_or_admin(request.user)

    def has_add_permission(self, request):
        return _is_teacher_or_admin(request.user)

    def has_change_permission(self, request, obj=None):
        return _is_teacher_or_admin(request.user)

    def has_delete_permission(self, request, obj=None):
        return _is_teacher_or_admin(request.user)


@admin.register(Semester)
class SemesterAdmin(TeacherAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_current', 'start_date', 'end_date')
    list_editable = ('is_current',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Announcement)
class AnnouncementAdmin(TeacherAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'semester', 'author', 'is_pinned', 'created_at')
    list_filter = ('semester', 'is_pinned')
    search_fields = ('title',)


@admin.register(Chapter)
class ChapterAdmin(TeacherAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'semester', 'order_index', 'is_published', 'has_lecture', 'created_at')
    list_filter = ('semester', 'is_published')
    list_editable = ('order_index', 'is_published')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 50

    fieldsets = (
        ('基本信息', {
            'fields': ('semester', 'author', 'title', 'slug', 'is_published', 'order_index')
        }),
        ('章节内容', {
            'fields': ('content', 'lecture_pdf'),
            'description': '章节内容使用 Markdown 编写。讲义 PDF 仅支持 PDF 格式，大小不超过 20MB。',
        }),
    )

    @admin.display(boolean=True, description='有讲义')
    def has_lecture(self, obj):
        return bool(obj.lecture_pdf)


@admin.register(Assignment)
class AssignmentAdmin(TeacherAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'semester', 'due_date', 'is_published', 'has_attachment', 'created_at')
    list_filter = ('semester', 'is_published')
    search_fields = ('title',)
    list_editable = ('is_published',)
    list_per_page = 50
    date_hierarchy = 'due_date'

    fieldsets = (
        ('基本信息', {
            'fields': ('semester', 'author', 'title', 'is_published')
        }),
        ('作业详情', {
            'fields': ('description', 'attachment', 'due_date'),
            'description': '作业附件仅支持 PDF 格式，大小不超过 20MB。',
        }),
    )

    @admin.display(boolean=True, description='有附件')
    def has_attachment(self, obj):
        return bool(obj.attachment)


@admin.register(Submission)
class SubmissionAdmin(TeacherAdminMixin, admin.ModelAdmin):
    list_display = ('student', 'assignment', 'file_name', 'is_late', 'score_display', 'scored_by_display', 'file_size_display', 'created_at')
    list_filter = ('assignment', 'is_late')
    search_fields = ('student__username', 'student__display_name', 'student__student_id')
    readonly_fields = ('file_name', 'file_size', 'created_at', 'is_late')
    list_per_page = 50

    fieldsets = (
        ('提交信息', {
            'fields': ('assignment', 'student', 'file', 'file_name', 'file_size', 'is_late', 'created_at')
        }),
        ('学生留言', {
            'fields': ('message', 'late_reason', 'score', 'feedback'),
        }),
    )

    @admin.display(description='文件大小')
    def file_size_display(self, obj):
        from .utils import format_file_size
        return format_file_size(obj.file_size)

    @admin.display(description='评分')
    def score_display(self, obj):
        if obj.score is not None:
            return f'{obj.score} 分'
        return '-'

    @admin.display(description='评分人')
    def scored_by_display(self, obj):
        if obj.scored_by:
            return obj.scored_by.display_name or obj.scored_by.username
        return '-'

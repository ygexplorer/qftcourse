"""
课程视图 — 首页、学期首页、章节详情、作业相关
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, FileResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import logging

from .models import Semester, Chapter, Assignment, Submission
from .forms import SubmissionForm
from .decorators import teacher_required, ta_required, student_required

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────
# 首页 / 学期 / 章节（第四阶段已完成）
# ──────────────────────────────────────────

def home(request):
    """课程公开首页"""
    current = Semester.objects.filter(is_current=True).first()
    semesters = Semester.objects.all()
    return render(request, 'courses/home.html', {
        'semesters': semesters,
        'current_semester': current,
    })


def semester_home(request, slug):
    """学期首页 — 展示该学期的章节列表"""
    semester = get_object_or_404(Semester, slug=slug)
    user = request.user

    if user.is_authenticated and getattr(user, 'is_teacher', False):
        chapters = semester.chapters.all()
    else:
        chapters = semester.chapters.filter(is_published=True)

    return render(request, 'courses/semester_home.html', {
        'semester': semester,
        'chapters': chapters,
    })


def chapter_detail(request, semester_slug, chapter_slug):
    """章节详情页 — Markdown 渲染"""
    chapter = get_object_or_404(
        Chapter,
        semester__slug=semester_slug,
        slug=chapter_slug,
    )

    user = request.user
    is_teacher = user.is_authenticated and getattr(user, 'is_teacher', False)

    if not chapter.is_published and not is_teacher:
        raise Http404("该章节尚未发布")

    if is_teacher:
        siblings = chapter.semester.chapters.all()
    else:
        siblings = chapter.semester.chapters.filter(is_published=True)

    chapter_list = list(siblings)
    idx = chapter_list.index(chapter)
    prev_chapter = chapter_list[idx - 1] if idx > 0 else None
    next_chapter = chapter_list[idx + 1] if idx < len(chapter_list) - 1 else None

    return render(request, 'courses/chapter_detail.html', {
        'chapter': chapter,
        'semester': chapter.semester,
        'prev_chapter': prev_chapter,
        'next_chapter': next_chapter,
        'is_draft_preview': is_teacher and not chapter.is_published,
    })


# ──────────────────────────────────────────
# 作业系统（第五阶段）
# ──────────────────────────────────────────

def _get_current_semester():
    """获取当前学期，无当前学期则返回最新学期"""
    return Semester.objects.filter(is_current=True).first() or Semester.objects.first()


@login_required
def assignment_list(request):
    """
    作业列表页
    - 学生/TA：当前学期已发布作业
    - 教师：当前学期全部作业（含未发布）
    """
    semester = _get_current_semester()
    if not semester:
        return render(request, 'courses/assignment/assignment_list.html', {
            'semester': None,
        })

    user = request.user
    is_teacher = getattr(user, 'is_teacher', False)

    if is_teacher:
        assignments = semester.assignments.all()
    else:
        assignments = semester.assignments.filter(is_published=True)

    # 预取当前用户在该作业下的提交状态
    if user.role == 'student':
        user_submissions = {
            s.assignment_id: s
            for s in Submission.objects.filter(
                assignment__in=assignments, student=user
            )
        }
    else:
        user_submissions = {}

    # TA 和教师看提交数量
    if user.role in ('ta', 'teacher'):
        from django.db.models import Count
        assignments = assignments.annotate(submission_count=Count('submissions'))

    return render(request, 'courses/assignment/assignment_list.html', {
        'semester': semester,
        'assignments': assignments,
        'user_submissions': user_submissions,
        'role': user.role,
        'now': timezone.now(),
    })


@login_required
def assignment_detail(request, pk):
    """
    作业详情页
    - 学生：作业说明 + 附件下载 + 提交/查看提交
    - TA：作业说明 + 附件下载 + 查看提交列表
    - 教师：同 TA
    """
    assignment = get_object_or_404(Assignment, pk=pk)
    user = request.user

    # 非 teacher 不能看未发布作业
    if not assignment.is_published and not getattr(user, 'is_teacher', False):
        raise Http404("该作业尚未发布")

    is_late = (
        assignment.due_date is not None
        and timezone.now() > assignment.due_date
    )

    # 学生：获取自己的提交
    if user.role == 'student':
        submission = Submission.objects.filter(
            assignment=assignment, student=user
        ).first()

        if request.method == 'POST':
            # 重新提交：先从数据库重新读取最新的 submission
            # 确保 submission.file 指向当前磁盘上的实际文件
            if submission:
                submission.refresh_from_db()

            form = SubmissionForm(
                request.POST, request.FILES,
                is_late=is_late,
            )
            if form.is_valid():
                uploaded_file = request.FILES['file']

                if submission:
                    # 重新提交 → 覆盖旧记录
                    # 第 1 步：删除旧文件（防止磁盘留下孤儿文件）
                    if submission.file and submission.file.name:
                        try:
                            old_path = submission.file.path
                            import os
                            if os.path.isfile(old_path):
                                os.remove(old_path)
                                logger.info(f"旧文件已删除: {old_path}")
                        except Exception as e:
                            logger.warning(f"旧文件删除失败（不影响新提交）: {e}")

                    # 第 2 步：更新已有记录的所有字段
                    submission.file = uploaded_file
                    submission.file_name = uploaded_file.name
                    submission.file_size = uploaded_file.size
                    submission.message = form.cleaned_data.get('message', '')
                    submission.is_late = is_late
                    submission.late_reason = form.cleaned_data.get('late_reason', '')
                    submission.save()
                else:
                    # 首次提交 → 创建新记录
                    obj = form.save(commit=False)
                    obj.assignment = assignment
                    obj.student = user
                    obj.file = uploaded_file
                    obj.file_name = uploaded_file.name
                    obj.file_size = uploaded_file.size
                    obj.is_late = is_late
                    obj.save()

                messages.success(request, '作业提交成功！')
                return redirect('courses:assignment_detail', pk=assignment.pk)
        else:
            form = SubmissionForm(is_late=is_late)

        return render(request, 'courses/assignment/assignment_detail.html', {
            'assignment': assignment,
            'submission': submission,
            'form': form,
            'is_late': is_late,
            'now': timezone.now(),
            'role': 'student',
        })

    # TA 和教师：查看所有学生提交
    elif user.role in ('ta', 'teacher'):
        submissions = assignment.submissions.select_related('student').all()
        return render(request, 'courses/assignment/assignment_detail.html', {
            'assignment': assignment,
            'submissions': submissions,
            'is_late': is_late,
            'now': timezone.now(),
            'role': user.role,
        })

    else:
        raise Http404


@login_required
def download_submission(request, pk):
    """
    下载学生提交的作业文件
    - TA 和教师可以下载所有提交
    - 学生只能下载自己的提交
    """
    submission = get_object_or_404(Submission, pk=pk)
    user = request.user

    # 权限检查：学生只能下载自己的
    if user.role == 'student' and submission.student != user:
        raise Http404("无权下载此文件")

    # 权限检查：只有 student/ta/teacher 能下载
    if user.role not in ('student', 'ta', 'teacher'):
        raise Http404

    # TA/教师检查：确认不是通过伪造 URL 访问未发布作业的提交
    if user.role in ('ta', 'teacher') and not submission.assignment.is_published:
        # 教师可以看未发布作业的提交，TA 不行
        if not getattr(user, 'is_teacher', False):
            raise Http404

    if not submission.file:
        raise Http404("文件不存在")

    response = FileResponse(
        submission.file.open('rb'),
        content_type='application/pdf',
        as_attachment=True,
        filename=submission.file_name or submission.file.name.split('/')[-1],
    )
    return response


@login_required
def download_attachment(request, pk):
    """
    下载教师上传的作业附件
    - 所有已登录用户都可以下载
    """
    assignment = get_object_or_404(Assignment, pk=pk)

    if not assignment.is_published and not getattr(request.user, 'is_teacher', False):
        raise Http404

    if not assignment.attachment:
        raise Http404("附件不存在")

    response = FileResponse(
        assignment.attachment.open('rb'),
        content_type='application/pdf',
        as_attachment=True,
        filename=assignment.attachment_filename or assignment.attachment.name.split('/')[-1],
    )
    return response

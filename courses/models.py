"""
课程核心模型 — 学期、公告、章节、作业、提交
"""

from django.db import models
from django.conf import settings


class TimeStampedModel(models.Model):
    """抽象基类：自动添加 created_at / updated_at"""

    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        abstract = True


class Semester(TimeStampedModel):
    """学期"""

    name = models.CharField('学期名称', max_length=100)
    slug = models.SlugField('URL 标识', max_length=50, unique=True)
    is_current = models.BooleanField('当前学期', default=False)
    start_date = models.DateField('开始日期', null=True, blank=True)
    end_date = models.DateField('结束日期', null=True, blank=True)

    class Meta:
        db_table = 'semesters'
        verbose_name = '学期'
        verbose_name_plural = '学期'
        ordering = ['-start_date']

    def __str__(self):
        return self.name


class Announcement(TimeStampedModel):
    """课程公告"""

    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE,
        verbose_name='所属学期', related_name='announcements'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name='发布人', limit_choices_to={'role': 'teacher'}
    )
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容', blank=True, default='')
    is_pinned = models.BooleanField('置顶', default=False)

    class Meta:
        db_table = 'announcements'
        verbose_name = '公告'
        verbose_name_plural = '公告'
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"[{self.semester.name}] {self.title}"


def chapter_lecture_path(instance, filename):
    """
    章节讲义 PDF 上传路径：lectures/ch{章节id}/原始文件名.pdf
    保留原始文件名，每章一个子目录避免同名冲突。
    """
    safe_name = filename.replace('\\', '/').split('/')[-1]
    return f'lectures/ch{instance.pk}/{safe_name}'


class Chapter(TimeStampedModel):
    """课程章节"""

    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE,
        verbose_name='所属学期', related_name='chapters'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name='编辑人', limit_choices_to={'role__in': ['teacher', 'ta']}
    )
    order_index = models.IntegerField('排序序号', default=0)
    title = models.CharField('章节标题', max_length=200)
    slug = models.SlugField('URL 标识', max_length=100, blank=True, default='')
    content = models.TextField('Markdown 内容', blank=True, default='')
    is_published = models.BooleanField('已发布', default=False)
    lecture_pdf = models.FileField(
        '讲义 PDF', upload_to=chapter_lecture_path,
        blank=True, default='',
        help_text='本章主讲义 PDF 文件（仅支持 PDF，不超过 20MB）',
    )

    class Meta:
        db_table = 'chapters'
        verbose_name = '章节'
        verbose_name_plural = '章节'
        ordering = ['order_index']
        unique_together = [['semester', 'slug']]

    def __str__(self):
        return self.title

    @property
    def lecture_pdf_filename(self):
        """返回讲义 PDF 的原始文件名"""
        if self.lecture_pdf:
            return self.lecture_pdf.name.split('/')[-1]
        return ''


# ──────────────────────────────────────────
# 作业上传路径函数（按类型/年/月分目录）
# 方便以后迁移到腾讯云 COS，只需换存储后端
# ──────────────────────────────────────────

def assignment_attachment_path(instance, filename):
    """
    教师上传的作业附件路径：assignments/2026/03/attachment_1_20260329_104530.pdf

    服务器自动重命名规则：attachment_作业ID_日期时间.pdf
    原始文件名保存在 Assignment 模型的 attachment 字段中（Django 自动记录）。
    """
    from django.utils import timezone
    now = timezone.now()
    dt_str = now.strftime('%Y%m%d_%H%M%S')
    new_filename = f"attachment_a{instance.pk}_{dt_str}.pdf"
    return f'assignments/{now.year:04d}/{now.month:02d}/{new_filename}'


def submission_file_path(instance, filename):
    """
    学生提交的作业文件路径：submissions/2026/03/username_a1_20260329_104530.pdf

    服务器自动重命名规则：用户名_作业ID_提交日期时间.pdf
    原始文件名保存在 Submission.file_name 字段，方便教师查看。
    """
    from django.utils import timezone
    now = timezone.now()
    dt_str = now.strftime('%Y%m%d_%H%M%S')
    safe_name = instance.student.username
    safe_title = f"a{instance.assignment.pk}"
    new_filename = f"{safe_name}_{safe_title}_{dt_str}.pdf"
    return f'submissions/{now.year:04d}/{now.month:02d}/{new_filename}'


class Assignment(TimeStampedModel):
    """作业"""

    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE,
        verbose_name='所属学期', related_name='assignments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name='发布人', limit_choices_to={'role': 'teacher'}
    )
    title = models.CharField('作业标题', max_length=200)
    description = models.TextField('作业要求', blank=True, default='')
    attachment = models.FileField(
        '作业附件（PDF）', upload_to=assignment_attachment_path,
        blank=True, default='',
        help_text='教师上传的作业题目 PDF'
    )
    due_date = models.DateTimeField('截止时间', null=True, blank=True)
    is_published = models.BooleanField('已发布', default=False)

    class Meta:
        db_table = 'assignments'
        verbose_name = '作业'
        verbose_name_plural = '作业'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.semester.name}] {self.title}"

    @property
    def attachment_filename(self):
        """返回附件的原始文件名"""
        if self.attachment:
            return self.attachment.name.split('/')[-1]
        return ''


class Submission(TimeStampedModel):
    """作业提交记录"""

    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE,
        verbose_name='所属作业', related_name='submissions'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name='提交学生', related_name='submissions',
        limit_choices_to={'role': 'student'}
    )
    file = models.FileField('作业文件（PDF）', upload_to=submission_file_path)
    file_name = models.CharField('原始文件名', max_length=255, blank=True)
    file_size = models.BigIntegerField('文件大小(bytes)', default=0)
    message = models.TextField('留言/备注', blank=True, default='')
    is_late = models.BooleanField('是否逾期', default=False)
    late_reason = models.TextField('逾期原因', blank=True, default='')
    score = models.IntegerField('评分', null=True, blank=True)
    feedback = models.TextField('评语', blank=True, default='')
    scored_at = models.DateTimeField('评分时间', null=True, blank=True)
    scored_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='评分人',
        limit_choices_to={'role__in': ['teacher', 'ta']},
        related_name='graded_submissions',
    )

    class Meta:
        db_table = 'submissions'
        verbose_name = '作业提交'
        verbose_name_plural = '作业提交'
        ordering = ['-created_at']
        unique_together = [['assignment', 'student']]

    def __str__(self):
        return f"{self.student.display_name} → {self.assignment.title}"

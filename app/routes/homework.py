import os
from datetime import timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory
from flask_login import login_required, current_user
from app.models.chapter import Chapter, Assignment, Submission, Grade
from app import db
from werkzeug.utils import secure_filename

homework_bp = Blueprint('homework', __name__)

ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_valid_pdf(file_stream):
    """通过文件头部 magic bytes 验证是否为真正的 PDF 文件"""
    header = file_stream.read(5)
    file_stream.seek(0)  # 重置读取位置
    return header == b'%PDF-'


@homework_bp.route('/')
@login_required
def index():
    """学生作业列表 - 显示所有章节的作业"""
    chapters = Chapter.query.filter_by(is_visible=True).order_by(Chapter.number).all()
    # 获取当前学生已提交的作业
    my_submissions = {}
    if not current_user.is_staff():
        for s in Submission.query.filter_by(student_id=current_user.id).all():
            my_submissions[s.assignment_id] = s
    return render_template('homework/index.html', chapters=chapters, my_submissions=my_submissions)


@homework_bp.route('/submit/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def submit(assignment_id):
    """学生提交作业"""
    if current_user.is_staff():
        flash('教师和助教账号无需提交作业。', 'error')
        return redirect(url_for('homework.index'))

    assignment = Assignment.query.get_or_404(assignment_id)

    # 检查作业是否已关闭（已过期或非活跃）
    if not assignment.is_active:
        flash('该作业已关闭，无法提交。', 'error')
        return redirect(url_for('homework.index'))
    from datetime import datetime
    if assignment.due_date and datetime.now(assignment.due_date.tzinfo or timezone.utc) > assignment.due_date:
        flash('该作业已过截止日期，无法提交。', 'error')
        return redirect(url_for('homework.index'))

    # 检查是否已提交
    existing = Submission.query.filter_by(
        assignment_id=assignment_id,
        student_id=current_user.id
    ).first()

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('请选择文件上传。', 'error')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('未选择文件。', 'error')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash('仅支持 PDF 格式文件。', 'error')
            return redirect(request.url)

        if not is_valid_pdf(file.stream):
            flash('文件不是有效的 PDF 格式。', 'error')
            return redirect(request.url)

        from datetime import date
        import re
        filename = secure_filename(file.filename)
        # 命名规则：姓名_第X章_日期.pdf（姓名中的特殊字符替换为下划线）
        ch_num = assignment.chapter.number
        today = date.today().strftime('%Y%m%d')
        ext = os.path.splitext(filename)[1]
        safe_name = f"{re.sub(r'[^\w\u4e00-\u9fff]', '_', current_user.name)}_第{ch_num}章_{today}{ext}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], safe_name)
        file.save(filepath)

        file_size = os.path.getsize(filepath)

        if existing:
            # 覆盖已有提交，删除旧文件
            old_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], existing.filepath)
            if os.path.exists(old_filepath):
                os.remove(old_filepath)
            existing.filename = safe_name
            existing.filepath = safe_name
            existing.file_size = file_size
            existing.score = None  # 重新提交，清除之前分数
            # 同步清除 Grade 表中的成绩
            grade = Grade.query.filter_by(
                student_id=current_user.id,
                chapter_id=assignment.chapter_id
            ).first()
            if grade:
                grade.score = None
            db.session.commit()
            flash('作业已更新提交！', 'success')
        else:
            submission = Submission(
                assignment_id=assignment_id,
                student_id=current_user.id,
                filename=safe_name,
                filepath=safe_name,
                file_size=file_size
            )
            db.session.add(submission)
            db.session.commit()
            flash('作业提交成功！', 'success')

        return redirect(url_for('homework.index'))

    return render_template('homework/submit.html', assignment=assignment, existing=existing)


@homework_bp.route('/download/<int:submission_id>')
@login_required
def download(submission_id):
    """下载作业文件（教师和学生都可以下载自己的）"""
    submission = Submission.query.get_or_404(submission_id)
    if not current_user.is_staff() and submission.student_id != current_user.id:
        flash('无权访问该文件。', 'error')
        return redirect(url_for('homework.index'))

    upload_dir = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(
        upload_dir, submission.filepath,
        as_attachment=True, download_name=submission.filename
    )


@homework_bp.route('/grades')
@login_required
def my_grades():
    """学生个人成绩汇总"""
    if current_user.is_staff():
        return redirect(url_for('admin.grades'))

    chapters = Chapter.query.filter_by(is_visible=True).order_by(Chapter.number).all()
    submissions = Submission.query.filter_by(student_id=current_user.id).all()

    # 按章节组织提交信息
    submission_map = {}
    for s in submissions:
        ch_id = s.assignment.chapter_id
        submission_map[ch_id] = s

    # 获取教师录入的成绩
    grades = Grade.query.filter_by(student_id=current_user.id).all()
    grade_map = {}
    for g in grades:
        grade_map[g.chapter_id] = g

    return render_template('homework/grades.html',
                           chapters=chapters,
                           submission_map=submission_map,
                           grade_map=grade_map)

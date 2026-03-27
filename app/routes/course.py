from flask import Blueprint, render_template, abort
from flask_login import current_user
from app.models.chapter import Chapter

course_bp = Blueprint('course', __name__)


@course_bp.route('/')
def index():
    chapters = Chapter.query.filter_by(is_visible=True).order_by(Chapter.number).all()
    return render_template('course/index.html', chapters=chapters)


@course_bp.route('/<slug>')
def chapter(slug):
    chapter = Chapter.query.filter_by(slug=slug).first_or_404()
    if not chapter.is_visible and (not current_user.is_authenticated or not current_user.is_staff()):
        abort(404)

    # 所有可见章节（用于侧边栏）
    all_chapters = Chapter.query.filter_by(is_visible=True).order_by(Chapter.number).all()

    # 获取上一篇和下一章
    prev_ch = Chapter.query.filter(Chapter.number < chapter.number, Chapter.is_visible == True)\
                           .order_by(Chapter.number.desc()).first()
    next_ch = Chapter.query.filter(Chapter.number > chapter.number, Chapter.is_visible == True)\
                           .order_by(Chapter.number.asc()).first()

    return render_template('course/chapter.html', chapter=chapter, prev_ch=prev_ch, next_ch=next_ch,
                           all_chapters=all_chapters)

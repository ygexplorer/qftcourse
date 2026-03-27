from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.announcement import Announcement

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    from app.models.chapter import Chapter
    chapters = Chapter.query.filter_by(is_visible=True).order_by(Chapter.number).all()
    # 获取活跃公告（置顶优先，最多5条）
    announcements = Announcement.query.filter_by(is_active=True).order_by(
        Announcement.is_pinned.desc(),
        Announcement.created_at.desc()
    ).limit(5).all()
    return render_template('main/index.html', chapters=chapters, announcements=announcements)


@main_bp.route('/announcements')
def announcement_list():
    """查看所有公告"""
    announcements = Announcement.query.filter_by(is_active=True).order_by(
        Announcement.is_pinned.desc(),
        Announcement.created_at.desc()
    ).all()
    return render_template('main/announcements.html', announcements=announcements)


@main_bp.route('/announcements/<int:announcement_id>')
def announcement_detail(announcement_id):
    """查看公告详情"""
    announcement = Announcement.query.get_or_404(announcement_id)
    if not announcement.is_active and not (current_user.is_authenticated and current_user.is_staff()):
        flash('该公告不存在。', 'error')
        return redirect(url_for('main.index'))
    return render_template('main/announcement_detail.html', announcement=announcement)


@main_bp.route('/about')
def about():
    return render_template('main/about.html')


@main_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """修改密码（所有用户通用）"""
    if request.method == 'POST':
        old_pwd = request.form.get('old_password', '')
        new_pwd = request.form.get('new_password', '')
        confirm_pwd = request.form.get('confirm_password', '')

        if not old_pwd or not new_pwd or not confirm_pwd:
            flash('请填写所有字段。', 'error')
            return redirect(request.url)

        if not current_user.check_password(old_pwd):
            flash('当前密码不正确。', 'error')
            return redirect(request.url)

        if len(new_pwd) < 6:
            flash('新密码至少 6 位。', 'error')
            return redirect(request.url)

        if new_pwd != confirm_pwd:
            flash('两次输入的新密码不一致。', 'error')
            return redirect(request.url)

        current_user.set_password(new_pwd)
        db.session.commit()
        flash('密码修改成功。', 'success')
        # 返回到用户各自的首页
        if current_user.is_staff():
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.index'))

    return render_template('main/change_password.html')


import re
import html


@main_bp.route('/search')
def search():
    """全站搜索 API：搜索章节标题和内容"""
    q = request.args.get('q', '').strip()
    if not q or len(q) < 1:
        return jsonify([])

    from app.models.chapter import Chapter
    chapters = Chapter.query.filter_by(is_visible=True).order_by(Chapter.number).all()

    results = []
    keywords = q.lower().split()

    for ch in chapters:
        # 去掉 HTML 标签和公式分隔符，提取纯文本
        plain_text = ch.content or ''
        plain_text = html.unescape(plain_text)
        plain_text = re.sub(r'<[^>]+>', ' ', plain_text)       # 去掉 HTML 标签
        plain_text = re.sub(r'\$\$.*?\$\$', ' ', plain_text, flags=re.DOTALL)  # 去掉 display 公式
        plain_text = re.sub(r'\$[^$]+\$', ' ', plain_text)      # 去掉 inline 公式
        plain_text = re.sub(r'\\\([^)]*\\\)', ' ', plain_text)   # 去掉 \( \) 公式
        plain_text = re.sub(r'\\\[[^\]]*\\\]', ' ', plain_text)  # 去掉 \[ \] 公式
        plain_text = re.sub(r'\s+', ' ', plain_text).strip()     # 合并空白
        plain_text = re.sub(r'[*_`#>~|]', '', plain_text)       # 去掉 Markdown 标记
        text_lower = plain_text.lower()
        title_lower = ch.title.lower()

        # 匹配标题
        title_matched = all(kw in title_lower for kw in keywords)

        # 匹配内容
        if title_matched:
            content_matched = True
            snippet = ''
        else:
            content_matched = all(kw in text_lower for kw in keywords)
            snippet = ''
            if content_matched:
                # 找到第一个关键词的位置，提取上下文
                first_pos = len(plain_text)
                for kw in keywords:
                    pos = text_lower.find(kw)
                    if pos != -1 and pos < first_pos:
                        first_pos = pos
                start = max(0, first_pos - 60)
                end = min(len(plain_text), first_pos + 120)
                snippet = ('...' if start > 0 else '') + plain_text[start:end] + ('...' if end < len(plain_text) else '')

        if title_matched or content_matched:
            results.append({
                'title': ch.title,
                'number': ch.number,
                'url': url_for('course.chapter', slug=ch.slug),
                'snippet': snippet,
                'title_matched': title_matched
            })

    return jsonify(results[:20])

"""
初始化课程数据：将章节信息导入数据库
"""
import os
import sys

# 将项目根目录加入路径
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

from app import create_app, db
from app.models.chapter import Chapter
from app.models.user import User


# 14 章课程基本信息
CHAPTERS = [
    (1, '基础回顾', 'chapter01'),
    (2, '路径积分量子化', 'chapter02'),
    (3, '规范场基础', 'chapter03'),
    (4, '规范场的量子化', 'chapter04'),
    (5, '费曼图计算基础', 'chapter05'),
    (6, '圈图计算简介', 'chapter06'),
    (7, '场论中的对称性', 'chapter07'),
    (8, '对称性的破缺 — 概述', 'chapter08'),
    (9, '对称性的自发破缺', 'chapter09'),
    (10, '重整化', 'chapter10'),
    (11, '重整化群', 'chapter11'),
    (12, '反常', 'chapter12'),
    (13, '规范-引力之联系', 'chapter13'),
    (14, 'S矩阵方法', 'chapter14'),
]


def init_chapters():
    """初始化章节数据"""
    app = create_app()

    with app.app_context():
        # 检查是否已有数据
        if Chapter.query.count() > 0:
            print(f"数据库中已有 {Chapter.query.count()} 个章节，跳过初始化。")
            return

        for number, title, slug in CHAPTERS:
            chapter = Chapter(
                number=number,
                title=title,
                slug=slug,
                sort_order=number,
                is_visible=True
            )
            db.session.add(chapter)

        db.session.commit()
        print(f"已初始化 {len(CHAPTERS)} 个章节。")


def import_chapter_content():
    """
    将 docsify 版本的课程 Markdown 内容导入到数据库。
    Markdown 内容会被存为原始文本，前端用 |safe 直接渲染。
    """
    app = create_app()
    docsify_dir = os.path.join(BASE_DIR, 'gauge-theory-course', 'lectures')

    # Docsify Markdown → HTML 简单转换器
    def md_to_html(md_text):
        """简单的 Markdown 到 HTML 转换（去除 Docsify 特有语法）"""
        import re
        from markupsafe import escape

        def escape_line(text):
            """转义 HTML 特殊字符，但保留 LaTeX 公式"""
            # 保护 LaTeX 公式不被转义：先提取，转义其余部分，再还原
            # 行间公式 $$...$$
            parts = re.split(r'(\$\$.+?\$\$)', text)
            result = []
            for part in parts:
                if part.startswith('$$') and part.endswith('$$'):
                    result.append(part)
                else:
                    # 行内公式 $...$（非 $$ 开头的）
                    sub_parts = re.split(r'(\$[^$]+?\$)', part)
                    for sp in sub_parts:
                        if sp.startswith('$') and sp.endswith('$') and len(sp) > 2:
                            result.append(sp)
                        else:
                            result.append(escape(sp))
            return ''.join(result)

        lines = md_text.split('\n')
        html_lines = []
        in_table = False
        in_code_block = False

        for line in lines:
            # 代码块
            if line.strip().startswith('```'):
                if in_code_block:
                    html_lines.append('</code></pre>')
                    in_code_block = False
                else:
                    html_lines.append('<pre><code>')
                    in_code_block = True
                continue

            if in_code_block:
                # 代码块内容只做最基础的转义
                html_lines.append(escape(line) if line.strip() else '')
                continue

            # 去掉 Docsify 专有语法（!!! 开头的提示框）
            if line.strip().startswith('!!!'):
                m = re.match(r'!!!\s*(info|warning|danger|tip|abstract|quote)?\s*["\']?(.*?)["\']?\s*$', line.strip())
                if m:
                    ctype = m.group(1) or 'info'
                    title = m.group(2)
                    type_map = {
                        'info': ('ℹ️', '#eff6ff', '#3b82f6'),
                        'warning': ('⚠️', '#fffbeb', '#f59e0b'),
                        'danger': ('🚫', '#fef2f2', '#ef4444'),
                        'tip': ('💡', '#ecfdf5', '#10b981'),
                        'abstract': ('📋', '#f0f9ff', '#0ea5e9'),
                        'quote': ('💬', '#f0fdf4', '#22c55e'),
                    }
                    icon, bg, border = type_map.get(ctype, type_map['info'])
                    html_lines.append(f'<blockquote style="border-left:4px solid {border}; background:{bg}; padding:12px 16px; border-radius:0 8px 8px 0;">')
                    if title:
                        html_lines.append(f'<strong>{icon} {escape(title)}</strong><br>')
                continue

            # 去掉 [[]] 内部链接语法，保留文字
            line = re.sub(r'\[\[(.+?)\]\]', r'\1', line)

            # 关闭 blockquote（遇到空行或新标题时）
            if line.strip() == '' or line.startswith('#'):
                if html_lines and html_lines[-1].startswith('<blockquote'):
                    pass  # blockquote 内容继续

            # 标题
            if line.startswith('####'):
                text = escape_line(line[4:].strip())
                html_lines.append(f'<h4>{text}</h4>')
            elif line.startswith('###'):
                text = escape_line(line[3:].strip())
                html_lines.append(f'<h3>{text}</h3>')
            elif line.startswith('##'):
                text = escape_line(line[2:].strip())
                html_lines.append(f'<h2>{text}</h2>')
            elif line.startswith('#'):
                # 跳过页面主标题，避免和页面标题重复
                continue

            # 分隔线
            elif line.strip() == '---':
                html_lines.append('<hr>')

            # 表格
            elif '|' in line and line.strip().startswith('|'):
                if re.match(r'^\|[\s\-:|]+\|$', line.strip()):
                    continue
                cells = [escape(c.strip()) for c in line.strip().split('|')[1:-1]]
                if not in_table:
                    html_lines.append('<table>')
                    in_table = True
                if html_lines[-1] == '<table>':
                    html_lines.append('<thead><tr>')
                    for cell in cells:
                        html_lines.append(f'<th>{cell}</th>')
                    html_lines.append('</tr></thead><tbody>')
                else:
                    html_lines.append('<tr>')
                    for cell in cells:
                        html_lines.append(f'<td>{cell}</td>')
                    html_lines.append('</tr>')
            else:
                if in_table and not line.strip().startswith('|'):
                    html_lines.append('</tbody></table>')
                    in_table = False

                # 引用
                if line.strip().startswith('>'):
                    text = escape_line(line.strip()[1:].strip())
                    html_lines.append(f'<blockquote>{text}</blockquote>')
                # 列表
                elif re.match(r'^\s*[-*]\s+', line):
                    text = escape_line(re.sub(r'^\s*[-*]\s+', '', line))
                    html_lines.append(f'<li>{text}</li>')
                elif re.match(r'^\s*\d+\.\s+', line):
                    text = escape_line(re.sub(r'^\s*\d+\.\s+', '', line))
                    html_lines.append(f'<li>{text}</li>')
                # 段落
                elif line.strip():
                    line = escape_line(line)
                    # 简单处理行内加粗和斜体（在已转义的文本上操作）
                    line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
                    line = re.sub(r'\*(.+?)\*', r'<em>\1</em>', line)
                    html_lines.append(f'<p>{line}</p>')
                else:
                    html_lines.append('<br>')

        if in_table:
            html_lines.append('</tbody></table>')

        return '\n'.join(html_lines)

    with app.app_context():
        if not os.path.exists(docsify_dir):
            print(f"Docsify 课程目录不存在: {docsify_dir}")
            return

        imported = 0
        for filename in sorted(os.listdir(docsify_dir)):
            if not filename.endswith('.md'):
                continue

            # 从文件名提取章节号
            m = re.match(r'chapter(\d+)', filename)
            if not m:
                continue

            chapter_num = int(m.group(1))
            chapter = Chapter.query.filter_by(number=chapter_num).first()
            if not chapter:
                print(f"  跳过：未找到第 {chapter_num} 章的数据库记录")
                continue

            filepath = os.path.join(docsify_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                md_content = f.read()

            if chapter.content and chapter.content.strip():
                print(f"  第 {chapter_num} 章已有内容，跳过")
                continue

            # 转换 Markdown 到 HTML
            html_content = md_to_html(md_content)
            chapter.content = html_content
            imported += 1
            print(f"  ✓ 第 {chapter_num} 章：{chapter.title}")

        if imported > 0:
            db.session.commit()
            print(f"\n成功导入 {imported} 个章节的内容。")
        else:
            print("\n没有需要导入的章节内容。")


if __name__ == '__main__':
    import re
    print("=== 初始化章节数据 ===")
    init_chapters()
    print("\n=== 导入课程内容 ===")
    import_chapter_content()
    print("\n完成！")

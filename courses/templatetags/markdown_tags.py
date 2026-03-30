"""
自定义模板标签 — Markdown 渲染 + 辅助过滤器
"""

import re
import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='markdown')
def markdown_filter(text):
    """将 Markdown 文本转为 HTML（安全输出）"""
    if not text:
        return ''
    html = markdown.markdown(
        text,
        extensions=['fenced_code', 'tables', 'toc'],
    )
    return mark_safe(html)


@register.filter(name='extract_toc')
def extract_toc_filter(text):
    """
    从 Markdown 原文提取 H2 和 H3 标题，返回目录列表。

    返回格式：
    [
        {'level': 2, 'id': 'heading-1', 'title': '标题文本'},
        {'level': 3, 'id': 'heading-2', 'title': '子标题文本'},
        ...
    ]
    """
    if not text:
        return []

    toc = []
    counter = 0
    for line in text.split('\n'):
        line = line.rstrip()
        # 匹配 ## H2 或 ### H3
        m = re.match(r'^(#{2,3})\s+(.+)$', line)
        if m:
            counter += 1
            level = len(m.group(1))
            title = m.group(2).strip()
            # 去掉标题末尾可能的链接引用，如 "[^1]"
            title = re.sub(r'\s*\[.*?\]\s*$', '', title)
            toc.append({
                'level': level,
                'id': f'heading-{counter}',
                'title': title,
            })
    return toc


@register.filter(name='inject_heading_ids', needs_autoescape=False)
def inject_heading_ids_filter(html):
    """
    给渲染后的 HTML 中的 H2 和 H3 标签注入 id 属性。

    强制覆盖 markdown toc 扩展自动生成的 id，确保与 extract_toc 一致。
    """
    if not html:
        return html

    counter = 0

    def _replacer(match):
        nonlocal counter
        counter += 1
        heading_id = f'heading-{counter}'
        tag = match.group(1)  # 'h2' or 'h3'
        attrs = match.group(2) or ''
        content = match.group(3)
        # 移除已有的 id 属性，统一替换
        attrs = re.sub(r'\s*id="[^"]*"', '', attrs)
        return f'<{tag} id="{heading_id}"{attrs}>{content}</{tag}>'

    result = re.sub(
        r'<(h[23])(\s[^>]*)?>(.*?)</\1>',
        _replacer,
        html,
        flags=re.DOTALL,
    )
    return mark_safe(result)


@register.filter(name='filesize')
def filesize_filter(value):
    """将字节数转为人类可读格式"""
    try:
        size = int(value)
    except (ValueError, TypeError):
        return '0 B'

    if size < 1024:
        return f'{size} B'
    elif size < 1024 * 1024:
        return f'{size / 1024:.1f} KB'
    elif size < 1024 * 1024 * 1024:
        return f'{size / (1024 * 1024):.1f} MB'
    else:
        return f'{size / (1024 * 1024 * 1024):.1f} GB'


@register.filter
def get_item(dictionary, key):
    """从字典中取值（用于模板中 {{ mydict|get_item:key }}）"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter(name='graded_count')
def graded_count_filter(queryset_or_list):
    """统计已评分的提交数量"""
    try:
        return sum(1 for s in queryset_or_list if s.score is not None)
    except (TypeError, AttributeError):
        return 0


@register.filter(name='make_initial')
def make_initial_filter(name):
    """从姓名中取第一个字作为头像字母"""
    if not name:
        return '?'
    return name.strip()[0]

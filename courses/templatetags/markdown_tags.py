"""
自定义模板标签 — Markdown 渲染 + 辅助过滤器
"""

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

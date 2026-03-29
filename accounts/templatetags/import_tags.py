"""自定义模板标签 — 导入相关辅助过滤器"""

from django import template

register = template.Library()


@register.filter(name='last6')
def last6_filter(value):
    """取字符串后 6 位（用于显示学号后6位初始密码）"""
    s = str(value)
    return s[-6:] if len(s) >= 6 else s

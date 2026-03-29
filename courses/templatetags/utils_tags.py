"""通用模板过滤器"""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """字典按 key 取值，用于模板中 {{ dict|get_item:key }}"""
    if dictionary is None:
        return None
    return dictionary.get(str(key))

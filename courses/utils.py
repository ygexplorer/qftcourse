"""
文件上传辅助函数

前后端都做校验：
- 前端：HTML accept 属性 + JS 校验
- 后端：Django Form validate + 此模块的扩展名/MIME/大小校验
"""

from django.core.exceptions import ValidationError

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'pdf'}

# 文件大小限制
MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20MB


def validate_pdf(value):
    """
    校验上传文件是否为 PDF 且大小不超过 20MB。
    在 Django Form 的 validators 中使用。
    """
    if not value:
        return

    # 检查扩展名
    ext = value.name.rsplit('.', 1)[-1].lower() if '.' in value.name else ''
    if ext != 'pdf':
        raise ValidationError('只支持 PDF 文件，请上传 .pdf 格式。')

    # 检查 MIME type（后端双重校验）
    if hasattr(value, 'content_type'):
        if value.content_type and not value.content_type.startswith('application/pdf'):
            raise ValidationError(f'文件类型不正确（检测到 {value.content_type}），请上传 PDF。')

    # 检查空文件
    if value.size == 0:
        raise ValidationError('上传的文件为空，请检查后重新上传。')

    # 检查文件大小（20MB 限制）
    if value.size > MAX_UPLOAD_SIZE:
        raise ValidationError(f'文件大小不能超过 20MB，当前文件为 {format_file_size(value.size)}，请压缩后重新上传。')


def format_file_size(size_bytes):
    """将字节数转为人类可读格式"""
    if size_bytes < 1024:
        return f'{size_bytes} B'
    elif size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.1f} KB'
    elif size_bytes < 1024 * 1024 * 1024:
        return f'{size_bytes / (1024 * 1024):.1f} MB'
    else:
        return f'{size_bytes / (1024 * 1024 * 1024):.1f} GB'

"""
中间件 — 将教师/管理员角色的 is_staff 自动同步为 True

放在 AuthenticationMiddleware 之后，确保 request.user 已就绪。
仅做内存级修正，不写数据库（数据库由信号保证）。
"""


class SyncStaffMiddleware:
    """每次请求时，确保教师和管理员的 request.user.is_staff 为 True。"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated and not user.is_superuser:
            if user.role in ('teacher', 'admin') and not user.is_staff:
                # 内存级修正，不写数据库（信号会在 save 时持久化）
                user.is_staff = True
        return self.get_response(request)

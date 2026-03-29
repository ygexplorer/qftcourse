"""根 URL 路由"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('courses.urls')),
    path('accounts/', include('accounts.urls')),
]

# 开发环境：由 Django 直接提供 media 文件服务
# 生产环境：由 Nginx 提供静态文件服务，不需要此配置
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

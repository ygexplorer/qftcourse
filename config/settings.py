"""
规范场课程网站 — Django 配置
"""

import os
from pathlib import Path

# ──────────────────────────────────────────
# 基础路径
# ──────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ──────────────────────────────────────────
# 从 .env 文件加载环境变量（生产环境用）
# ──────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')

# ──────────────────────────────────────────
# 安全配置
# ──────────────────────────────────────────
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-dev-key-do-not-use-in-production-!!change-me!!'
)

DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',') if os.environ.get('ALLOWED_HOSTS') else ['*']

# CSRF 信任来源（生产环境通过 .env 配置，否则可能阻止表单提交）
CSRF_TRUSTED_ORIGINS = os.environ.get(
    'CSRF_TRUSTED_ORIGINS', ''
).split(',') if os.environ.get('CSRF_TRUSTED_ORIGINS') else []

# ──────────────────────────────────────────
# 应用注册
# ──────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 我们的应用
    'accounts',
    'courses',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'accounts.middleware.SyncStaffMiddleware',  # 教师/管理员自动获得 is_staff
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # 全局模板目录
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ──────────────────────────────────────────
# 数据库
#   开发环境用 SQLite，生产环境用 PostgreSQL
# ──────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),
    }
}

# ──────────────────────────────────────────
# 密码验证（开发时放宽，生产时可收紧）
# ──────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
]

# ──────────────────────────────────────────
# 国际化
# ──────────────────────────────────────────
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# ──────────────────────────────────────────
# 静态文件 & 上传文件
# ──────────────────────────────────────────
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # collectstatic 收集目标
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # 项目根目录 static/ 目录（favicon 等）
]

MEDIA_URL = 'media/'
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', str(BASE_DIR / 'media'))

# 文件上传限制
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB，超过则写入临时文件
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB

# ──────────────────────────────────────────
# 登录 / 登出配置
# ──────────────────────────────────────────
LOGIN_URL = 'accounts:login'          # 未登录时跳转到登录页（用 URL name，Django 会自动反转）
LOGIN_REDIRECT_URL = 'accounts:dashboard'  # 登录成功后跳转到仪表盘（按角色再跳转）
LOGOUT_REDIRECT_URL = '/'                  # 登出后回到首页

# ──────────────────────────────────────────
# 自定义用户模型
# ──────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.User'

# ──────────────────────────────────────────
# 默认主键类型
# ──────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

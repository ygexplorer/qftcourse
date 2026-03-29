# 部署指南 — 腾讯云 CVM (Ubuntu 22.04)

> 面向新手：假设你不熟悉 Linux 服务器操作，按步骤跟着做就行。

## 前置准备：去腾讯云确认什么信息

在动手之前，请先确认以下信息：

| 信息 | 在哪里看 | 用途 |
|------|----------|------|
| 服务器公网 IP | 腾讯云控制台 → 云服务器 → 实例列表 | SSH 登录、域名解析 |
| 服务器 root 密码或 SSH 密钥 | 创建服务器时设置的 | 登录服务器 |
| 域名 | 腾讯云控制台 → 域名注册 | HTTPS 访问 |
| 备案状态 | 腾讯云控制台 → 网站备案 | 国内服务器必须备案才能绑域名 |

**注意**：如果域名还没备案，可以先用 IP 地址 + 端口访问测试，备案完成后再绑域名。

## 本地 vs 生产环境对比

| 配置项 | 本地开发 | 腾讯云生产 |
|--------|----------|------------|
| DEBUG | True | **False** |
| 数据库 | SQLite | **PostgreSQL** |
| 静态文件 | Django 直接服务 | **Nginx 服务** |
| 上传文件 | Django 直接服务 | **Nginx 服务** |
| Web 服务器 | `runserver` | **Gunicorn + Nginx** |
| HTTPS | 无 | **Nginx + Let's Encrypt** |
| ALLOWED_HOSTS | `localhost,127.0.0.1` | **域名,IP** |
| CSRF_TRUSTED_ORIGINS | 空 | **https://你的域名** |
| SECRET_KEY | 开发用的固定值 | **随机生成** |

## 为什么用 Gunicorn + Nginx？

**Gunicorn** 是 Python WSGI 服务器：
- `python manage.py runserver` 是单线程开发服务器，**不适合生产**
- Gunicorn 可以同时处理多个请求，支持多 worker 进程
- 它是 Django 官方推荐的生产 WSGI 服务器

**Nginx** 是反向代理：
- Gunicorn 不直接对外暴露，Nginx 在前面接收用户请求
- Nginx 擅长：静态文件服务、HTTPS 终端、负载均衡、安全防护
- Nginx 把动态请求转发给 Gunicorn，自己处理静态文件（更快）

```
用户浏览器 → Nginx (80/443端口)
                ├── 静态文件 → 直接返回 (CSS/JS/图片)
                ├── 媒体文件 → 直接返回 (PDF上传/下载)
                └── 动态请求 → Gunicorn (本地8000端口) → Django
```

## 部署步骤

### 第一步：连接服务器

```bash
# 在本地终端执行（macOS 自带 ssh）
ssh root@你的服务器IP

# 首次连接会问 yes/no，输入 yes
# 然后输入 root 密码
```

### 第二步：系统更新

```bash
apt update && apt upgrade -y
```

### 第三步：安装软件

```bash
# Python 3.12 + pip + venv
apt install -y python3.12 python3.12-venv python3-pip

# PostgreSQL 数据库
apt install -y postgresql postgresql-contrib

# Nginx
apt install -y nginx

# 其他工具
apt install -y curl git
```

### 第四步：配置 PostgreSQL

```bash
# 切换到 postgres 用户
sudo -u postgres psql

# 在 PostgreSQL 命令行中执行：
CREATE DATABASE qft_course;
CREATE USER qft_user WITH PASSWORD '你的数据库密码';
GRANT ALL PRIVILEGES ON DATABASE qft_course TO qft_user;
\q
```

### 第五步：部署代码

```bash
# 创建项目目录
mkdir -p /opt/qft-course
cd /opt/qft-course

# 克隆代码（用 HTTPS 方式，或配置 SSH key）
git clone https://github.com/your-username/qft-course.git .

# 创建虚拟环境
python3.12 -m venv venv
source venv/bin/activate

# 安装依赖（取消 psycopg2-binary 的注释）
# 先编辑 requirements.txt，取消 psycopg2-binary 那行的注释
pip install -r requirements.txt
```

### 第六步：配置生产环境变量

```bash
# 复制模板
cp .env.example .env

# 编辑 .env（用 nano 编辑器）
nano .env
```

`.env` 生产配置示例：

```env
SECRET_KEY=用python生成的随机密钥填这里
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,你的服务器IP
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

DB_ENGINE=django.db.backends.postgresql
DB_NAME=qft_course
DB_USER=qft_user
DB_PASSWORD=你的数据库密码
DB_HOST=localhost
DB_PORT=5432

MEDIA_ROOT=/opt/qft-course/media/
```

生成 SECRET_KEY：

```bash
source venv/bin/activate
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 第七步：数据库迁移 + 收集静态文件

```bash
source venv/bin/activate

# 创建数据库表
python manage.py migrate

# 创建管理员账号
python manage.py createsuperuser

# 收集静态文件（Nginx 需要直接服务这些文件）
python manage.py collectstatic
```

### 第八步：配置 Gunicorn systemd 服务

创建服务文件：

```bash
nano /etc/systemd/system/qft-course.service
```

内容：

```ini
[Unit]
Description=Gunicorn daemon for QFT Course
After=network.target postgresql.service

[Service]
User=root
Group=root
WorkingDirectory=/opt/qft-course
ExecStart=/opt/qft-course/venv/bin/gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 3 \
    config.wsgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启用并启动：

```bash
systemctl daemon-reload
systemctl enable qft-course
systemctl start qft-course

# 检查是否运行成功
systemctl status qft-course
```

### 第九步：配置 Nginx

```bash
nano /etc/nginx/sites-available/qft-course
```

内容：

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com 你的服务器IP;

    # 静态文件
    location /static/ {
        alias /opt/qft-course/staticfiles/;
        expires 30d;
    }

    # 上传文件（PDF 等）
    location /media/ {
        alias /opt/qft-course/media/;
        # ⚠️ 重要：Nginx 也需要设置上传大小限制，否则 20MB 以上的文件会被拦截
        client_max_body_size 25M;
    }

    # 动态请求转发给 Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：

```bash
ln -s /etc/nginx/sites-available/qft-course /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default   # 删除默认配置

# 测试配置是否正确
nginx -t

# 重载 Nginx
systemctl reload nginx
```

### 第十步：HTTPS 证书（域名备案后）

```bash
# 安装 certbot
apt install -y certbot python3-certbot-nginx

# 申请证书（自动配置 Nginx）
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 第十一步：开放防火墙端口

```bash
# 腾讯云控制台 → 安全组 → 添加规则
# 开放端口：80 (HTTP)、443 (HTTPS)
# 不需要开放 8000 端口（Gunicorn 只监听本地）
```

## 20MB 上传限制：Nginx 和 Django 的关系

**Django 后端**已经限制了 20MB：
- `courses/utils.py` 中的 `MAX_UPLOAD_SIZE = 20 * 1024 * 1024`
- `settings.py` 中的 `FILE_UPLOAD_MAX_MEMORY_SIZE = 50MB`

**Nginx 也需要配置**，因为 Nginx 是第一道关卡：
- 默认 Nginx 只允许上传 1MB
- 如果不配置，用户上传 20MB 的 PDF 时，**Nginx 会直接返回 413 错误**，请求根本到不了 Django
- 所以 Nginx 配置中 `client_max_body_size` 要设为 **略大于** 20MB（建议 25M）

三道关卡的关系：

```
浏览器 (JS 校验) → Nginx (client_max_body_size) → Django (validate_pdf)
     前端防御              第一道服务器防御              第二道服务器防御
```

## 常用运维命令

```bash
# 查看应用日志
journalctl -u qft-course -f

# 查看错误日志
journalctl -u qft-course --since "1 hour ago"

# 重启应用（代码更新后）
systemctl restart qft-course

# 重载 Nginx（配置修改后）
systemctl reload nginx

# 更新代码
cd /opt/qft-course
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
systemctl restart qft-course
```

## 验证部署成功

1. 浏览器访问 `http://你的服务器IP` → 看到课程首页
2. 访问 `http://你的服务器IP/admin/` → 能登录管理后台
3. 注册一个学生账号 → 能登录
4. 提交一个测试作业 → 上传 PDF 成功
5. 用 `https://` 访问 → 证书生效（备案完成后）

## 常见问题

| 问题 | 原因 | 解决方法 |
|------|------|----------|
| 502 Bad Gateway | Gunicorn 没启动 | `systemctl status qft-course` 检查 |
| 静态文件 404 | collectstatic 没执行 | `python manage.py collectstatic` |
| 上传 413 错误 | Nginx client_max_body_size 太小 | 改为 25M 并 `nginx -s reload` |
| CSRF 验证失败 | CSRF_TRUSTED_ORIGINS 没配 | 在 .env 中添加域名 |
| 数据库连接失败 | PostgreSQL 没启动或密码错误 | `systemctl status postgresql` |
| 域名无法访问 | 没备案或 DNS 没解析 | 先用 IP 访问测试 |

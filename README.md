# 规范场课程网站

理论物理课程"规范场"的教学辅助网站，支持课程内容发布、公告管理、学生作业管理、在线评分和批量导入。

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端 | Django 5.1.7 | Python 3.12 |
| 数据库 | PostgreSQL（生产）/ SQLite（开发） | Django ORM |
| 前端样式 | Tailwind CSS | CDN 引入，无需构建 |
| 交互 | Alpine.js | CDN 引入，轻量交互 |
| 内容渲染 | python-markdown 3.10.2 | 章节内容使用 Markdown |
| 部署 | 腾讯云 CVM (Ubuntu 22.04) | Nginx + Gunicorn + systemd |

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/ygexplorer/qftcourse.git
cd qftcourse
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入真实值（开发环境可保持默认）
```

### 5. 数据库迁移

```bash
python manage.py migrate
```

### 6. 创建管理员账号

```bash
python manage.py createsuperuser
# 按提示输入用户名、密码等
```

### 7. 启动开发服务器

```bash
python manage.py runserver
```

访问 http://127.0.0.1:8000 即可看到网站首页。

管理后台：http://127.0.0.1:8000/admin/

## 项目结构

```
config/          Django 项目配置（settings.py, urls.py, wsgi.py）
accounts/        用户管理（User 模型、登录/注册、角色权限）
courses/         课程核心（学期、章节、作业、提交）
templates/       全局模板（base.html）
media/           用户上传文件（git 忽略，开发时由 Django 直接服务）
docs/            项目文档
.env             环境变量（git 忽略，包含密钥）
.env.example     环境变量模板（提交到 Git）
requirements.txt Python 依赖
```

## 用户角色

| 角色 | 创建方式 | 核心权限 |
|------|----------|----------|
| student | 自行注册 | 浏览课程、提交作业 |
| ta | 教师在 Admin 中创建 | 查看所有提交、下载文件、评分 |
| teacher | 管理员创建 | 管理课程内容、用户、公告、批量导入学生 |
| admin | `createsuperuser` 命令 | 全部权限 |

## 功能概览

- **课程内容**：学期管理 → 章节列表 → 章节详情（Markdown 渲染、草稿/发布控制）
- **作业系统**：发布作业（含 PDF 附件）→ 学生提交（逾期标记）→ TA/教师评分（0-100 + 评语）
- **评分工作台**：卡片式统一评分界面，支持筛选（未评分/已评分/逾期）、搜索、"保存并下一个"流程
- **公告系统**：发布通知（支持置顶），不需登录即可浏览
- **批量导入**：Admin 页面上传 Excel，一键创建学生账号（用户名=学号，密码=学号后6位）

## 生产部署

详见 [docs/DEPLOY.md](docs/DEPLOY.md)。

简要步骤：

1. 腾讯云 CVM 安装 PostgreSQL、Nginx、Python 3.12
2. 克隆代码，安装依赖（含 `psycopg2-binary`）
3. 配置 `.env`（DEBUG=False、SECRET_KEY、ALLOWED_HOSTS、数据库等）
4. `python manage.py migrate` + `python manage.py collectstatic`
5. 配置 Gunicorn + systemd 服务
6. 配置 Nginx 反向代理 + HTTPS 证书

## 许可证

MIT

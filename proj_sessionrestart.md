# 规范场课程网站 — 新会话启动摘要

> 复制此内容到新对话窗口即可恢复项目上下文。

## 项目概述

理论物理课程的辅助教学网站，面向课程教师、助教和学生，提供课程内容浏览和作业管理功能。

## 技术栈

- **后端**：Python 3.12.6 + Django 5.1.7
- **前端**：Tailwind CSS (CDN) + Alpine.js (CDN)，无前端构建工具
- **数据库**：开发 SQLite，生产 PostgreSQL
- **部署目标**：腾讯云 CVM（Ubuntu 22.04），域名已备好
- **开发环境**：venv 在项目根目录 `venv/`，`pip install` 需 `--trusted-host` 参数
- **超级管理员**：admin / admin123
- **项目路径**：`/Users/gangyang/WorkBuddy/20260328230225/`

## 项目结构

```
config/          — Django 项目配置（settings, urls, wsgi）
accounts/        — 用户管理（User 模型、登录/注册、角色中间件、信号）
courses/         — 课程核心（Semester, Chapter, Assignment, Submission）
templates/       — 全局模板（base.html）
media/           — 用户上传文件（开发环境通过 Django 直接服务）
.env             — 环境变量（不提交 GitHub）
requirements.txt — Python 依赖
```

## 三种角色权限

| 功能 | student | ta | teacher |
|------|---------|----|---------|
| 注册账号 | ✅ 自己注册 | ❌ 教师创建 | ❌ 教师创建 |
| 浏览课程内容 | ✅ 已发布 | ✅ 已发布 | ✅ 全部（含草稿预览） |
| 发布/管理作业 | ❌ | ❌ | ✅（通过 Django Admin） |
| 提交作业 | ✅ | ❌ | ❌ |
| 重新提交（覆盖） | ✅ 覆盖旧文件 | ❌ | ❌ |
| 查看提交列表 | 仅自己的 | ✅ 全部学生 | ✅ 全部学生 |
| 下载提交文件 | 仅自己的 | ✅ 全部 | ✅ 全部 |
| 管理用户账号 | ❌ | ❌ | ✅ student/ta（不含其他 teacher） |

## 已完成功能（第一～五阶段）

1. **用户系统**：登录/注册/登出/修改密码，按角色自动跳转，`SyncStaffMiddleware` 让教师自动获得 Admin 访问权限
2. **课程内容**：首页（当前学期高亮）→ 学期页（章节列表）→ 章节详情（Markdown 渲染、上下章导航、草稿预览）
3. **作业系统**：
   - 教师通过 Django Admin 发布作业（含 PDF 附件）
   - 学生前台提交 PDF（20MB 限制，前后端双重校验）
   - 逾期提交必须填原因，系统标记 `is_late`
   - 重新提交覆盖旧文件（`os.remove` 删除旧文件，直接更新记录）
   - PDF 自动命名：`username_a{assignment_id}_{datetime}.pdf`，原始文件名保存在数据库
   - 作业列表状态：未提交 / 已提交 / 逾期提交 / 已逾期未提交
   - 下载权限：学生仅自己的，TA 仅已发布作业的，教师全部

## 第一版明确不做

- ❌ 不做在线评分（`score`/`feedback` 字段预留但前台不展示）
- ❌ 不保留提交历史（重新提交直接覆盖，唯一约束 `unique_together = [['assignment', 'student']]`）
- ❌ 不做公告系统前台展示（模型已有，第一版不启用）
- ❌ 不做前端构建（Tailwind/Alpine 均用 CDN）

## 待完成（第六阶段）

- GitHub 仓库初始化 + .gitignore
- 腾讯云部署（PostgreSQL、Nginx、Gunicorn、systemd）
- MEDIA_ROOT 迁移到腾讯云 COS（长期）

## 关键技术决策

- **Admin 权限**：`TeacherAdminMixin` 让教师通过 Admin 管理课程内容，但不能修改其他教师/管理员
- **is_staff 同步**：中间件（请求时）+ pre_save 信号（持久化），避免 AnonymousUser 兼容问题
- **文件上传**：`upload_to` 用可调用函数按 `类型/年/月` 分目录，方便以后迁移 COS
- **Markdown**：`python-markdown 3.10.2`（注意包名大写 `Markdown`），自定义 `{{ content|markdown }}` 模板标签
- **学生登录跳转**：登录/注册后 → 课程首页 `/`，导航栏点"我的作业"进入 `/assignments/`
- **MEDIA_ROOT**：通过 `.env` 环境变量配置，开发/生产分离

## 当前已知问题

- 无已知未修复 bug（最近修复了重新提交覆盖逻辑和 URL 引用遗漏）

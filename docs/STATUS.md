# 开发进度

## 阶段总览

| 阶段 | 内容 | 状态 |
|------|------|------|
| 1 | 技术方案 | ✅ 完成 |
| 2 | 项目初始化 + 模型 + 基础模板 | ✅ 完成 |
| 3 | 用户注册/登录/权限 | ✅ 完成 |
| 4 | 课程主页 + 章节浏览 + Markdown 渲染 | ✅ 完成 |
| 5 | 作业系统（发布/提交/PDF上传/逾期标记） | ✅ 完成 |
| 6 | GitHub 仓库 + 腾讯云部署 | ✅ 完成 |
| 7 | 公告系统（列表+详情+置顶） | ✅ 完成 |
| 8 | 评分与评语（TA/教师评分 0-100） | ✅ 完成 |
| 9 | 教师评分工作台（卡片式+筛选+搜索+自动下一个） | ✅ 完成 |
| 10 | 学生批量导入（Admin 上传 Excel） | ✅ 完成 |
| 11 | 学生个人资料编辑（display_name / student_id） | ✅ 完成 |
| 12 | 章节导航与讲义下载 | ✅ 完成 |
| 13 | 首页视觉重设计（Hero/知识图谱/暗色模式） | ✅ 完成 |

## 已完成功能详情

### 第三阶段：用户系统

- [x] 自定义 User 模型（含 role、display_name、student_id 字段）
- [x] 学生自行注册（TA/Teacher 由教师通过 Admin 创建）
- [x] 登录/登出（按角色自动跳转）
- [x] 修改密码
- [x] 角色权限装饰器（teacher_required、ta_required、student_required）
- [x] 教师自动获得 Django Admin 访问权限（SyncStaffMiddleware + pre_save 信号）
- [x] 教师在 Admin 中可管理 student/ta 用户，但不能修改其他教师/管理员
- [x] 权限拒绝友好提示页（403 → 200 友好页面）

### 第四阶段：课程内容

- [x] 课程首页（学期列表，当前学期高亮）
- [x] 学期首页（章节列表，序号排列）
- [x] 章节详情（Markdown 渲染，上下章导航）
- [x] 草稿/发布状态控制（教师可预览草稿，其他人草稿返回 404）
- [x] Django Admin 中管理学期和章节
- [x] 教师仪表盘（课程管理入口）
- [x] TA 仪表盘（课程内容入口）

### 第五阶段：作业系统

- [x] Assignment 模型（标题、描述、PDF 附件、截止时间、发布状态）
- [x] Submission 模型（文件、原始文件名、文件大小、留言、逾期标记、逾期原因）
- [x] 教师通过 Admin 发布作业（含 PDF 附件）
- [x] 学生前台提交 PDF
  - [x] 前端 JS 校验（PDF 格式 + 20MB 大小）
  - [x] 后端校验（扩展名 + MIME type + 文件大小 + 空文件检查）
- [x] 逾期提交必须填原因，系统标记 `is_late`
- [x] 重新提交覆盖旧文件（删除旧文件 → 更新记录）
- [x] PDF 自动命名（`username_a{id}_{datetime}.pdf`）
- [x] 原始文件名保存在数据库，下载时恢复
- [x] 作业列表状态显示（未提交 / 已提交 / 逾期提交 / 已逾期未提交）
- [x] 下载权限控制（学生仅自己的，TA 仅已发布作业，教师全部）
- [x] TA 不能下载未发布作业的学生提交
- [x] 学生登录后 → 课程首页，导航栏"我的作业"进入作业列表
- [x] TA/教师仪表盘添加作业管理入口
- [x] 逾期判断以服务器时间为准（`timezone.now()`）

### 第六阶段：GitHub + 腾讯云部署

- [x] `.gitignore` 完善（排除 `.env`、`media/`、`staticfiles/`、`.workbuddy/`、`*.pyc` 等）
- [x] `requirements.txt` 整理（逐包注释，`psycopg2-binary` 注释标注生产需要）
- [x] `.env.example` 更新（添加 `CSRF_TRUSTED_ORIGINS`、`MEDIA_ROOT` 说明）
- [x] `settings.py` 添加 `CSRF_TRUSTED_ORIGINS` 支持（从环境变量读取）
- [x] `README.md` 创建（技术栈、快速开始、项目结构、角色说明）
- [x] `docs/DEPLOY.md` 部署指南
- [x] GitHub 仓库复用（`ygexplorer/qftcourse`，旧代码备份至 `backup-main` 分支）
- [x] 腾讯云部署
  - [x] PostgreSQL 14 数据库（`qft_course` / `qft_user`）
  - [x] 项目部署至 `/home/ubuntu/qft-course/`
  - [x] Gunicorn（3 workers，`127.0.0.1:8001`）
  - [x] systemd 服务（`qft-course.service`）
  - [x] Nginx 反向代理 + 静态/媒体文件服务（`client_max_body_size 25M`）
  - [x] HTTPS（Let's Encrypt，域名 `gaugetheory.angly.cn`）
  - [x] 生产环境配置（`DEBUG=False`、随机 `SECRET_KEY`、`ALLOWED_HOSTS`、`CSRF_TRUSTED_ORIGINS`）
  - [x] 验证通过：首页 HTTPS 200、Admin 登录、学生注册

### 第七阶段：公告系统

- [x] 公告列表页（按学期筛选，最新在前）
- [x] 公告详情页（Markdown 渲染）
- [x] 置顶功能（置顶公告始终在顶部）
- [x] 不需要登录即可浏览
- [x] 教师通过 Django Admin 管理公告
- [x] URL 路由优先级（`announcements/` 在 `semester/<slug>/` 之前）

### 第八阶段：评分与评语

- [x] Submission 模型新增 `scored_at` 和 `scored_by` 字段（migration 0003）
- [x] TA/教师可在作业提交详情页填写评分（0-100）和评语
- [x] 非模型表单 `GradingForm`，score 留空表示清除评分
- [x] 学生可查看自己的分数和评语

### 第九阶段：教师评分工作台

- [x] 独立页面 `assignment/<pk>/grading/`
- [x] 卡片式提交列表（学生信息、提交状态、留言、评分区）
- [x] Alpine.js 前端筛选（全部 / 未评分 / 已评分 / 逾期）
- [x] 学生姓名搜索
- [x] 颜色编码左边框（橙色=未评分、绿色=已评分、红色=逾期）
- [x] "保存并评下一个"自动跳转下一个未评分提交（URL hash 定位）
- [x] 全部评完显示完成提示
- [x] 学生访问返回 404
- [x] 作业列表页提交数可点击进入工作台
- [x] 作业详情页有"进入评分工作台"按钮

### 第十阶段：学生批量导入

- [x] Admin 页面上传 Excel（`/admin/import-students/`）
- [x] `admin.site.admin_view()` 权限包裹
- [x] 支持 .xls/.xlsx 格式（pandas 读取，学号列 `dtype=str` 保留前导零）
- [x] 用户名=学号，密码=学号后6位，role=student
- [x] 已存在学号自动跳过不覆盖
- [x] 导入结果页（成功/跳过/错误分表显示）
- [x] Admin 用户列表页顶部绿色"批量导入学生"按钮

### 第十一阶段：学生个人资料编辑

- [x] `ProfileEditForm` 表单（仅允许编辑 display_name 和 student_id）
- [x] `profile_edit` 视图（所有已登录角色可访问）
- [x] 资料编辑模板（居中卡片布局，用户名只读展示）
- [x] URL 路由 `/accounts/profile/`
- [x] 导航栏桌面端和手机端添加"个人资料"入口
- [x] 保存后按角色跳转，显示成功提示

### 第十二阶段：章节导航与讲义下载

- [x] Chapter 模型新增 `lecture_pdf` 字段（FileField，可选 PDF 上传）
- [x] `chapter_lecture_path` 上传路径函数（`lectures/YYYY/MM/` 目录结构）
- [x] `download_lecture` 下载视图（已登录可见，未发布章节仅教师可见）
- [x] Admin Chapter 页面：新增讲义字段、列表显示"有讲义"标记
- [x] `extract_toc` 过滤器：从 Markdown 提取 H2/H3 标题列表
- [x] `inject_heading_ids` 过滤器：给渲染后 HTML 注入 `heading-N` 锚点（覆盖 toc 扩展的默认 id）
- [x] 章节详情页改为左右两栏布局（左侧目录 sticky + 右侧正文）
- [x] 桌面端目录可收缩/展开（Alpine.js 切换）
- [x] 手机端抽屉式目录（从左侧滑出 + 半透明遮罩）
- [x] IntersectionObserver 滚动高亮当前可见标题
- [x] 讲义下载入口卡片（章节标题下方，仅已登录 + 有 PDF 时显示）
- [x] 数据库迁移 `0004_chapter_lecture_pdf`

### 第十三阶段：首页视觉重设计

**背景**：Phase 4 的首页仅有学期列表，功能性弱但视觉朴素。Phase 13 对首页进行全面视觉重设计，引入知识图谱可视化、Hero 动画、暗色模式等特性，大幅提升用户体验。

#### base.html 全局增强

- [x] 暗色模式支持：Tailwind `darkMode: 'class'` + localStorage 持久化 + IIFE 初始化（避免页面闪烁）
- [x] 导航栏毛玻璃效果（`backdrop-blur-md`）+ 阴影边框（`shadow-sm border-b`）
- [x] 全局页面过渡动画（`transition-colors duration-200`）
- [x] Django messages 提示样式（成功/错误/默认三种颜色）
- [x] 页脚 Copyright 2026
- [x] `x-cloak` CSS 隐藏 Alpine 未加载时的闪烁
- [x] 暗色模式切换按钮（太阳/月亮 SVG 图标，桌面端 + 手机端均有）

#### home.html 完全重写

- [x] **Hero 区域**：渐变背景（`from-slate-50 via-blue-50/60 to-indigo-50/40`）+ 3 个动态浮动圆形光斑（`hero-orb1/2/3`，`orbFloat` 动画 10-14s）+ SVG 同心圆装饰
- [x] **课程标语**：学期徽章（脉冲圆点 + "2026 年春季学期 · 杭高院"）+ 大标题（"规范场"）+ 英文副标题（"Gauge Field Theory"）
- [x] **进入课程按钮**：蓝色大按钮，悬停阴影提升 + 上移动画
- [x] **知识图谱**（核心亮点）：
  - 14 个节点分 4 行排列（SVG 连接线 + 流动动画 `dashFlow`）
  - 节点颜色编码（蓝/橙/绿/紫），颜色定义在视图 `KNOWLEDGE_GROUPS` 常量中
  - 每节点带发光光晕（`blur-md`）+ 毛玻璃卡片效果
  - 悬停展开章节列表弹窗（popover）
  - 有内容的节点显示绿色小圆点标记
- [x] **动画系统**：`fadeUp` 淡入动画（0.55s，4 档延迟）+ `kg-flow` SVG 虚线流动
- [x] **暗色模式适配**：`.dark .glass-card` 暗色毛玻璃效果
- [x] **底部学期入口**：链接回学期首页

#### home 视图增强

- [x] `Chapter.group` 字段分组（`exclude(group='')` 排除未分组章节）
- [x] `KNOWLEDGE_GROUPS` 常量（14 个节点元数据：id/label/row/num/color/glow/desc）
- [x] 教师可看全部章节（含草稿），其他人只看已发布
- [x] `chapters_by_group` 字典：按 group id 分组的章节列表，供模板悬停弹窗使用

#### semester_home.html 公告区增强

- [x] 置顶公告样式升级（琥珀色背景 `bg-amber-50`，醒目边框）
- [x] 普通公告白色卡片 + 悬停高亮（`hover:border-primary-300 hover:bg-primary-50`）
- [x] 公告条目右侧箭头图标（`group-hover` 动态颜色）

## 待完成

- [ ] 教师仪表盘动态数据
- [ ] 提交历史记录
- [ ] 课程资料/参考材料
- [ ] 文件存储迁移至腾讯云 COS
- [ ] 在线 Markdown 编辑器

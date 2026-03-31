# 设计决策记录

本文档记录项目开发过程中的关键设计决策及其理由。

## D-01: 技术栈选择 — Django + CDN

**决策**：使用 Django 作为全栈框架，前端样式和交互通过 CDN 引入 Tailwind CSS 和 Alpine.js，不使用前端构建工具。

**理由**：
- 项目以内容管理和表单交互为主，无需复杂前端 SPA
- 用户（课程教师）不具备前端工程经验，CDN 方式更易维护
- Django 模板 + Tailwind CSS 足以实现清晰美观的教学界面
- 减少构建流程，降低部署复杂度

---

## D-02: 三角色权限模型

**决策**：使用自定义 User 模型的 `role` 字段（student/ta/teacher/admin），而非 Django 原生的 `is_staff`/`is_superuser` 来区分业务角色。

**理由**：
- 业务角色（学生/助教/教师）与 Django 的 staff/superuser 概念不同
- `role` 字段更直观，权限逻辑更清晰
- 教师/管理员需要 Admin 访问权限（`is_staff`），但 `is_staff` 仅用于 Admin 入口控制，不用于业务权限判断

**实现**：
- `SyncStaffMiddleware`：每个请求时将 teacher/admin 的 `is_staff` 设为 True
- `sync_staff_on_save` 信号：保存用户时持久化 `is_staff`
- 业务权限通过 `role` 字段 + 自定义装饰器判断

---

## D-03: TA 权限边界

**决策**：TA 只能查看，不能创建或修改课程内容。

**具体规则**：
- TA 可以查看已发布的课程章节
- TA 可以查看所有学生的作业提交和下载提交文件
- TA 不能查看未发布作业的学生提交
- TA 不能在 Django Admin 中管理任何内容
- TA 账号由教师通过 Admin 创建

**理由**：TA 的职责是协助批改和管理，不应有发布权限。

---

## D-04: 课程内容管理方式 — Django Admin

**决策**：第一版通过 Django Admin 管理学期、章节和作业，不开发独立的前台编辑界面。

**理由**：
- 教师用户少（1-2 人），Admin 界面完全够用
- 减少 50% 以上的前端开发工作量
- Django Admin 自带表单验证、搜索、过滤、排序等功能
- 仪表盘已预留"课程管理"入口链接到 Admin

**局限性**：Markdown 内容需要在 Admin 的 TextField 中编写，没有实时预览。后续可考虑集成 Markdown 编辑器。

---

## D-05: 作业提交 — 覆盖而非追加

**决策**：每个学生对每个作业只能有一条提交记录，重新提交直接覆盖旧文件和记录。

**理由**：
- 第一版不保留提交历史，简化数据模型和逻辑
- 数据库约束 `unique_together = [['assignment', 'student']]` 确保唯一性
- 教师看到的始终是学生的最新提交
- 如果需要评分历史，后续可扩展 SubmissionHistory 模型

**实现**：
- 重新提交时先 `os.remove()` 删除旧物理文件
- 然后更新已有 Submission 记录的所有字段
- Django 的 FileField `save()` 自动为新文件调用 `upload_to` 生成存储路径

---

## D-06: 第一版不做评分

**决策**：模型中预留了 `score` 和 `feedback` 字段，但第一版前台不展示评分功能。

**理由**：
- 第一版优先确保作业提交流程可用
- 评分方式和标准需要教师确认后再设计 UI
- 字段已预留，后续只需开发前台展示和编辑界面

---

## D-07: 文件上传设计

**决策**：
- 文件大小限制 20MB（前后端双重校验）
- 仅支持 PDF 格式（扩展名 + MIME type 双重校验）
- 服务器自动重命名，原始文件名保存在数据库
- 按类型/年/月分目录存储

**命名规则**：
- 学生提交：`{username}_a{assignment_id}_{YYYYMMDD_HHMMSS}.pdf`
- 教师附件：`attachment_a{assignment_id}_{YYYYMMDD_HHMMSS}.pdf`

**理由**：
- 自动命名避免文件名冲突和中文/空格问题
- 用户名（username）是唯一且 ASCII 安全的，比 display_name 更可靠
- 原始文件名保存在数据库，教师下载时恢复为原始文件名
- 按月分目录方便以后迁移到对象存储（如腾讯云 COS）
- 20MB 足以覆盖正常 PDF 作业，避免滥用磁盘

---

## D-08: 逾期判断以服务器时间为准

**决策**：使用 Django 的 `timezone.now()` 判断是否逾期，不信任浏览器时间。

**理由**：
- 浏览器时间可以被用户随意修改
- 服务器时间（`TIME_ZONE = 'Asia/Shanghai'`）是唯一可信来源
- `USE_TZ = True` 确保所有时间都是 timezone-aware 的

---

## D-09: Markdown 渲染方案

**决策**：使用 `python-markdown 3.10.2`（PyPI 包名为 `Markdown`，大写 M），自定义 `{{ content|markdown }}` 模板标签。

**理由**：
- 服务端渲染，输出安全且可控
- 支持常用扩展：fenced_code、tables、toc
- 比 CommonMark 更灵活，适合物理课程中可能出现的数学公式块

**注意**：`pip install markdown` 会安装错误的包（0.1.0），必须使用 `pip install Markdown`。

---

## D-10: 部署目标 — 仅腾讯云

**决策**：正式部署只面向腾讯云 CVM，不做多云或多平台适配。

**理由**：
- 用户已准备好腾讯云 CVM 和域名
- 单一部署目标简化配置和运维
- 数据库使用 PostgreSQL（腾讯云自带或自建）
- MEDIA_ROOT 通过 `.env` 环境变量配置，开发/生产分离

---

## D-11: 学生登录跳转 → 课程首页

**决策**：学生登录/注册后跳转到课程首页（`/`），而非作业列表。学生通过导航栏"我的作业"链接进入作业列表。

**理由**：
- 课程首页是所有学生的公共入口，包含课程内容导航
- 作业只是课程的一部分，不应作为唯一入口
- 导航栏始终可见，"我的作业"只需一次点击

---

## D-12: ~~暗色模式实现~~ → **已废弃**

**决策**：完全移除暗色模式。

**原因**：Tailwind CDN 模式下 `darkMode: 'class'` 配置不生效——dark: 样式被生成在 `@media (prefers-color-scheme: dark)` 媒体查询中，而非预期的 `.dark .dark\:xxx` 类选择器。暗色模式切换从未真正工作过。

**实现**：移除切换按钮、IIFE 脚本、`darkMode: 'class'` 配置、所有 dark: 类。

---

## D-16: 数学公式渲染 — KaTeX 前端渲染 + 国内 CDN

**决策**：章节内容和公告的数学公式使用 KaTeX 前端渲染，通过国内 BootCDN 加载。

**理由**：
- Python-Markdown 标准库无 math 扩展，安装第三方扩展（mdx-math）有网络/CDN 稳定性问题
- KaTeX 的 auto-render 是纯前端处理：扫描 `$...$` / `$$...$$` 文本直接在浏览器渲染，不需要后端参与
- 后端只负责把 Markdown 转 HTML，`$...$` 原文原样输出，KaTeX 在浏览器端渲染

**CDN 选择**：BootCDN（`cdn.bootcdn.net`）替代 jsdelivr（国内访问有问题）。

**风险**：依赖 BootCDN 第三方服务长期稳定性。如遇失效可换 75CDN（`lib.baomitu.com`）。

**支持语法**：`$inline$`、`$$display$$`、`\[...\]`、`\(...\)`

---

## D-13: 首页知识图谱 — 静态节点定义 + 动态章节数据

**决策**：首页展示的 14 个知识节点（元数据：颜色/标签/位置）硬编码在视图 `KNOWLEDGE_GROUPS` 常量中，章节是否属于某节点由 `Chapter.group` 字段动态决定。

**理由**：
- 知识图谱的节点结构（顺序、颜色、描述）反映课程知识体系，应由开发者/教师在代码层面定义，不适合放到数据库
- 章节与节点的归属关系由 `Chapter.group` 字段动态关联，支持后续调整
- `Chapter.group=''`（空字符串）的章节不显示在图谱中，保持灵活性
- 硬编码 14 个节点与讲义 14 个主干章节一一对应，视觉上整齐

**KNOWLEDGE_GROUPS 结构**：
```python
{
    'id': 'review',   # 与 Chapter.group 值对应
    'label': '基础回顾',  # 节点显示标签
    'row': 1,         # 图谱第几行（1-4）
    'num': 1,        # 节点序号（1-14）
    'color': '#475569',  # 节点主色（十六进制）
    'glow': '#64748b',   # 光晕色
    'desc': '经典场论 · 正则量子化 · SD方程',  # 节点描述
}
```

---

## D-14: 知识图谱节点分组方式 — Chapter.group 字段

**决策**：`Chapter` 模型新增 `group` 字段（CharField），用于将章节归属到知识图谱的某个节点。同一个 group 下的多个章节在节点悬停时显示为列表。

**理由**：
- 一个知识节点下可能包含多个章节（如"基础回顾"可能有多章），需要一对多关系
- `group=''` 表示该章节不参与知识图谱展示（可能是补充章节或草稿）
- 教师通过 Admin 方便地编辑章节的 group 值，无需改代码

---

## D-15: 知识图谱视图逻辑 — 教师可见草稿章节

**决策**：`home` 视图中，教师用户（`is_teacher=True`）可以看全部章节（含草稿），其他人只看 `is_published=True` 的已发布章节。

**理由**：
- 教师需要预览草稿章节在图谱中的位置
- 学生和匿名用户只看已发布内容是合理的课程保护策略
- 实现方式：视图层判断，模板不需要额外判断，逻辑集中

---

## D-17: 网站 Favicon 图标

**决策**：课程网站使用 AI 生成的 Favicon 图标，象征规范场/纤维丛联络。

**图标设计**：深蓝色圆球 + 三条白色曲线，象征纤维丛上的联络（Connection）。

**实现**：
- AI 生成图标文件：`static/favicon/favicon.png`
- `base.html` 添加 `<link rel="icon">` 和 `<link rel="apple-touch-icon">`
- `settings.py` 添加 `STATICFILES_DIRS = [BASE_DIR / 'static']`（使 collectstatic 能收集项目 static 目录）

---

## D-18: STATICFILES_DIRS 配置 — 项目 static 目录收集

**问题**：部署后发现项目的 `static/` 目录（favicon 等）不会被 `collectstatic` 收集到 `staticfiles/` 目录，导致文件无法通过 Nginx 访问。

**原因**：`settings.py` 中只有 `STATIC_URL` 和 `STATIC_ROOT`，缺少 `STATICFILES_DIRS`。

**修复**：`settings.py` 添加：
```python
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # 项目根目录 static/ 目录（favicon 等）
]
```

**教训**：后续新加任何 static 文件，都需要确保此配置存在。

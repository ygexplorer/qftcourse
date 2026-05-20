# 删除知识图谱第14章 — 实施计划 (v2: 节点13移到第3行)

## 目标

删除第14章 "S矩阵在壳性方法"（`smatrix`），节点13 "规范-引力之联系"从第4行移到第3行，知识图谱变为整齐的 3 行 13 节点。

## 布局变化

```
之前:                          之后:
Row 1: ① ② ③ ④ ⑤ ⑥         Row 1: ① ② ③ ④ ⑤ ⑥
Row 2: ⑦ ⑧ ⑨                 Row 2: ⑦ ⑧ ⑨
Row 3: ⑩ ⑪ ⑫                 Row 3: ⑩ ⑪ ⑫ ⑬
Row 4: ⑬ ⑭                  (第4行删除)
```

## 修改清单

### 1. `courses/models.py:89` — 删除

```python
('smatrix',   '14 S矩阵在壳性方法'),   ← 删除这一行
```

### 2. `courses/views.py` — 删除 smatrix + 移动 grav 到 row 3

- 第 40 行注释：`14个` → `13个`
- 第 69–71 行的 `grav` 节点：`'row': 4` → `'row': 3`
- 删除第 72–73 行的 `smatrix` 节点

### 3. `courses/templates/courses/home.html` — 3处修改

**a) 第 100 行：** `共 14 个核心章节` → `共 13 个核心章节`

**b) 第3行 SVG（~232–249行）：** 从3节点改为4节点

- 渐变 `row3Line` 添加第4个色标：`<stop offset="100%" stop-color="#6366f1" stop-opacity="0.2"/>`（节点13颜色）
- 添加第4个圆：`<circle cx="775" cy="10" r="4" fill="#6366f1" opacity="0.5"/>`
- 添加第4条虚线：`<line x1="775" y1="10" x2="775" y2="58" stroke="#6366f1" stroke-width="1.2" stroke-dasharray="4 3" opacity="0.35" class="kg-flow"/>`
- 主轴线从 `x2="675"` 延伸至 `x2="775"`
- 渐变 `row3Line` 调整 stops 为 0%/33%/66%/100%，使4个stop均匀分布

**c) 删除整个第4行区块（291–345行）** — 包含 SVG 和 `<div>` 节点循环

### 4. 数据库迁移

```bash
cd /Users/angly/MiniFiles/QFT_website/sources
source venv/bin/activate
python manage.py makemigrations courses
```

### 5. 部署

```bash
# 本地提交并推送
git add -A
git commit -m "删除知识图谱第14章S矩阵在壳性方法，节点13移至第3行"
git push

# 服务器部署
ssh ubuntu@150.158.103.51
cd /home/ubuntu/qft-course
git pull
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart qft-course
```

## 涉及文件

| 文件 | 修改类型 |
|------|----------|
| `courses/models.py` | 删除 1 行 |
| `courses/views.py` | 改 grav 的 row + 删 smatrix + 注释 |
| `courses/templates/courses/home.html` | 标题文字 + 第3行SVG扩展 + 删除第4行 |
| `courses/migrations/XXXX_*.py` | 自动生成 |

## 部署前提检查

| 检查项 | 状态 |
|--------|------|
| SSH 到服务器 (`ubuntu@150.158.103.51`) | ✅ OK |
| GitHub SSH 认证 (`git@github.com:ygexplorer/qftcourse`) | ✅ OK |
| 本地 Git 工作区 | ✅ 干净，无未提交改动 |
| 本地 SQLite 无 smatrix 章节 | ✅ 无数据冲突 |

## 验证

1. 本地 `runserver` → 首页图谱 3 行 13 节点，第3行 4 个节点排列整齐
2. 首页文字 "共 13 个核心章节"
3. Admin 添加章节时 group 下拉无第14项
4. 部署后线上同等验证

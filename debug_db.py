#!/usr/bin/env python3
"""诊断脚本：检查数据库路径和内容"""
import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

print(f"项目根目录: {BASE_DIR}")
print(f"instance 目录: {os.path.join(BASE_DIR, 'instance')}")
print(f"instance 目录是否存在: {os.path.exists(os.path.join(BASE_DIR, 'instance'))}")

db_path = os.path.join(BASE_DIR, 'instance', 'gauge_theory.db')
print(f"数据库文件: {db_path}")
print(f"数据库是否存在: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    size = os.path.getsize(db_path)
    print(f"数据库大小: {size} bytes")

# 检查 Flask 应用中的数据库路径
from app import create_app
app = create_app()
print(f"\nFlask 配置的数据库 URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

# 检查数据库内容
from app.models.user import User
from app.models.chapter import Chapter
with app.app_context():
    users = User.query.all()
    chapters = Chapter.query.all()
    print(f"\n数据库中的用户数: {len(users)}")
    for u in users:
        print(f"  - {u.username} ({u.role})")
    print(f"数据库中的章节数: {len(chapters)}")
    for c in chapters:
        has_content = bool(c.content and c.content.strip())
        print(f"  - 第{c.number}章 {c.title}: {'有内容' if has_content else '空'}")

#!/bin/bash

# QFT Course 服务器一键初始化脚本
# 在服务器上运行此脚本

set -e

echo "========================================="
echo "开始部署 QFT Course..."
echo "========================================="

# 1. 安装系统依赖
echo "[1/7] 安装系统依赖..."
apt update
apt install -y python3-pip python3-venv nginx git

# 2. 克隆代码
echo "[2/7] 克隆代码..."
if [ -d "/root/qftcourse" ]; then
    cd /root/qftcourse
    git pull origin main
else
    cd /root
    git clone https://github.com/ygexplorer/qftcourse.git
    cd qftcourse
fi

# 3. 创建虚拟环境
echo "[3/7] 创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# 4. 创建必要目录
echo "[4/7] 创建目录结构..."
mkdir -p instance
mkdir -p app/uploads

# 5. 初始化数据库
echo "[5/7] 初始化数据库..."
if [ ! -f "instance/gauge_theory.db" ]; then
    python init_data.py
fi

# 6. 配置 Gunicorn 服务
echo "[6/7] 配置 Gunicorn 服务..."
cp gunicorn.service /etc/systemd/system/gunicorn-qftcourse.service
systemctl daemon-reload
systemctl enable gunicorn-qftcourse
systemctl start gunicorn-qftcourse

# 7. 配置 Nginx
echo "[7/7] 配置 Nginx..."
cp nginx.conf /etc/nginx/sites-available/qftcourse
ln -sf /etc/nginx/sites-available/qftcourse /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

# 配置防火墙
if command -v ufw &> /dev/null; then
    ufw allow 'Nginx Full'
fi

echo ""
echo "========================================="
echo "部署完成！"
echo "========================================="
echo "访问地址: http://150.158.103.51"
echo ""
echo "服务状态:"
systemctl status gunicorn-qftcourse --no-pager
systemctl status nginx --no-pager

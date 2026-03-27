#!/bin/bash

# 一键上传和部署脚本
# 用法: ./upload-and-deploy.sh

SERVER_IP="150.158.103.51"
SERVER_USER="root"
REMOTE_DIR="/root/qftcourse"

echo "========================================="
echo "正在上传代码到服务器..."
echo "========================================="

# 创建必要的远程目录
ssh ${SERVER_USER}@${SERVER_IP} "mkdir -p ${REMOTE_DIR}"

# 上传代码（排除不必要的文件）
rsync -avz --progress \
    --exclude='.git' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='instance/*.db' \
    --exclude='.DS_Store' \
    --exclude='.idea' \
    --exclude='.vscode' \
    . ${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/

echo ""
echo "========================================="
echo "代码上传完成！"
echo "========================================="
echo ""
echo "现在在服务器上执行以下命令完成部署："
echo ""
echo "ssh root@${SERVER_IP}"
echo "cd /root/qftcourse"
echo "bash deploy.sh"
echo ""

# QFT Course 部署指南

## 第一步：在 GitHub 创建仓库

1. 访问 https://github.com/new
2. 仓库名称：`qftcourse`
3. 选择 Public 或 Private（都行）
4. 不要初始化 README、.gitignore 或 LICENSE（因为本地已经有了）
5. 点击 "Create repository"

## 第二步：推送代码到 GitHub

在项目根目录 `/Users/gangyang/WorkBuddy/20260327165939/gauge-theory-app/` 执行：

```bash
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/ygexplorer/qftcourse.git
git push -u origin main
```

## 第三步：服务器端初始化

SSH 连接到服务器后，执行：

```bash
# 1. 安装基础软件
sudo apt update
sudo apt install -y python3-pip python3-venv nginx

# 2. 克隆代码
cd ~
git clone https://github.com/ygexplorer/qftcourse.git
cd qftcourse

# 3. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# 4. 创建必要的目录
mkdir -p instance
mkdir -p app/uploads

# 5. 初始化数据库
python init_data.py

# 6. 配置 Gunicorn 服务
cp gunicorn.service /etc/systemd/system/gunicorn-qftcourse.service
systemctl enable gunicorn-qftcourse
systemctl start gunicorn-qftcourse

# 7. 配置 Nginx
sudo cp nginx.conf /etc/nginx/sites-available/qftcourse
sudo ln -sf /etc/nginx/sites-available/qftcourse /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# 8. 设置防火墙（如果启用了 ufw）
sudo ufw allow 'Nginx Full'
```

## 第四步：配置部署脚本

```bash
# 给部署脚本执行权限
chmod +x deploy.sh
```

## 以后更新网站

只需两步：

```bash
cd ~/qftcourse
git pull
./deploy.sh
```

## 验证部署

访问：http://150.158.103.51

---

## 域名配置（域名审核通过后）

1. 在域名管理后台添加 A 记录：
   - 主机记录：`@` 或 `www`
   - 记录值：`150.158.103.51`

2. 修改 Nginx 配置：
   ```bash
   sudo nano /etc/nginx/sites-available/qftcourse
   ```
   把 `server_name 150.158.103.51;` 改为 `server_name your-domain.com;`

3. 重启 Nginx：
   ```bash
   sudo systemctl restart nginx
   ```

4. （可选）配置 SSL 证书：
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

---

## 故障排查

```bash
# 查看 Gunicorn 日志
journalctl -u gunicorn-qftcourse

# 查看 Nginx 日志
sudo tail -f /var/log/nginx/error.log

# 重启服务
systemctl restart gunicorn-qftcourse
systemctl restart nginx
```

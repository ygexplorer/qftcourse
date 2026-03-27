import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    # 配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gauge_theory.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB 上传限制
    app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录。'

    # 注册蓝图
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.course import course_bp
    from app.routes.homework import homework_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(course_bp, url_prefix='/course')
    app.register_blueprint(homework_bp, url_prefix='/homework')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # 注册 Jinja2 过滤器和全局函数
    app.template_filter('datetime_format')(datetime_format)
    from datetime import datetime, timezone, timedelta
    app.jinja_env.globals['now'] = lambda: datetime.now(timezone.utc)
    app.jinja_env.globals['timedelta'] = timedelta

    # 错误页面
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return render_template('errors/413.html'), 413

    # 导入所有模型以确保表被创建
    from app.models import user, chapter, announcement

    # 创建数据库表
    with app.app_context():
        db.create_all()
        # 创建默认教师账号（如果不存在）
        from app.models.user import User
        if not User.query.filter_by(role='teacher').first():
            teacher = User(
                username='teacher',
                name='杨刚',
                email='teacher@example.com',
                role='teacher'
            )
            teacher.set_password('teacher123')
            db.session.add(teacher)
            db.session.commit()

    return app


def datetime_format(value, fmt='%Y-%m-%d %H:%M'):
    if value is None:
        return ''
    return value.strftime(fmt)

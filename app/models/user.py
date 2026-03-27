from datetime import datetime, timezone
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'teacher' or 'student'
    student_id = db.Column(db.String(32), unique=True, nullable=True)  # 学号
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # 关系
    submissions = db.relationship('Submission', backref='student', lazy='dynamic')
    grades = db.relationship('Grade', backref='student', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        # 确保空字符串 email 不会触发 UNIQUE 约束冲突
        if self.email == '':
            self.email = None

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_teacher(self):
        return self.role == 'teacher'

    def is_ta(self):
        return self.role == 'ta'

    def is_staff(self):
        """教师或助教都属于教学管理人员"""
        return self.role in ('teacher', 'ta')

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))

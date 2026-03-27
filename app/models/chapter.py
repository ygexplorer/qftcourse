from datetime import datetime, timezone
from app import db


class Chapter(db.Model):
    __tablename__ = 'chapters'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False)
    title = db.Column(db.String(128), nullable=False)
    slug = db.Column(db.String(64), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=True, default='')
    is_visible = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)

    # 关系
    assignments = db.relationship('Assignment', backref='chapter', lazy='dynamic',
                                  order_by='Assignment.due_date')

    def __repr__(self):
        return f'<Chapter {self.number}: {self.title}>'


class Assignment(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    title = db.Column(db.String(128), nullable=False, default='课后作业')
    description = db.Column(db.Text, nullable=True, default='')
    due_date = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    # 关系
    submissions = db.relationship('Submission', backref='assignment', lazy='dynamic')

    def __repr__(self):
        return f'<Assignment {self.title} (Ch.{self.chapter_id})>'


class Submission(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(256), nullable=False)
    filepath = db.Column(db.String(512), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)  # bytes
    submitted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    score = db.Column(db.Float, nullable=True)

    # 确保每个学生对每次作业只能提交一次（最新版本）
    __table_args__ = (db.UniqueConstraint('assignment_id', 'student_id'), )

    def __repr__(self):
        return f'<Submission {self.student_id} -> Assignment {self.assignment_id}>'


class Grade(db.Model):
    __tablename__ = 'grades'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    score = db.Column(db.Float, nullable=True)
    comment = db.Column(db.Text, nullable=True, default='')
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # 确保每个学生每章只有一个成绩
    __table_args__ = (db.UniqueConstraint('student_id', 'chapter_id'), )

    def __repr__(self):
        return f'<Grade Student {self.student_id} Ch.{self.chapter_id}: {self.score}>'

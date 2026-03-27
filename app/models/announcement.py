from datetime import datetime, timezone
from app import db


class Announcement(db.Model):
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False, default='')
    is_pinned = db.Column(db.Boolean, default=False)  # 是否置顶
    is_active = db.Column(db.Boolean, default=True)  # 是否显示
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Announcement {self.title}>'

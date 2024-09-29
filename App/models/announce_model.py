from datetime import datetime

from ..exts import db

class Announcement(db.Model):
    __tablename__ = 'announcement'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', back_populates='announcements')

    def __repr(self):
        return f'<Announcement {self.title}>'

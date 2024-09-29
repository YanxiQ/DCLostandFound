from datetime import datetime

from ..exts import db

class FAQ(db.Model):
    __tablename__ = 'faq'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_asked = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_answered = db.Column(db.Boolean, default=False, nullable=False)


    user = db.relationship('User', back_populates='faqs')
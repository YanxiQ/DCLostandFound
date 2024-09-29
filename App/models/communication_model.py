from ..exts import db
from datetime import datetime

class Communication(db.Model):
    __tablename__ = 'communication'
    id = db.Column(db.Integer, primary_key=True)
    found_item_id = db.Column(db.Integer, db.ForeignKey('found_item.id'), nullable=True)
    lost_item_id = db.Column(db.Integer, db.ForeignKey('lost_item.id'), nullable=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False, nullable=False)

    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])
    found_item = db.relationship('FoundItem', back_populates='communications')
    lost_item = db.relationship('LostItem', back_populates='communications')

from datetime import datetime
from sqlalchemy.orm import relationship
from ..exts import db

class LostItem(db.Model):
    __tablename__ = 'lost_item'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500))
    category = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    colour = db.Column(db.String(50))
    additional_info = db.Column(db.String(500))
    date_lost = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    location_lost = db.Column(db.String(100), nullable=False)
    lost_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    found_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_found = db.Column(db.Boolean, default=False)
    date_found = db.Column(db.DateTime, nullable=True)

    lost_by = db.relationship('User', foreign_keys=[lost_by_id], back_populates='lost_items')
    found_by = db.relationship('User', foreign_keys=[found_by_id], back_populates='found_lost_items')
    communications = db.relationship('Communication', back_populates='lost_item', cascade='all, delete-orphan')
    images = db.relationship('LostImage', backref='lost_item', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<LostItem {self.name}>'


class LostImage(db.Model):
    __tablename__ = 'lost_item_image'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    lost_item_id = db.Column(db.Integer, db.ForeignKey('lost_item.id'), nullable=False)
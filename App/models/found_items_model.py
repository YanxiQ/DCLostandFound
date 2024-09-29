from datetime import datetime
from sqlalchemy.orm import relationship
from ..exts import db

class FoundItem(db.Model):
    __tablename__ = 'found_item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500))
    category = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    colour = db.Column(db.String(50))
    additional_info = db.Column(db.String(500))
    date_found = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    location_found = db.Column(db.String(100), nullable=False)
    found_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    claimed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_claimed = db.Column(db.Boolean, default=False)
    date_claimed = db.Column(db.DateTime, nullable=True)

    found_by = db.relationship('User', foreign_keys=[found_by_id], back_populates='found_items')
    claimed_by = db.relationship('User', foreign_keys=[claimed_by_id], back_populates='claimed_items')
    images = db.relationship('FoundImage', cascade="all, delete-orphan")

    communications = db.relationship('Communication', back_populates='found_item', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<FoundItem {self.name}>'


class FoundImage(db.Model):
    __tablename__ = 'found_item_images'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    found_item_id = db.Column(db.Integer, db.ForeignKey('found_item.id'), nullable=False)

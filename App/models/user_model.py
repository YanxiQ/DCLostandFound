from flask_login import UserMixin
from ..exts import db, login_manager
from ..models.communication_model import Communication

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    student_id = db.Column(db.String(20))
    profile_pic = db.Column(db.String(120), nullable=True, default='default.jpg')
    is_active = db.Column(db.Boolean, default=True)

    lost_items = db.relationship('LostItem', foreign_keys='LostItem.lost_by_id', back_populates='lost_by')
    found_lost_items = db.relationship('LostItem', foreign_keys='LostItem.found_by_id', back_populates='found_by')
    found_items = db.relationship('FoundItem', foreign_keys='FoundItem.found_by_id', back_populates='found_by')
    claimed_items = db.relationship('FoundItem', foreign_keys='FoundItem.claimed_by_id', back_populates='claimed_by')

    sent_messages = db.relationship('Communication', foreign_keys='Communication.sender_id', back_populates='sender', lazy='dynamic')
    received_messages = db.relationship('Communication', foreign_keys='Communication.receiver_id', back_populates='receiver', lazy='dynamic')

    forum_posts = db.relationship('ForumPost', back_populates='forum_poster')
    forum_comments = db.relationship('ForumComment', back_populates='user')
    announcements = db.relationship('Announcement', back_populates='author', cascade='all, delete-orphan')

    faqs = db.relationship('FAQ', back_populates='user', cascade='all, delete-orphan')


    @property
    def new_messages_count(self):
        return self.received_messages.filter_by(is_read=False).count()

    @property
    def is_admin(self):
        return self.role == 'Admin'

    def __repr__(self):
        return f'<User {self.firstname}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


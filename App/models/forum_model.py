from datetime import datetime
from ..exts import db

# Association table for many-to-many relationship between Tag and ForumPost
forum_tag = db.Table('forum_tag',
db.Column('post_id', db.Integer, db.ForeignKey('forum_post.id'), primary_key=True),
db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)


class ForumPost(db.Model):
    __tablename__ = 'forum_post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    comments = db.relationship('ForumComment', back_populates='post', cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary=forum_tag, back_populates='posts')

    forum_poster = db.relationship('User', back_populates='forum_posts')


class ForumComment(db.Model):
    __tablename__ = 'forum_comment'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_post.id'), nullable=False)

    user = db.relationship('User', back_populates='forum_comments')
    post = db.relationship('ForumPost', back_populates='comments')


class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    posts = db.relationship('ForumPost', secondary=forum_tag, back_populates='tags')

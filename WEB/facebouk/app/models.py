from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    gender = db.Column(db.String(16), nullable=False, default='Unknown')
    birthday = db.Column(db.Date, nullable=True)

    profile_pic_url = db.Column(db.String(512), nullable=True)
    cover_quote = db.Column(db.String(255), nullable=True)

    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    posts_authored = db.relationship(
        'Post', foreign_keys='Post.author_id',
        back_populates='author', cascade='all, delete-orphan'
    )
    posts_received = db.relationship(
        'Post', foreign_keys='Post.target_user_id',
        back_populates='target_user', cascade='all, delete-orphan'
    )
    comments_authored = db.relationship(
        'Comment', foreign_keys='Comment.author_id',
        back_populates='author', cascade='all, delete-orphan'
    )
    friendships_1 = db.relationship(
        'Friendship', foreign_keys='Friendship.user_id_1',
        back_populates='user1', cascade='all, delete-orphan'
    )
    friendships_2 = db.relationship(
        'Friendship', foreign_keys='Friendship.user_id_2',
        back_populates='user2', cascade='all, delete-orphan'
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    target_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)

    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(512), nullable=True)  # Optional image path/URL for "Photo"-style posts.

    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    likes_count = db.Column(db.Integer, default=0, nullable=False)

    author = db.relationship('User', foreign_keys=[author_id], back_populates='posts_authored')
    target_user = db.relationship('User', foreign_keys=[target_user_id], back_populates='posts_received')
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan', order_by='Comment.timestamp.asc()')


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    post = db.relationship('Post', back_populates='comments')
    author = db.relationship('User', back_populates='comments_authored')


class Friendship(db.Model):
    __tablename__ = 'friendships'

    user_id_1 = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    user_id_2 = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)

    status = db.Column(db.String(16), nullable=False, default='pending', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user1 = db.relationship('User', foreign_keys=[user_id_1], back_populates='friendships_1')
    user2 = db.relationship('User', foreign_keys=[user_id_2], back_populates='friendships_2')

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class PlaceBubble(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feeds = db.relationship('PlaceFeed', backref='place_bubble', lazy=True)
    tags = db.relationship('PlaceBubbleTag', backref='place_bubble', lazy=True)
    image_url = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    size_level = db.Column(db.Integer, nullable=False) # 1, 2, 3
    pos_x = db.Column(db.Float, nullable=False)  # New field for x-coordinate
    pos_y = db.Column(db.Float, nullable=False)  # New field for y-coordinate
    pos_z = db.Column(db.Float, nullable=False)  # New field for z-coordinate

    def __repr__(self):
        return f"PlaceBubble('{self.title}', Group ID: {self.group_id}, Image URL: {self.image_url})"
    
    def to_json(self):
        return {
            'id': self.id,
            'image_url': self.image_url,
            'title': self.title,
            'size_level': self.size_level,
            'tags': [tag.to_json() for tag in self.tags],
            'pos_x': self.pos_x,  # Include in JSON representation
            'pos_y': self.pos_y,  # Include in JSON representation
            'pos_z': self.pos_z   # Include in JSON representation
        }

class PlaceBubbleTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bubble_id = db.Column(db.Integer, db.ForeignKey('place_bubble.id'), nullable=False)
    content = db.Column(db.String(50), nullable=False)
    is_advertisement = db.Column(db.Boolean, default=False, nullable=False)
    size_level = db.Column(db.Integer, nullable=False) # 1, 2, 3

    def __repr__(self):
        return f"PlaceBubbleTag('{self.name}', Bubble ID: {self.bubble_id})"
    
    def to_json(self):
        return {
            'id': self.id,
            'bubble_id': self.bubble_id,
            'content': self.content,
            'is_advertisement': self.is_advertisement,
            'size_level': self.size_level
        }

class PlaceFeed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bubble_id = db.Column(db.Integer, db.ForeignKey('place_bubble.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bubble = db.relationship('PlaceBubble', backref='place_feeds', lazy=True)
    user = db.relationship('User', backref='place_feeds', lazy=False)
    tags = db.relationship('PlaceFeedTag', backref='place_feed', lazy=True)
    content = db.Column(db.Text, nullable=False)
    media_url = db.Column(db.String(512), nullable=False)
    media_type = db.Column(db.String(10), nullable=False) # image, video
    is_advertisement = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    view_count = db.Column(db.Integer, nullable=False, default=0)
    like_count = db.Column(db.Integer, nullable=False, default=0)
    is_liked = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"PlaceFeed('{self.title}', '{self.content[:20]}...', Item ID: {self.item_id}, Advertisement: {self.is_advertisement}, User ID: {self.user_id})"
    
    def to_json(self):
        return {
            'id': self.id,
            'bubble_id': self.bubble_id,
            'user': self.user.to_json(),
            'content': self.content,
            'media_url': self.media_url,
            'media_type': self.media_type,
            'is_advertisement': self.is_advertisement,
            'created_at': self.created_at.isoformat(),
            'view_count': self.view_count,
            'like_count': self.like_count,
            'is_liked': self.is_liked,
            'tags': [tag.to_json() for tag in self.tags]
        }

class PlaceFeedTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feed_id = db.Column(db.Integer, db.ForeignKey('place_feed.id'), nullable=False)
    feed = db.relationship('PlaceFeed', backref='feed_tags', lazy=True)
    content = db.Column(db.String(50), nullable=False)
    is_advertisement = db.Column(db.Boolean, default=False, nullable=False)

    def to_json(self):
        return {
            'id': self.id,
            'content': self.content,
            'is_advertisement': self.is_advertisement
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feeds = db.relationship('PlaceFeed', backref='user_profile', lazy=True)
    username = db.Column(db.String(150), unique=False, nullable=False)
    profile_image_url = db.Column(db.String(512), nullable=False)
    is_sponsor = db.Column(db.Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    
    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'profile_image_url': self.profile_image_url,
            'is_sponsor': self.is_sponsor
        }
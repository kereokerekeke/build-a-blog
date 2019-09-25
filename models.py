from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    posts = db.relationship('Post', backref='blog')
    
    def __init__(self, title):
        self.title = title


class Post(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(450))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    created_by = db.Column(db.Integer,
                           db.ForeignKey('user.id'))
    blog_id = db.Column(db.Integer, 
                        db.ForeignKey('blog.id'))
    
    def __init__(self, title, body, blog_id, created_by):
        self.title = title
        self.body = body
        self.blog_id = blog_id
        self.created_by = created_by
    

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    posts = db.relationship('Post', backref='owner')

    def __init__(self, email, password, username):
        self.email = email
        self.password = password
        self.username = username
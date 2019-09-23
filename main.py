from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:totesnotcia@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'WhatisloveBabydonthurtmeDonthurtmeNomore'


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
    blog_id = db.Column(db.Integer, 
                        db.ForeignKey('blog.id'))
    
    def __init__(self, title, body, blog_id):
        self.title = title
        self.body = body
        self.blog_id = blog_id


@app.route('/blog')
def blog():
    
    blog_id = request.args.get('blog_id')
    posts = Post.query.filter_by(blog_id=blog_id).order_by(Post.created_at).all()
    
    return render_template('blog.html', 
                           title='Blog',
                           posts=posts,
                           blog_id=blog_id)
    

@app.route('/post')
def post():
    
    post_id = request.args.get('post_id')
    post = Post.query.filter_by(id=post_id).first()
    
    return render_template('post.html', 
                           title='post',
                           post=post)


@app.route('/newpost', methods=['GET', 'POST'])
def new_post():
    
    blog_id = request.args.get('blog_id')
    
    if request.method == 'POST':
        post_title = request.form['title']
        post_body = request.form['body']
        new_post = Post(post_title, post_body, blog_id)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/post?post_id={post_id}'.format(post_id=new_post.id))
        
    return render_template('newpost.html',
                           title='Add post',
                           blog_id=blog_id)


@app.route('/newblog', methods=['GET', 'POST'])
def new_blog():
    
    if request.method == 'POST':
        blog_title = request.form['title']
        new_blog = Blog(blog_title)
        
        if blog_title:
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/')
        else:
            return redirect('/newblog')
        # TODO - flash message with error
        
        
    return render_template('newblog.html',
                           title='Add blog')


@app.route('/')
def blogs():
    
    blogs = Blog.query.all()
    
    return render_template('blogs.html',
                          blogs=blogs)


if __name__ == '__main__':
    app.run()
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



def check_validity(type, string):

    error = False

    if (string != ''):
        if (' ' in string) or (3 > len(string) or len(string) > 21):
            error = True
        if type == 'Email' and ((string.count('@') != 1) or (string.count('.') != 1)):
            error = True
    elif type != 'Email':
        error = True
    
    if error:
        return type + ' not valid' 
    else:
        return ''

    
@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')
    
    
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method =='POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in", category="alert-success")
            return redirect('/')
        else:
            flash('User password is incorrect or user does not exist', category="alert-danger")
            pass

    return render_template('login.html')    
    
    
@app.route('/logout')
def logout():

    del session['email']
    return redirect('/')    
    
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    
    username_error = ''
    password_error = ''
    verify_error = ''
    email_error = ''
    username = ''
    email = ''

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - put the server-side validation in

        username_error = check_validity('Username', username)
        password_error = check_validity('Password', password)
            
        if verify != password:
            verify_error = 'Passwords do not match'

        email_error = check_validity('Email', email)
        
        if not username_error and not password_error and not verify_error and not email_error:
            pass
        else:
            for error in [username_error, password_error, verify_error, email_error]:
                if error:
                    flash(error, category="alert-danger")
                    return redirect('/')

        existing_user = User.query.filter_by(email=email).first()

        if not existing_user:
            new_user = User(email, password, username)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            # TODO duplicate user
            pass 

    return render_template('register.html')    
    
    
@app.route('/blog')
def blog():
    
    blog_id = request.args.get('blog_id')
    
    posts = db.session.query(Post).filter_by(blog_id=blog_id).join(User).add_columns(Post.title, 
                                                                                     Post.id, 
                                                                                     Post.body, 
                                                                                     Post.created_at, 
                                                                                     User.username).order_by(Post.created_at).all()

    
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
        created_by = User.query.filter_by(email=session['email']).first()
        new_post = Post(post_title, post_body, blog_id, created_by.id)
        if len(new_post.body) > 450:
            flash('Body of the post can not be longer than 450 characters', category='alert-danger')
            return redirect('/newpost?blog_id={blog_id}'.format(blog_id=blog_id))
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


@app.route('/delete_post', methods=['GET', 'POST'])
def delete_post():
    if request.method == 'POST':
        post_id = request.form['post_id']
        post = Post.query.filter_by(id=post_id).first()
        blog_id = post.blog_id
        db.session.delete(post)
        db.session.commit()
        return redirect('/blog?blog_id={blog_id}'.format(blog_id=blog_id))
    

@app.route('/delete_blog', methods=['GET', 'POST'])
def delete_blog():
    if request.method == 'POST':
        blog_id = request.form['blog_id']
        blog = Blog.query.filter_by(id=blog_id).first()
        db.session.delete(blog)
        db.session.commit()
        return redirect('/')
    
@app.route('/update_post', methods=['GET', 'POST'])
def update_post():
    
    post_id = request.args.get('post_id')
    
    if request.method == 'POST':
        post = Post.query.filter_by(id=post_id).first()
        print(post_id)
        post.title = request.form['title']
        post.body = request.form['body']
        db.session.commit()
        flash('Post updated', category="alert-success")
        return redirect('/post?post_id={post_id}'.format(post_id=post_id))
    else:
        
        return render_template('newpost.html',
                            update=True,
                            post_id=post_id)
    

@app.route('/')
def blogs():
    
    blogs = Blog.query.all()
    
    return render_template('blogs.html',
                          blogs=blogs)


if __name__ == '__main__':
    app.run()
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:pass@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

    def __repr__(self):
        return '<Title %r>' % self.title

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

# blog page
@app.route('/blog')
def blog():
    blog_id = request.args.get('id')
    if(blog_id):
        blog = Blog.query.get(blog_id)
        return render_template('blog.html', blog = blog)

    blog_list = Blog.query.all()
    return render_template('blog.html', blog_list = blog_list)

# adds a new post page
@app.route('/newpost', methods = ['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        title_error = ''
        body_error = ''
        owner = User.query.filter_by(username = session['username']).first()
        if title == '' or body == '':
            if title == '':
                title_error = 'You have not added a Title for you Blog.'
            if body == '':
                body_error = 'You have not added a Body for your Blog.'
            return render_template('newpost.html',title = title, body = body, title_error = title_error, body_error = body_error)

        blog = Blog(title = title, body = body, owner = owner)
        db.session.add(blog)
        db.session.commit()
        return redirect('/blog?id='+str(blog.id))
    else:
        return render_template('newpost.html')

# signup page
@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        users = User.query.filter_by(username = username).first()

        if not username or not password or not verify:
            flash('One or more of the fields are empty.')
       
        elif users:
            flash('That username already exists') 

        elif password != verify:
            flash('The passwords does not seem to match')

        elif len(username) < 3 or len(password) < 3:
            flash('username and password have to be 3 characters or more')

        else:
            user = User(username = username, password = password)
            db.session.add(user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
    
    else:
        return render_template('signup.html')

# login page
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username = username).first()
        if user:
            if password == user.password:
                session['username'] = username
                return redirect('/newpost')
            else:
                flash('password incorrect')
                return redirect('/login')
        flash('username does not exist')
        return redirect('/login')
    else:
        return render_template('login.html')

# logout the user
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/blog')

#allowed routes
allowed_routes = ['login', 'blog', 'index', 'signup', 'logout', 'newpost']
@app.before_request
def require_login():
    if 'user' not in session and request.endpoint not in allowed_routes:
        return redirect('/login')

# home page
@app.route('/', methods = ['GET'])
def index():
    if request.method == 'GET':
        username = request.args.get('user')
        user = User.query.filter_by(username = username).first()
        if(username):
            blog_list = Blog.query.filter_by(owner_id = user.id).all()
            return render_template('blog.html', username = username, blog_list = blog_list)

    user_list = User.query.all()

    return render_template('index.html', user_list = user_list)



if __name__ == "__main__":
    app.run()



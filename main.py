from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:pass@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

    def __repr__(self):
        return '<Title %r>' % self.title

# main page
@app.route('/blog')
def index():
    blog_id = request.args.get('id')
    if(blog_id):
        blog = Blog.query.get(blog_id)
        return render_template('blog.html', blog = blog)

    blog_list = Blog.query.all()
    return render_template('blog.html', blog_list = blog_list)

@app.route('/newpost', methods = ['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        title_error = ''
        body_error = ''
        if title == '' or body == '':
            if title == '':
                title_error = 'You have not added a Title for you Blog.'
            if body == '':
                body_error = 'You have not added a Body for your Blog.'
            return render_template('newpost.html',title = title, body = body, title_error = title_error, body_error = body_error)

        blog = Blog(title = title, body = body)
        db.session.add(blog)
        db.session.commit()
        return redirect('/blog?id='+str(blog.id))
    else:
        return render_template('newpost.html')

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

if __name__ == "__main__":
    app.run()


#blog?id={{blog.id}}
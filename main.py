from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:root@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(9999))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog', methods=['GET','POST'])
def blog():
    blogs = Blog.query.all()
    id = request.args.get('id')
    if id and id != '':
        blog_id = request.args.get(Blog.id)
        blog = Blog.query.get(id)
        return render_template('individual_blog.html', title=blog.title, body=blog.body)
    else:
        return render_template('blogs.html', blogs=blogs)


@app.route('/new_post', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        new_blog = Blog(title, body)
        db.session.add(new_blog)
        db.session.commit()
        blog_id = len(Blog.query.all())
        blog = Blog.query.get(blog_id)
        return render_template('individual_blog.html', title=blog.title, body=blog.body)

    return render_template('new_post.html')

if __name__ == '__main__':
    app.run()
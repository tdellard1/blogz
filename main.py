from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:root@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '8uh65fvjko097Hg5'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(9999))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True)
    password = db.Column(db.String(60))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

def valid(text):
    if len(text) >= 3 and len(text) <= 20:
        for char in text:
            if char == "":
                return  "Field should contain no space"
            else:
                return ''
    else:
        return "Field isn't correct length."
    
def empty(text):
    if text == '':
        return 'Field is empty'
    else:
        return ''



@app.route('/blog', methods=['GET','POST'])
def blog():
    blogs = Blog.query.all()
    id = request.args.get('id')
    user = request.args.get('user')
    if user and user != '':
        blog_total = Blog.query.filter_by(owner_id=user).all()
        blog_id = request.args.get('blog.id')
        return render_template('singleUser.html', blog_total=blog_total)
    if id and id != '':
        blog_id = request.args.get(Blog.id)
        blog = Blog.query.get(id)
        user = User.query.get(id)
        return render_template('individual_blog.html', title=blog.title, body=blog.body, owner=user.username)
    # - default '/blog' route
    return render_template('blogs.html', blogs=blogs)
    


@app.route('/new_post', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        new_blog = Blog(title, body, owner)
        db.session.add(new_blog)
        db.session.commit()
        blog_id = len(Blog.query.all())
        blog = Blog.query.get(blog_id)
        return redirect('/blog?id={0}'.format(blog_id))

    return render_template('new_post.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        vpassword = request.form['vpassword']
        if not empty(username):
            if not valid(username):
                if not empty(password):
                    if not valid(password):
                        if not empty(vpassword):
                            new_user = User(username,password)
                            registered_user = User.query.filter_by(username=username).first()
                            if username != registered_user:
                                if password == vpassword:
                                    db.session.add(new_user)
                                    db.session.commit()
                                    session['username'] = username
                                    return redirect('/new_post')
                                else:
                                    flash('Passwords do not match')
                                    return redirect('/signup')
                            else:
                                flash('Username already exists')
                                return redirect('/signup')
                        else:
                            flash('Verified password empty')
                            return redirect('/signup')
                    else:
                        flash('Password is not valid')
                        return redirect('/signup')
                else:
                    flash('Password is empty')
                    return redirect('/signup')
            else:
                flash('Username is not valid')
                return redirect('/signup')
        else:
            flash('Username is empty')
            return redirect('/signup')
    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session ['username'] = username
            return redirect('/new_post')
        elif user and user.password != password:
            flash("Password is incorrect")
            return redirect('/login')
        elif not user:
            flash("User does not exist")
            return redirect('/login')
    return render_template('login.html')

@app.route('/')
def index():
    authors = User.query.all()
    return render_template('index.html', authors=authors) 

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    del session['username']
    return redirect('/blog')


if __name__ == '__main__':
    app.run()
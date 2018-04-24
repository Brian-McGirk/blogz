from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcyAs&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(120))
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, userName, password):
        self.userName = userName
        self. pw_hash = make_pw_hash(password)


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')        


@app.route("/logout", methods=['POST', 'GET'])
def logout():
    del session['username']
    return redirect("/blog")


@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
 
        existing_user = User.query.filter_by(userName=username).first()

        name_error = ""
        password_error = ""
        match_error = ""
        email_error = ""
          
        if not username:
            name_error = "You must enter a Username"
        elif " " in username or len(username) < 3 or len(username) > 20:
            name_error = "That's not a valid Username"
            user_name = ""
        elif existing_user:
            name_error = "That user already exists"
            existing_user = ""
           
        if not password:
            password_error = "You must enter a Password"
        elif " " in password or len(password) < 3 or len(password) > 20:
            password_error = "Thats not a valid Password"

        if not verify or password != verify:
            match_error = "Passwords don't match"
            
                                 
        if not name_error and not password_error and not match_error and not email_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            return render_template("signup.html", title="Signup",name_error=name_error, password_error=password_error, match_error=match_error, email_error=email_error, username=username)

    return render_template('signup.html', title="Sign up")


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(userName=username).first()

        user_error = ""
        password_error = ""

        if not user:
            user_error = "That user doesn't exist"
            username = ""
            return render_template("login.html", user_error=user_error)
        if not check_pw_hash(password, user.pw_hash):
            password_error = "Incorrect password"
            return render_template("login.html", user_error=user_error, password_error=password_error, username=username)

        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            return redirect('/newpost')

            
    return render_template('login.html', title="Log in")


@app.route("/")
def index():
    users = User.query.all()
    return render_template('index.html', users=users, session=session)


@app.route("/blog", methods=['POST', 'GET'])
def blog():
    blog_id = request.args.get('id')
    user_id = request.args.get('user')
    
    if blog_id:
        blogs = Blog.query.filter_by(id=blog_id).first()
        return render_template('entries.html', blogs=blogs)
    if user_id:
        blogs = Blog.query.filter_by(owner_id=user_id).all()
        user = User.query.filter_by(id=user_id).first()
        return render_template('singleUser.html', blogs=blogs, user=user, session=session)

    blogs = Blog.query.all()
    
    
    return render_template("blog.html", blogs=blogs, session=session)


@app.route("/newpost", methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':

        blog_title = request.form['title']
        blog_body = request.form['body']

        title_error = ""
        body_error = ""
        
        if not blog_title:
            title_error = "Please fill out the title"
        if not blog_body:
            body_error = "Please fill out the body"
        if not title_error and not body_error:
            owner = User.query.filter_by(userName=session['username']).first()
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect("/blog?id={0}".format(new_blog.id))
        else:
            return render_template("/new_post.html", title_error=title_error, body_error=body_error, blog_title=blog_title, blog_body=blog_body, session=session)

    return render_template("/new_post.html", session=session)
            
if __name__ == '__main__':    
    app.run()
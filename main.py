from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

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
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    # TODO - Finish
    pass

@app.route("/signup")
def signup():
    # TODO - Finish
    pass

@app.route("/login")
def login():
    # TODO - Finish
    pass

@app.route("/index")
def index():
    # TODO - Finish
    pass

@app.route("/logout", methods=['POST'])
def logout():
    # TODO - del user from session
    return redirect("/blog")

@app.route("/blog", methods=['POST', 'GET'])
def blog():
    blog_id = request.args.get('id')
    
    if blog_id:
        blogs = Blog.query.filter_by(id=blog_id).first()
        return render_template('entries.html', blogs=blogs)

    blogs = Blog.query.all()
    
    return render_template("blog.html", blogs=blogs)
    



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
            owner = User.query.filter_by(email=session['email']).first()
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect("/blog?id={0}".format(new_blog.id))
        else:
            return render_template("/new_post.html", title_error=title_error, body_error=body_error, blog_title=blog_title, blog_body=blog_body)

    return render_template("/new_post.html")
            
if __name__ == '__main__':    
    app.run()
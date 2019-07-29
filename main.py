from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'o4538208O'

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(15000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

@app.before_request 
def require_login(): 
    allowed_routes = ['login', 'blog', 'index', 'signup'] 
    if request.endpoint not in allowed_routes and 'username' not in session: 
        return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)
    
@app.route('/login', methods=['POST', 'GET'])
def login():
    username_error = ''
    password_error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if username == '':
            username_error = 'Please enter a valid username'
            return render_template('login.html', username_error=username_error)
         
        if password == '':
            password_error = 'Please enter a valid password'
            return render_template('login.html', password_error=password_error)
        
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
    
        else:
            username_error = 'User does not exist. Please signup.'
            return render_template('login.html', username_error=username_error)
        
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    username_error = ''
    verify_error = ''
    password_error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
         
        existing_user = User.query.filter_by(username=username).first()
        
        if username == '': 
            username_error = 'Please enter a valid email'
            return render_template('signup.html', username_error=username_error)
        
        if len(username) < 5:
            username_error = 'Please enter a valid username'
            return render_template('signup.html', username_error=username_error)

        if password == '':
            password_error = 'Please enter a valid password'
            return render_template('signup.html', password_error=password_error)

        if len(password) < 3:
            password_error = "Password must be longer than 3 characters"
            return render_template('signup.html', password_error=password_error)
        
        if verify == '':    
            verify_error = 'Please verify password'
            return render_template('signup.html', verify_error=verify_error)
        
        if not verify == password:
            verify_error = 'Your passwords do not match'
            return render_template('signup.html', verify_error=verify_error) 
        
        if existing_user:
            username_error = 'This user already exists. Please login.'
            return render_template('login.html', username_error=username_error)
        
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
   
    return render_template('signup.html')


@app.route('/blog')
def blog():
    id = request.args.get('id')
    user = request.args.get('username')
    users = User.query.all()

    if id:
        blog = Blog.query.get(id)
        return render_template('indivblog.html', blog=blog)

    if user:
        blogs = Blog.query.filter_by(owner_id=user).all()
        username = User.query.filter_by(id=user).first()
        return render_template('indivuser.html', blogs=blogs, user=username)

    else:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)   


@app.route('/newpost', methods=['GET', 'POST'])
def new_post():
    title_error = ''
    body_error = ''

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        

        if title == '':
            title_error = "Please enter a title!"
            return render_template('newpost.html', title_error=title_error)
        
        if body == '':
            body_error = "Please enter some fascinating text!"
            return render_template('newpost.html', body_error=body_error)

        else:
            blog = Blog(title, body, owner)
            db.session.add(blog)
            db.session.commit()
            return redirect('/blog?id=' + str(blog.id))

    return render_template('newpost.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


if __name__ == '__main__':
    app.run()
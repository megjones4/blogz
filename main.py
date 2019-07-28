from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'o4538208O'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(15000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/', methods=['POST', 'GET'])
def index():
    blogs = Blog.query.all()
    return render_template("blog.html", blogs=blogs)
        
@app.route('/blog', methods=['POST', 'GET'])
def blog():

    if request.args:
        id = request.args.get('id')
        blog = Blog.query.get(id)

        return render_template('blog.html', blog=blog)

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
        

        if title == '':
            title_error = "Please enter a title!"
            return render_template('newpost.html', title_error=title_error)
        
        if body == '':
            body_error = "Please enter some fascinating text!"
            return render_template('newpost.html', body_error=body_error)

        else:
            blog = Blog(title, body)
            db.session.add(blog)
            db.session.commit()
            return redirect('/blog')

    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()
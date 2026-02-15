from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'copp.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Article %r>' % self.id

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/news')
def news():
    news = Article.query.order_by(Article.date.desc()).all()

    return render_template("news.html",news=news)


@app.route('/create-news',methods=['GET', 'POST'])
def create_news():
    if request.method == 'POST':
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']

        article = Article(title=title,intro=intro,text=text)
        print(intro,title)
        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/news')
        except Exception as e:
            print(e)  # покажет причину ошибки в консоли
            return f"ERROR: {e}"
    else:
        return render_template('create-news.html')


if __name__ == "__main__":
    app.run(debug=True)
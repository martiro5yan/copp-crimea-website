# check_news.py
import os
from flask import Flask
from models import db, Article

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, "copp.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    articles = Article.query.order_by(Article.date.desc()).all()
    print(f"Всего новостей: {len(articles)}\n")
    for a in articles:
        print(f"ID: {a.id}")
        print(f"Заголовок: {a.title}")
        print(f"Краткое описание: {a.intro}")
        print(f"Текст: {a.text[:50]}...")
        print(f"Превью: {a.preview_image}")
        print('-'*40)
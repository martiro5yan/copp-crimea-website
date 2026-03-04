from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from katy_mode import katy_bp
from models import db, Article
import os
from dotenv import load_dotenv

# Загрузка .env
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["ADMIN_LOGIN"] = os.getenv("ADMIN_LOGIN")
app.config["ADMIN_PASSWORD"] = os.getenv("ADMIN_PASSWORD")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "copp.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Регистрируем админку
app.register_blueprint(katy_bp)

# Публичные маршруты
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/news")
def news():
    news_list = Article.query.order_by(Article.date.desc()).all()
    return render_template("news.html", news=news_list)

@app.route("/news/<int:id>")
def news_detail(id):
    article = Article.query.get_or_404(id)
    return render_template("posts.html", article=article)

# Создаём таблицы (один раз)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
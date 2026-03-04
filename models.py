from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Создаём экземпляр SQLAlchemy БЕЗ app
# (инициализация будет в app.py)
db = SQLAlchemy()


# =========================
# Модель статьи
# =========================
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    intro = db.Column(db.String(500), nullable=False)
    text = db.Column(db.Text, nullable=False)
    preview_image = db.Column(db.String(255), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    images = db.relationship(
        'ArticleImage',
        backref='article',
        lazy=True
    )


# =========================
# Модель изображений статьи
# =========================
class ArticleImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255), nullable=False)

    article_id = db.Column(
        db.Integer,
        db.ForeignKey('article.id'),
        nullable=False
    )
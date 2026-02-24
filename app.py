import os
import uuid
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
from katy_mode import katy_bp  # твой файл с /katy-mode и /logout

# --- Настройка Flask ---
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Конфиг базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'copp.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Загрузка файлов
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Секретный ключ и пароль админа
app.secret_key = 'supersecretkey123'
app.config['ADMIN_PASSWORD'] = '1'

# --- Инициализация базы ---
db = SQLAlchemy(app)

# --- Подключаем Blueprint для katy-mode ---
app.register_blueprint(katy_bp)


# --- Функции ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --- Модели ---
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    intro = db.Column(db.String(500), nullable=False)
    text = db.Column(db.Text, nullable=False)
    preview_image = db.Column(db.String(255), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    images = db.relationship('ArticleImage', backref='article', lazy=True)


class ArticleImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)


# --- Маршруты ---
@app.route('/')
def index():
    return render_template("index.html")


@app.route('/news')
def news():
    news = Article.query.order_by(Article.date.desc()).all()
    return render_template("news.html", news=news)


@app.route('/create-news', methods=['GET', 'POST'])
def create_news():
    if request.method == 'POST':
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']

        # превью
        preview = request.files['preview_image']
        preview_filename = None
        if preview and allowed_file(preview.filename):
            filename = secure_filename(preview.filename)
            unique_name = str(uuid.uuid4()) + "_" + filename
            preview.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_name))
            preview_filename = f'uploads/{unique_name}'

        article = Article(title=title, intro=intro, text=text, preview_image=preview_filename)
        db.session.add(article)
        db.session.commit()

        # дополнительные картинки
        images = request.files.getlist("images")
        for image in images:
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                unique_name = str(uuid.uuid4()) + "_" + filename
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_name))

                article_image = ArticleImage(
                    image_path=f'uploads/{unique_name}',
                    article_id=article.id
                )
                db.session.add(article_image)
        db.session.commit()

        return redirect('/news')

    return render_template('create-news.html')


@app.route('/news/<int:id>')
def news_detail(id):
    article = Article.query.get_or_404(id)
    return render_template("posts.html", article=article)


# --- Запуск ---
if __name__ == "__main__":
    app.run(debug=True)
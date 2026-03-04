# katy_mode.py
from flask import Blueprint, render_template, request, redirect, session, current_app
from functools import wraps
from models import db, Article, ArticleImage
import os, uuid
from werkzeug.utils import secure_filename

# Разрешённые расширения и папка для загрузки
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Создаём Blueprint
katy_bp = Blueprint("katy_bp", __name__, url_prefix="/katy-mode")

# --------------------------
# Декоратор авторизации
# --------------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect("/katy-mode/login")
        return f(*args, **kwargs)
    return decorated

# --------------------------
# Вход
# --------------------------
@katy_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")
        if login == current_app.config["ADMIN_LOGIN"] and password == current_app.config["ADMIN_PASSWORD"]:
            session["admin_logged_in"] = True
            return redirect("/katy-mode/dashboard")
        else:
            return render_template("katy-mode-login.html", error="Неверный логин или пароль")
    return render_template("katy-mode-login.html")

# --------------------------
# Главная админки
# --------------------------
@katy_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("katy-mode.html")

# --------------------------
# Модуль "Создать новость" — возвращает HTML формы
# --------------------------
@katy_bp.route("/module/create-news")
@login_required
def module_create_news():
    return render_template("modules/create-news.html")

# --------------------------
# Создание новости — только POST
# --------------------------
@katy_bp.route("/create-news", methods=["POST"])
@login_required
def create_news():
    print("=== Новый запрос на создание новости ===")
    print("Form:", request.form)
    print("Files:", request.files)

    title = request.form.get('title')
    intro = request.form.get('intro')
    text = request.form.get('text')

    if not title or not intro or not text:
        return "Ошибка: заполните все поля", 400

    # Превью
    preview_filename = None
    preview = request.files.get('preview_image')
    if preview and allowed_file(preview.filename):
        filename = secure_filename(preview.filename)
        unique_name = f"{uuid.uuid4()}_{filename}"
        preview.save(os.path.join(UPLOAD_FOLDER, unique_name))
        preview_filename = f'uploads/{unique_name}'

    # Создаём статью
    article = Article(title=title, intro=intro, text=text, preview_image=preview_filename)
    db.session.add(article)
    db.session.commit()
    print(f"Создана статья ID={article.id}, title={article.title}")

    # Доп. картинки
    images = request.files.getlist('images')
    for image in images:
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            unique_name = f"{uuid.uuid4()}_{filename}"
            image.save(os.path.join(UPLOAD_FOLDER, unique_name))
            article_image = ArticleImage(image_path=f'uploads/{unique_name}', article_id=article.id)
            db.session.add(article_image)
    db.session.commit()
    print(f"Добавлено {len(images)} изображений к статье ID={article.id}")

    # Ответ AJAX
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return "Новость успешно создана!"

    return redirect('/news')

# ===== МОДУЛЬ НОВОСТЕЙ =====
@katy_bp.route('/module/news')
@login_required
def module_news():
    """
    Модуль "Новости" для админки SPA.
    Возвращает HTML с новостями.
    """
    from models import Article
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template("modules/news.html", news=articles)
# --------------------------
# Выход
# --------------------------
@katy_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return redirect("/")
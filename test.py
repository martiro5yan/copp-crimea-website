from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///copp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Простейшие настройки для картинок
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Создаем папку для картинок
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# ОЧЕНЬ ПРОСТАЯ модель с картинкой
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    image = db.Column(db.String(200))  # тут просто храним имя файла

# Проверка расширения файла
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Главная страница - показать все записи
@app.route('/')
def index():
    items = Item.query.all()
    return render_template('test.html', items=items)

# Добавление записи с картинкой
@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        
        # Сохраняем картинку
        image = request.files['image']
        image_filename = None
        
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_filename = filename
        
        # Создаем запись в БД
        new_item = Item(name=name, image=image_filename)
        db.session.add(new_item)
        db.session.commit()
        
        return redirect('/')
    
    return render_template('add.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
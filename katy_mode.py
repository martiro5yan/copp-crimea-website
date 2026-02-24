from flask import Blueprint, render_template, request, redirect, session, current_app as app
from functools import wraps

# Blueprint
katy_bp = Blueprint('katy_mode', __name__, template_folder='templates')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            return redirect('/katy-mode')
        return f(*args, **kwargs)
    return decorated_function

@katy_bp.route('/katy-mode', methods=['GET','POST'])
def katy_mode_login():
    if 'logged_in' in session and session['logged_in']:
        return render_template('katy-mode.html')

    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == app.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            return redirect('/katy-mode')
        else:
            error = 'Неверный пароль'

    return render_template('katy-mode-login.html', error=error)

@katy_bp.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    return redirect('/katy-mode')
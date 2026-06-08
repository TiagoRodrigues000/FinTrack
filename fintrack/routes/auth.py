from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Category

auth_bp = Blueprint('auth', __name__)

DEFAULT_CATEGORIES = [
    ('Salário',       'briefcase',     '#27AE60', 'income'),
    ('Freelance',     'laptop',        '#2ECC71', 'income'),
    ('Investimentos', 'trending-up',   '#1ABC9C', 'income'),
    ('Outros',        'plus-circle',   '#3498DB', 'income'),
    ('Alimentação',   'utensils',      '#E74C3C', 'expense'),
    ('Transporte',    'car',           '#E67E22', 'expense'),
    ('Moradia',       'home',          '#9B59B6', 'expense'),
    ('Saúde',         'heart',         '#E91E63', 'expense'),
    ('Lazer',         'smile',         '#F39C12', 'expense'),
    ('Educação',      'book',          '#3498DB', 'expense'),
    ('Compras',       'shopping-bag',  '#1ABC9C', 'expense'),
    ('Outros',        'tag',           '#95A5A6', 'expense'),
]

@auth_bp.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        name     = request.form.get('name','').strip()
        email    = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        confirm  = request.form.get('confirm','')
        if not name or not email or not password:
            flash('Preencha todos os campos.', 'error')
            return render_template('register.html')
        if password != confirm:
            flash('As senhas não coincidem.', 'error')
            return render_template('register.html')
        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('E-mail já cadastrado.', 'error')
            return render_template('register.html')
        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        for cname, icon, color, ctype in DEFAULT_CATEGORIES:
            db.session.add(Category(name=cname, icon=icon, color=color, type=ctype, user_id=user.id))
        db.session.commit()
        login_user(user)
        flash(f'Bem-vindo, {user.name}! Conta criada com sucesso.', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        email    = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        remember = request.form.get('remember') == 'on'
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            nxt = request.args.get('next')
            return redirect(nxt or url_for('main.dashboard'))
        flash('E-mail ou senha incorretos.', 'error')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('auth.login'))

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, Transaction, Category
from datetime import datetime, date
from sqlalchemy import func, extract
import json

main_bp = Blueprint('main', __name__)

# ── helpers ──────────────────────────────────────────────────────────────────
def _summary(user_id, month=None, year=None):
    q = Transaction.query.filter_by(user_id=user_id)
    if month and year:
        q = q.filter(
            extract('month', Transaction.date) == month,
            extract('year',  Transaction.date) == year
        )
    income  = sum(t.amount for t in q.filter_by(type='income').all())
    expense = sum(t.amount for t in q.filter_by(type='expense').all())
    return income, expense, income - expense

# ── dashboard ─────────────────────────────────────────────────────────────────
@main_bp.route('/')
@main_bp.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    income, expense, balance = _summary(current_user.id, today.month, today.year)

    # last 6 months chart data
    months_data = []
    for i in range(5, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12; y -= 1
        inc, exp, _ = _summary(current_user.id, m, y)
        months_data.append({'month': date(y, m, 1).strftime('%b'), 'income': inc, 'expense': exp})

    # expense by category (current month)
    cat_data = (
        db.session.query(Category.name, Category.color, func.sum(Transaction.amount))
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(Transaction.user_id == current_user.id,
                Transaction.type == 'expense',
                extract('month', Transaction.date) == today.month,
                extract('year',  Transaction.date) == today.year)
        .group_by(Category.id).all()
    )

    # recent transactions
    recent = (Transaction.query
              .filter_by(user_id=current_user.id)
              .order_by(Transaction.date.desc(), Transaction.id.desc())
              .limit(8).all())

    return render_template('dashboard.html',
        income=income, expense=expense, balance=balance,
        months_data=json.dumps(months_data),
        cat_data=json.dumps([{'name':r[0],'color':r[1],'value':r[2]} for r in cat_data]),
        recent=recent,
        today=today
    )

# ── transactions ──────────────────────────────────────────────────────────────
@main_bp.route('/transactions')
@login_required
def transactions():
    page     = request.args.get('page', 1, type=int)
    ttype    = request.args.get('type', '')
    cat_id   = request.args.get('category', 0, type=int)
    month    = request.args.get('month', 0, type=int)
    year     = request.args.get('year',  0, type=int)
    search   = request.args.get('search', '')

    q = Transaction.query.filter_by(user_id=current_user.id)
    if ttype:    q = q.filter_by(type=ttype)
    if cat_id:   q = q.filter_by(category_id=cat_id)
    if month:    q = q.filter(extract('month', Transaction.date) == month)
    if year:     q = q.filter(extract('year',  Transaction.date) == year)
    if search:   q = q.filter(Transaction.description.ilike(f'%{search}%'))

    transactions = q.order_by(Transaction.date.desc(), Transaction.id.desc()).paginate(page=page, per_page=15)
    categories   = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
    today        = date.today()

    return render_template('transactions.html',
        transactions=transactions,
        categories=categories,
        filters={'type': ttype, 'category': cat_id, 'month': month, 'year': year, 'search': search},
        today=today,
        years=list(range(today.year - 3, today.year + 1))
    )

@main_bp.route('/transactions/add', methods=['GET','POST'])
@login_required
def add_transaction():
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
    if request.method == 'POST':
        try:
            desc    = request.form.get('description','').strip()
            amount  = float(request.form.get('amount', 0))
            ttype   = request.form.get('type')
            tdate   = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
            cat_id  = request.form.get('category_id') or None
            notes   = request.form.get('notes','').strip()
            if not desc or amount <= 0 or ttype not in ('income','expense'):
                flash('Dados inválidos.', 'error')
                return render_template('transaction_form.html', categories=categories, today=date.today())
            t = Transaction(description=desc, amount=amount, type=ttype,
                            date=tdate, notes=notes,
                            user_id=current_user.id, category_id=cat_id)
            db.session.add(t); db.session.commit()
            flash('Transação adicionada!', 'success')
            return redirect(url_for('main.transactions'))
        except Exception as e:
            flash('Erro ao salvar.', 'error')
    return render_template('transaction_form.html', categories=categories, today=date.today(), tx=None)

@main_bp.route('/transactions/<int:tx_id>/edit', methods=['GET','POST'])
@login_required
def edit_transaction(tx_id):
    tx = Transaction.query.filter_by(id=tx_id, user_id=current_user.id).first_or_404()
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
    if request.method == 'POST':
        try:
            tx.description  = request.form.get('description','').strip()
            tx.amount       = float(request.form.get('amount', 0))
            tx.type         = request.form.get('type')
            tx.date         = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
            tx.category_id  = request.form.get('category_id') or None
            tx.notes        = request.form.get('notes','').strip()
            db.session.commit()
            flash('Transação atualizada!', 'success')
            return redirect(url_for('main.transactions'))
        except:
            flash('Erro ao atualizar.', 'error')
    return render_template('transaction_form.html', categories=categories, today=date.today(), tx=tx)

@main_bp.route('/transactions/<int:tx_id>/delete', methods=['POST'])
@login_required
def delete_transaction(tx_id):
    tx = Transaction.query.filter_by(id=tx_id, user_id=current_user.id).first_or_404()
    db.session.delete(tx); db.session.commit()
    flash('Transação removida.', 'info')
    return redirect(url_for('main.transactions'))

# ── categories ────────────────────────────────────────────────────────────────
@main_bp.route('/categories')
@login_required
def categories():
    cats = Category.query.filter_by(user_id=current_user.id).order_by(Category.type, Category.name).all()
    return render_template('categories.html', categories=cats)

@main_bp.route('/categories/add', methods=['POST'])
@login_required
def add_category():
    name  = request.form.get('name','').strip()
    icon  = request.form.get('icon','tag')
    color = request.form.get('color','#27AE60')
    ctype = request.form.get('type')
    if name and ctype in ('income','expense'):
        db.session.add(Category(name=name, icon=icon, color=color, type=ctype, user_id=current_user.id))
        db.session.commit()
        flash('Categoria criada!', 'success')
    return redirect(url_for('main.categories'))

@main_bp.route('/categories/<int:cat_id>/delete', methods=['POST'])
@login_required
def delete_category(cat_id):
    cat = Category.query.filter_by(id=cat_id, user_id=current_user.id).first_or_404()
    Transaction.query.filter_by(category_id=cat_id).update({'category_id': None})
    db.session.delete(cat); db.session.commit()
    flash('Categoria removida.', 'info')
    return redirect(url_for('main.categories'))

# ── API for charts ─────────────────────────────────────────────────────────────
@main_bp.route('/api/balance')
@login_required
def api_balance():
    today = date.today()
    income, expense, balance = _summary(current_user.id, today.month, today.year)
    return jsonify({'income': income, 'expense': expense, 'balance': balance})

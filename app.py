import os
import random
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'union_bank_super_secret_key_2026'
# Use SQLite database in the database folder
basedir = os.path.abspath(os.path.dirname(__name__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'bank.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# --- Database Models ---

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(12), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    profile_pic = db.Column(db.String(20), nullable=False, default='default.jpg')
    dark_mode = db.Column(db.Boolean, default=False)
    transactions = db.relationship('Transaction', backref='author', lazy=True, foreign_keys='Transaction.user_id')

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False) # Deposit, Withdraw, Transfer
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.String(200), nullable=False)
    balance_after = db.Column(db.Float, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def generate_account_number():
    while True:
        acc_num = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        if not User.query.filter_by(account_number=acc_num).first():
            return acc_num

# --- Routes ---

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        acc_num = generate_account_number()
        new_user = User(full_name=full_name, email=email, password=hashed_password, account_number=acc_num)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).limit(5).all()
    # Calculate some stats for the charts
    deposits = db.session.query(db.func.sum(Transaction.amount)).filter_by(user_id=current_user.id, type='Deposit').scalar() or 0
    withdrawals = db.session.query(db.func.sum(Transaction.amount)).filter_by(user_id=current_user.id, type='Withdraw').scalar() or 0
    
    return render_template('dashboard.html', recent_transactions=recent_transactions, deposits=deposits, withdrawals=withdrawals)

@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    if request.method == 'POST':
        amount_str = request.form.get('amount')
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash('Invalid amount. Please enter a positive number.', 'danger')
            return redirect(url_for('deposit'))
            
        current_user.balance += amount
        txn = Transaction(user_id=current_user.id, type='Deposit', amount=amount, description='Cash Deposit', balance_after=current_user.balance)
        db.session.add(txn)
        db.session.commit()
        flash(f'Successfully deposited ${amount:,.2f}', 'success')
        return redirect(url_for('dashboard'))
    return render_template('deposit.html')

@app.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    if request.method == 'POST':
        amount_str = request.form.get('amount')
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash('Invalid amount. Please enter a positive number.', 'danger')
            return redirect(url_for('withdraw'))
            
        if amount > current_user.balance:
            flash('Insufficient balance!', 'danger')
        else:
            current_user.balance -= amount
            txn = Transaction(user_id=current_user.id, type='Withdraw', amount=amount, description='Cash Withdrawal', balance_after=current_user.balance)
            db.session.add(txn)
            db.session.commit()
            flash(f'Successfully withdrew ${amount:,.2f}', 'success')
            return redirect(url_for('dashboard'))
    return render_template('withdraw.html')

@app.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    if request.method == 'POST':
        recipient_acc = request.form.get('account_number')
        amount_str = request.form.get('amount')
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash('Invalid amount. Please enter a positive number.', 'danger')
            return redirect(url_for('transfer'))
            
        recipient = User.query.filter_by(account_number=recipient_acc).first()
        
        if not recipient:
            flash('Recipient account not found.', 'danger')
        elif recipient.id == current_user.id:
            flash('You cannot transfer money to yourself.', 'danger')
        elif amount > current_user.balance:
            flash('Insufficient balance!', 'danger')
        else:
            current_user.balance -= amount
            recipient.balance += amount
            
            # Sender transaction
            txn_out = Transaction(user_id=current_user.id, type='Transfer Out', amount=amount, description=f'Transfer to {recipient.full_name}', balance_after=current_user.balance)
            # Receiver transaction
            txn_in = Transaction(user_id=recipient.id, type='Transfer In', amount=amount, description=f'Transfer from {current_user.full_name}', balance_after=recipient.balance)
            
            db.session.add(txn_out)
            db.session.add(txn_in)
            db.session.commit()
            
            flash(f'Successfully transferred ${amount:,.2f} to {recipient.full_name}', 'success')
            return redirect(url_for('dashboard'))
    return render_template('transfer.html')

@app.route('/transactions')
@login_required
def transactions():
    page = request.args.get('page', 1, type=int)
    # Pagination
    pagination = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).paginate(page=page, per_page=10)
    return render_template('transactions.html', pagination=pagination)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        if full_name:
            current_user.full_name = full_name
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
    return render_template('profile.html')

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        dark_mode = request.form.get('dark_mode') == 'on'
        current_user.dark_mode = dark_mode
        db.session.commit()
        flash('Settings updated successfully.', 'success')
        return redirect(url_for('settings'))
    return render_template('settings.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('If an account exists with that email, a password reset link has been sent.', 'info')
        else:
            flash('If an account exists with that email, a password reset link has been sent.', 'info')
        return redirect(url_for('login'))
    return render_template('forgot_password.html')

if __name__ == '__main__':
    # Make sure database directory exists
    os.makedirs(os.path.join(basedir, 'database'), exist_ok=True)
    with app.app_context():
        db.create_all()
    import os

if __name__ == '__main__':
    # Make sure database directory exists
    os.makedirs(os.path.join(basedir, 'database'), exist_ok=True)

    with app.app_context():
        db.create_all()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

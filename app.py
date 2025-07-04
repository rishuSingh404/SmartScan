import os
from flask import Flask, request, render_template, flash, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from scoring import ResumeScorer

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or email already exists')
            return redirect(url_for('register'))
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@login_required
def upload_files():
    if 'files' not in request.files:
        flash('No files selected')
        return redirect(url_for('index'))
    files = request.files.getlist('files')
    uploaded_files = []
    upload_folder = 'files/uploads'
    os.makedirs(upload_folder, exist_ok=True)
    for file in files:
        if file.filename == '':
            continue
        filename = file.filename
        file.save(os.path.join(upload_folder, filename))
        uploaded_files.append(filename)
    if uploaded_files:
        flash(f'Successfully uploaded: {", ".join(uploaded_files)}')
    return redirect(url_for('index'))

@app.route('/process', methods=['POST'])
@login_required
def process_resumes():
    job_description = request.form.get('job_description', '').strip()
    if not job_description:
        flash('Job description is required')
        return redirect(url_for('index'))
    # Here you would add logic to process resumes and score them using ResumeScorer
    flash('Resumes processed and scored! (Demo)')
    return redirect(url_for('index'))

# Auto-create DB if missing
if not os.path.exists('users.db'):
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 
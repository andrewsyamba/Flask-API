from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
import uuid, random, schedule, threading, time

# App configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'my_secret_key'

# Gmail App Password config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey1992@gmail.com'
app.config['MAIL_PASSWORD'] = 'lrqd nbow zxpg lksn'

db = SQLAlchemy(app)
mail = Mail(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    api_key = db.Column(db.String(36), unique=True)

# Usage log model
class UsageLog(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.Date, default=date.today)
    count = db.Column(db.Integer, default=0)
    user = db.relationship('User', backref='usage_logs')

# Create database tables
with app.app_context():
    db.create_all()

# Quotes list
QUOTES = [
    "Believe in yourself.",
    "Success is not final; failure is not fatal.",
    "You are stronger than you think.",
    "Every day is a second chance.",
    "Stay patient and trust your journey."
]

# Registration route
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 400

    hashed_pw = generate_password_hash(password)
    new_user = User(email=email, password_hash=hashed_pw, api_key=str(uuid.uuid4()))
    db.session.add(new_user)
    db.session.commit()

    try:
        msg = Message('Welcome to the Quote API!', sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = f"Hello,\n\nThanks for signing up!\nYour API key is:\n{new_user.api_key}"
        mail.send(msg)
    except Exception as e:
        print("Email send error:", e)

    return jsonify({"message": "Registered successfully", "api_key": new_user.api_key})

# Login route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({"message": "Login successful", "api_key": user.api_key})

# Rotate API Key
@app.route('/rotate-key', methods=['POST'])
def rotate_key():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    user.api_key = str(uuid.uuid4())
    db.session.commit()
    return jsonify({"message": "API key rotated", "new_api_key": user.api_key})

# Quote route
@app.route('/quote', methods=['GET'])
def get_quote():
    api_key = request.headers.get('x-api-key')
    user = User.query.filter_by(api_key=api_key).first()
    if not user:
        return jsonify({"error": "Invalid or missing API key"}), 401

    today = date.today()
    usage = UsageLog.query.filter_by(user_id=user.id, date=today).first()

    if usage and usage.count >= 10:
        return jsonify({"error": "Daily quote limit reached (10 max)"}), 429

    if not usage:
        usage = UsageLog(user_id=user.id, date=today, count=1)
        db.session.add(usage)
    else:
        usage.count += 1

    db.session.commit()

    return jsonify({
        "quote": random.choice(QUOTES),
        "user": user.email,
        "remaining_quotes_today": 10 - usage.count
    })

# Home route
@app.route('/')
def home():
    return "🎉 Welcome to the Quote API. Use POST /register to sign up."

# Email report route
@app.route('/send-report')
def send_daily_report():
    today = date.today()
    usage_logs = UsageLog.query.filter_by(date=today).all()

    if not usage_logs:
        return jsonify({"message": "No usage logs for today."})

    report_lines = ["📅 Daily Quote Usage Report\n"]
    for log in usage_logs:
        report_lines.append(f"- {log.user.email}: {log.count} quotes")

    try:
        msg = Message(
            '📈 Daily API Usage Report',
            sender=app.config['MAIL_USERNAME'],
            recipients=['apikey1992@gmail.com']
        )
        msg.body = "\n".join(report_lines)
        mail.send(msg)
        return jsonify({"message": "Report sent"})
    except Exception as e:
        return jsonify({"error": str(e)})

# Admin dashboard template
dashboard_template = """
<!DOCTYPE html>
<html>
<head><title>Admin Dashboard</title></head>
<body>
    <h1>📊 Admin Dashboard</h1>
    <h2>Registered Users</h2>
    <ul>
        {% for user in users %}
            <li>{{ user.email }} | API Key: {{ user.api_key }}</li>
        {% endfor %}
    </ul>
    <h2>Usage Logs</h2>
    <table border="1">
        <tr>
            <th>User Email</th>
            <th>Date</th>
            <th>Count</th>
        </tr>
        {% for log in logs %}
        <tr>
            <td>{{ log.user.email }}</td>
            <td>{{ log.date }}</td>
            <td>{{ log.count }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# Admin dashboard route
@app.route('/admin')
def admin_dashboard():
    users = User.query.all()
    logs = UsageLog.query.order_by(UsageLog.date.desc()).all()
    return render_template_string(dashboard_template, users=users, logs=logs)

# Background scheduler
def schedule_daily_report():
    schedule.every().day.at("23:59").do(send_report_job)
    while True:
        schedule.run_pending()
        time.sleep(60)

def send_report_job():
    with app.app_context():
        try:
            today = date.today()
            usage_logs = UsageLog.query.filter_by(date=today).all()
            if usage_logs:
                lines = ["📅 Daily Quote Usage Report\n"]
                for log in usage_logs:
                    lines.append(f"- {log.user.email}: {log.count} quotes")

                msg = Message(
                    '📈 Daily API Usage Report',
                    sender=app.config['MAIL_USERNAME'],
                    recipients=['apikey1992@gmail.com']
                )
                msg.body = "\n".join(lines)
                mail.send(msg)
                print("✅ Scheduled report sent.")
        except Exception as e:
            print("❌ Failed to send scheduled report:", str(e))

# Run app and start scheduler
if __name__ == '__main__':
    threading.Thread(target=schedule_daily_report, daemon=True).start()
    app.run(debug=True)

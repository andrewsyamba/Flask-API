# Flask-API
# 💬 Quote API - Powered by Flask

Welcome to the Quote API – a simple, secure, and feature-rich RESTful API built using Python and Flask. This API allows users to register, log in, and retrieve motivational quotes daily, with built-in usage tracking and email reporting. Ideal for developers, learners, or anyone looking to build and consume a lightweight Flask-based API.

---

## 🌟 Key Features

- 🔐 User Authentication – Secure registration and login with hashed passwords
- 🔑 API Key Generation – Each user gets a unique API key after registering
- 📊 **Daily Quote Limits** – Each user is limited to 10 quotes per day
- 📅 **Usage Tracking** – Tracks how many quotes each user accesses per day
- 📬 **Email Notifications** – Sends welcome emails and daily usage reports
- 🖥️ **Admin Dashboard** – Web-based dashboard to monitor users and activity
- 🔁 **API Key Rotation** – Users can reset and update their API keys anytime
- ⏰ **Scheduled Reports** – Daily quote usage reports sent automatically via email

---

## 🧰 Tech Stack

- Python 3
- Flask
- SQLite (via SQLAlchemy ORM)
- Flask-Mail
- Schedule (for background jobs)
- Gunicorn (for production deployment)
- Hosted on [Render](https://render.com)

---

## 🚀 How to Use the API

### 1. Register a New User

POST /register
{
"email": "your@email.com",
"password": "yourpassword"
}

➡️ Returns an API key via email and JSON response.

---

### 2. Login

POST /login
{
"email": "your@email.com",
"password": "yourpassword"
}

yaml
Copy
➡️ Returns login success and API key.

---

### 3. Get a Quote (Max 10 per day)
GET /quote
Headers: x-api-key: your_api_key

yaml
Copy
➡️ Returns a random motivational quote.

---

### 4. Rotate Your API Key
POST /rotate-key
{
"email": "your@email.com",
"password": "yourpassword"
}

yaml
Copy
➡️ Returns a new API key.

---

## 🔒 Security Features

- Encrypted passwords using `werkzeug.security`
- API key authentication via headers
- Usage limits enforced daily
- Safe email delivery via Gmail App Password

---

## 📈 Admin Dashboard

Visit `/admin` to view:
- Registered users and their API keys
- Quote usage logs for each day

---

## 📬 Daily Report

Every night, an email is automatically sent to the admin showing:
- List of users
- Number of quotes accessed today per user

---

## 🌐 Hosting Guide (Render)

### Build and Deployment
- Connect this GitHub repo to your Render account
- Set build and start commands:
  - `Build Command`: `pip install -r requirements.txt`
  - `Start Command`: `gunicorn app:app`

### Environment Variables
Set these in Render:
- `MAIL_USERNAME`: your Gmail address
- `MAIL_PASSWORD`: your 16-character Gmail App Password

---

## 👨🏾‍💻 Author

**Andrew Sahr Yamba**  
Community Health Nurse | Project Manager | Python Developer  
📧 apikey1992@gmail.com

---

## 📜 License

This project is free to use under the MIT License. Contributions are welcome!

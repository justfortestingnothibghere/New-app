from flask import Flask, render_template, request, redirect, session
from supabase import create_client, Client
import smtplib
import random
import socket
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "25e3f77d9bdc90e64fd4e97b78a67022"

# 🟢 Supabase credentials
SUPABASE_URL = "https://buenbdkodjrpzsfjsddu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ1ZW5iZGtvZGpycHpzZmpzZGR1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIwOTM3MjQsImV4cCI6MjA3NzY2OTcyNH0.8AOdXZtF3kaNnJ8dSEpEinD4RZM7GEy-nVtTV3o81B4"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🟡 Email OTP setup
SENDER_EMAIL = "armanhacker900@gmail.com"
SENDER_PASS = "nzvg efkc rdhz jiad"  # your app password

# 🔢 Store OTP temporarily
otp_data = {}

def get_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_otp', methods=['POST'])
def send_otp():
    email = request.form['email']
    name = request.form['name']
    username = request.form['username']
    phone = request.form['phone']
    otp = str(random.randint(100000, 999999))

    otp_data[email] = {"otp": otp, "info": {"name": name, "username": username, "phone": phone}}
    
    # Send OTP via Gmail
    msg = MIMEText(f"Your OTP for login/signup is: {otp}")
    msg['Subject'] = "Your OTP Code"
    msg['From'] = SENDER_EMAIL
    msg['To'] = email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASS)
            smtp.send_message(msg)
        return render_template('otp.html', email=email)
    except Exception as e:
        return f"Error sending OTP: {e}"

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    email = request.form['email']
    entered_otp = request.form['otp']

    if email in otp_data and otp_data[email]['otp'] == entered_otp:
        user_info = otp_data[email]['info']
        ip_address = request.remote_addr or get_ip()

        supabase.table("users").insert({
            "name": user_info['name'],
            "username": user_info['username'],
            "email": email,
            "phone": user_info['phone'],
            "ip_address": ip_address,
            "profile_photo": ""
        }).execute()

        return redirect('/complete')
    else:
        return "Invalid OTP. Please try again."

@app.route('/complete')
def complete():
    return render_template('complete.html')

if __name__ == '__main__':
    app.run(debug=True)

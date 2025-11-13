from flask import Blueprint, request, jsonify
from db_config import get_db_connection
import random
import string
import smtplib
from email.mime.text import MIMEText

login_bp = Blueprint("login", __name__)

EMAIL_ADDRESS = "throwaccp@gmail.com"
EMAIL_PASSWORD = "gtguaajgwkjknemq"

def init_user_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES LIKE 'user'")
    user_exists = cursor.fetchone()
    if not user_exists:
        cursor.execute("""
            CREATE TABLE user (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
        """)
        conn.commit()

    cursor.execute("SHOW TABLES LIKE 'otp_store'")
    otp_exists = cursor.fetchone()
    if not otp_exists:
        cursor.execute("""
            CREATE TABLE otp_store (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                otp VARCHAR(10) NOT NULL
            )
        """)
        conn.commit()

    cursor.close()
    conn.close()

@login_bp.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    if not username or not email or not password:
        return jsonify({"error": "username, email & password are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user WHERE username=%s OR email=%s", (username, email))
    existing_user = cursor.fetchone()
    if existing_user:
        cursor.close()
        conn.close()
        return jsonify({"error": "User already exists"}), 400

    cursor.execute("INSERT INTO user (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"message": "User registered successfully", "user_id": new_id}), 201

@login_bp.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()
    identifier = data.get("identifier")
    password = data.get("password")
    if not identifier or not password:
        return jsonify({"error": "identifier and password required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user WHERE (username=%s OR email=%s) AND password=%s", (identifier, identifier, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({"message": "Login successful"}), 200

def send_email(receiver, subject, body):
    msg = MIMEText(body)
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = receiver
    msg["Subject"] = subject

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.sendmail(EMAIL_ADDRESS, receiver, msg.as_string())
    server.quit()

@login_bp.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({"error": "email required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user WHERE email=%s", (email,))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        conn.close()
        return jsonify({"error": "email does not exist"}), 404

    otp = ''.join(random.choices(string.digits, k=6))
    cursor.execute("DELETE FROM otp_store WHERE email=%s", (email,))
    cursor.execute("INSERT INTO otp_store (email, otp) VALUES (%s, %s)", (email, otp))
    conn.commit()
    cursor.close()
    conn.close()

    send_email(email, "Your OTP Code", f"Your OTP code is {otp}")

    return jsonify({"message": "OTP sent"}), 200

@login_bp.route("/forgetpassword", methods=["POST"])
def reset_password():
    data = request.get_json()
    email = data.get("email")
    otp = data.get("otp")
    new_password = data.get("new_password")

    if not email or not otp or not new_password:
        return jsonify({"error": "email, otp and new_password required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM otp_store WHERE email=%s AND otp=%s", (email, otp))
    otp_record = cursor.fetchone()

    if not otp_record:
        cursor.close()
        conn.close()
        return jsonify({"error": "Invalid OTP"}), 400

    cursor.execute("UPDATE user SET password=%s WHERE email=%s", (new_password, email))
    conn.commit()
    cursor.execute("DELETE FROM otp_store WHERE email=%s", (email,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Password updated successfully"}), 200

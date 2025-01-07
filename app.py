from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import random
import smtplib
import tensorflow as tf
import joblib

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Simulated database
users = {}  # Stores user details
otps = {}   # Temporary storage for OTPs

# Email configuration
EMAIL = "bookrecommenderai@gmail.com"
PASSWORD = "hbspqngvgyyrekge"  # Your App Password from Gmail
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Load models
model1 = tf.keras.models.load_model('models/model1.h5')  # First model
model2 = joblib.load('models/model2.pkl')  # Second model


def send_otp_email(receiver_email, otp):
    """
    Function to send OTP to a specified email address.
    """
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        subject = "OTP Verification for Registration"
        body = f"Dear User,\n\nYour OTP for registration is {otp}. Please use this to complete your registration.\n\nThank you!"
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(EMAIL, receiver_email, message)
        server.quit()
        print(f"OTP sent to {receiver_email}")
    except Exception as e:
        print(f"Error sending email: {e}")
        raise e


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users and users[username]['password'] == password:
            session['user'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if username in users:
            flash('Username already exists!', 'danger')
        elif password != confirm_password:
            flash('Passwords do not match!', 'danger')
        else:
            otp = random.randint(100000, 999999)
            otps[username] = {'otp': otp, 'email': email, 'name': name, 'password': password}
            try:
                send_otp_email(email, otp)
                flash(f'OTP has been sent to {email}. Please verify.', 'info')
                return redirect(url_for('otp_verification', username=username))
            except Exception as e:
                flash('Failed to send OTP. Please try again.', 'danger')
    return render_template('register.html')


@app.route('/otp/<username>', methods=['GET', 'POST'])
def otp_verification(username):
    if username not in otps:
        flash('Invalid session. Please register again.', 'danger')
        return redirect(url_for('register'))

    if request.method == 'POST':
        otp_input = request.form.get('otp')
        if otp_input.isdigit() and int(otp_input) == otps[username]['otp']:
            users[username] = {
                'name': otps[username]['name'],
                'email': otps[username]['email'],
                'password': otps[username]['password'],
                'verified': True
            }
            otps.pop(username, None)
            flash('OTP verified successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP. Please try again.', 'danger')
    return render_template('otp_verification.html', username=username)


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))


@app.route('/predict1', methods=['POST'])
def predict1():
    data = request.json  # Expecting JSON input
    input_data = [data['feature1'], data['feature2'], data['feature3']]  # Adjust features
    input_data = tf.convert_to_tensor([input_data])  # Convert to TensorFlow tensor

    prediction = model1.predict(input_data)
    result = prediction[0][0]  # Adjust indexing as per your model's output
    return jsonify({'prediction': float(result)})


@app.route('/predict2', methods=['POST'])
def predict2():
    data = request.json  # Expecting JSON input
    input_data = [[data['feature1'], data['feature2'], data['feature3']]]  # Adjust features

    prediction = model2.predict(input_data)
    result = prediction[0]  # Adjust indexing as per your model's output
    return jsonify({'prediction': result})


if __name__ == '__main__':
    app.run(debug=True)

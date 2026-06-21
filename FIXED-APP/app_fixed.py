from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import subprocess
import sqlite3
import html
import os
import re

app = Flask(__name__)
app.secret_key = "SuperSecretKey_ChangeThisInProduction"


UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg', 'pdf'} 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, content TEXT)')
    conn.commit()
    conn.close()

init_db()


def allowed_file(filename):
    """Check if the uploaded file has an explicitly allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_ip(ip_address):
    """Strict Regex to ensure the input is ONLY a valid IPv4 address."""
    pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    return pattern.match(ip_address)



@app.route('/', methods=['GET', 'POST'])
def index():
    """Public Contact Form - Patched for Stored XSS"""
    if request.method == 'POST':
        message = request.form.get('message', '')
        

        safe_message = html.escape(message)
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO messages (content) VALUES (?)', (safe_message,))
        conn.commit()
        conn.close()
        return "Message securely sent!"
    

    return '''
        <h1>Contact Us</h1>
        <form method="POST">
            <textarea name="message" placeholder="Enter your message here..."></textarea><br>
            <input type="submit" value="Send Message">
        </form>
    '''

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    """Admin Login Portal"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
       
        if username == 'wesam' and password == 'password123':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials."
    return '''
        <form method="POST">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    '''

@app.route('/admin/dashboard')
def dashboard():
    """Admin Dashboard - Displays Messages"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT content FROM messages')
    messages = c.fetchall()
    conn.close()
    

    messages_html = "<ul>" + "".join([f"<li>{m[0]}</li>" for m in messages]) + "</ul>"
    
    return f'''
        <h1>Admin Dashboard</h1>
        <p><a href="/admin/ping">Network Diagnostics</a> | <a href="/admin/upload">File Upload</a></p>
        <h2>User Messages:</h2>
        {messages_html}
    '''

@app.route('/admin/ping', methods=['GET', 'POST'])
def ping():
    """Network Diagnostics - Patched for OS Command Injection"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    output = ""
    if request.method == 'POST':
        ip = request.form.get('ip', '')
        
       
        if not is_valid_ip(ip):
            output = "SECURITY ALERT: Invalid IP Address format detected. Execution blocked."
        else:
            try:
            
                result = subprocess.run(["ping", "-c", "4", ip], capture_output=True, text=True, timeout=5)
                output = result.stdout
            except Exception as e:
                output = "Ping execution failed."

    return f'''
        <h1>Network Diagnostics</h1>
        <form method="POST">
            IP Address to Ping: <input type="text" name="ip" value="127.0.0.1"><br>
            <input type="submit" value="Run Diagnostics">
        </form>
        <pre>{output}</pre>
    '''

@app.route('/admin/upload', methods=['GET', 'POST'])
def upload():
    """File Upload - Patched for Unrestricted File Uploads"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    message = ""
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
            
     
        if file and allowed_file(file.filename):
          
            safe_filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], safe_filename))
            message = f"File {safe_filename} successfully uploaded."
        else:
            message = "SECURITY ALERT: File type not allowed. Only TXT, PNG, JPG, and PDF are permitted."

    return f'''
        <h1>Upload File</h1>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file"><br>
            <input type="submit" value="Upload">
        </form>
        <p><b>{message}</b></p>
    '''

if __name__ == '__main__':
    
    app.run(host='0.0.0.0', port=5000, debug=False)
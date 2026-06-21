from flask import Flask, request, render_template_string, abort, redirect, url_for, session
import sqlite3
import subprocess
import os

app = Flask(__name__)
app.secret_key = "lab_admin_secret_key" 

DB_PATH = '/var/www/inventory_app/database.db'
UPLOAD_FOLDER = '/var/www/inventory_app/static/uploads'

CSS_STYLE = """
<style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121212; color: #e0e0e0; margin: 40px; }
    h2 { color: #64ffda; border-bottom: 1px solid #333; padding-bottom: 10px; }
    a { color: #bb86fc; text-decoration: none; font-weight: bold; }
    a:hover { text-decoration: underline; color: #d0aaff; }
    form { background-color: #1e1e1e; padding: 20px; border-radius: 8px; max-width: 400px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); border: 1px solid #333; }
    input[type="text"], input[type="password"], textarea, input[type="file"] { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #444; background-color: #2d2d2d; color: white; border-radius: 4px; box-sizing: border-box;}
    input[type="submit"] { width: 100%; padding: 12px; background-color: #03dac6; color: #000; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-top: 10px; }
    input[type="submit"]:hover { background-color: #00b3a6; }
    ul { list-style-type: none; padding: 0; }
    li { background-color: #1e1e1e; margin: 10px 0; padding: 15px; border-left: 4px solid #bb86fc; border-radius: 4px; }
    pre { background-color: #000; padding: 15px; border-radius: 5px; overflow-x: auto; color: #0f0; border: 1px solid #333; max-width: 800px; }
    .container { max-width: 800px; margin: 0 auto; }
</style>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_message = request.form.get('message')
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT INTO messages (content) VALUES (?)", (user_message,))
            conn.commit()
            conn.close()
            return CSS_STYLE + "<div class='container'><h2>Success</h2><p>Message sent to supplier!</p><a href='/'>Go back</a></div>"
        except sqlite3.OperationalError as e:
            abort(503, description="Database is currently locked or unreachable due to permissions.")
            
    html_form = CSS_STYLE + """
    <div class='container'>
        <h2>Corporate Inventory - Contact Supplier</h2>
        <form method="POST">
            <label>Secure Message:</label>
            <textarea name="message" rows="4" placeholder="Enter message here..."></textarea>
            <input type="submit" value="Send Message">
        </form>
        <br><br>
        <a href="/admin/login">Admin Portal Access &rarr;</a>
    </div>
    """
    return render_template_string(html_form)

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'password123':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return CSS_STYLE + "<div class='container'><h2>Error</h2><p>Invalid credentials.</p><a href='/admin/login'>Try again</a></div>"
            
    login_form = CSS_STYLE + """
    <div class='container'>
        <h2>Admin Authentication</h2>
        <form method="POST">
            <label>Username</label>
            <input type="text" name="username">
            <label>Password</label>
            <input type="password" name="password">
            <input type="submit" value="Authenticate">
        </form>
    </div>
    """
    return render_template_string(login_form)

@app.route('/admin/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, content TEXT)''')
        c.execute("SELECT content FROM messages")
        messages = c.fetchall()
        conn.close()
        
        html_dashboard = CSS_STYLE + "<div class='container'><h2>Admin Dashboard - Supplier Messages</h2><ul>"
        if not messages:
            html_dashboard += "<li>No messages currently in database.</li>"
        for msg in messages:
            html_dashboard += f"<li>{msg[0]}</li>" 
        html_dashboard += """
        </ul>
        <br><br>
        <h3>System Tools</h3>
        <p><a href='/admin/ping'>&gt; Network Diagnostics Tool</a></p>
        <p><a href='/admin/upload'>&gt; Upload Document</a></p>
        </div>
        """
        return render_template_string(html_dashboard)
    except sqlite3.OperationalError as e:
        abort(503, description="Database is currently locked or unreachable due to permissions.")

@app.route('/admin/ping', methods=['GET', 'POST'])
def ping():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    output = ""
    if request.method == 'POST':
        target_ip = request.form.get('ip')
        try:
            command = f"ping -c 1 {target_ip}"
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
        except subprocess.CalledProcessError as e:
            output = e.output
            
    ping_form = CSS_STYLE + f"""
    <div class='container'>
        <h2>Network Diagnostics</h2>
        <form method="POST">
            <label>IP Address to Ping:</label>
            <input type="text" name="ip" placeholder="e.g., 127.0.0.1">
            <input type="submit" value="Run Diagnostics">
        </form>
        """
    if output:
        ping_form += f"<br><h3>Terminal Output:</h3><pre>{output}</pre>"
        
    ping_form += "<br><a href='/admin/dashboard'>&larr; Back to Dashboard</a></div>"
    return render_template_string(ping_form)

@app.route('/admin/upload', methods=['GET', 'POST'])
def upload_file():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    message = ""
    if request.method == 'POST':
        if 'file' not in request.files:
            message = "No file part"
        else:
            file = request.files['file']
            if file.filename == '':
                message = "No selected file"
            else:
                save_path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(save_path)
                message = f"File uploaded successfully! View it at: <a href='/static/uploads/{file.filename}'>/static/uploads/{file.filename}</a>"
                
    upload_form = CSS_STYLE + f"""
    <div class='container'>
        <h2>Admin - Document Upload</h2>
        <p style="color: #03dac6;">{message}</p>
        <form method="POST" enctype="multipart/form-data">
            <label>Select File:</label>
            <input type="file" name="file">
            <input type="submit" value="Upload Document">
        </form>
        <br><a href='/admin/dashboard'>&larr; Back to Dashboard</a>
    </div>
    """
    return render_template_string(upload_form)

if __name__ == '__main__':
    app.run(debug=False)
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import bcrypt
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.secret_key = "membuatLoginFlask1"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # Ganti dengan password MySQL kamu jika ada
app.config['MYSQL_DB'] = 'flaskdb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


@app.route('/')
def home():
    return render_template("home.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM users WHERE email=%s", [email])
            user = cur.fetchone()
            cur.close()

            if user and bcrypt.checkpw(password, user['password'].encode('utf-8')):
                session['name'] = user['name']
                session['email'] = user['email']
                return redirect(url_for('home'))
            else:
                flash('Gagal, Email dan Password Tidak cocok!')
                return redirect(url_for('login'))
        
        except Exception as e:
            flash(f"Terjadi kesalahan: {str(e)}")
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hash_password))
            mysql.connection.commit()
            cur.close()

            session['name'] = name
            session['email'] = email
            return redirect(url_for('home'))
        
        except Exception as e:
            flash(f"Terjadi kesalahan: {str(e)}")
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/about')
def about():
    if 'email' in session:
        app.logger.debug(f"Email '{session['email']}' ditemukan dalam session.")
        return render_template('about.html')
    else:
        app.logger.debug("Session tidak memiliki email, mengalihkan kembali ke halaman home.")
        return redirect(url_for('home'))

@app.route('/portofolio')
def portofolio():
    if 'email' in session:
        return render_template('portofolio.html')
    else:
        return redirect(url_for('home'))

@app.route('/contact')
def contact():
    if 'email' in session:
        return render_template('contact.html')
    else:
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

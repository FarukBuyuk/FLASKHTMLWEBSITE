import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from wtforms import Form, StringField, PasswordField, validators
from functools import wraps
from wtforms import StringField, TextAreaField
from wtforms.widgets import TextInput
app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'templates'))
app.secret_key = "ybblog"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "ybblog"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
mysql = MySQL(app)
#Kullanıcı Girişini Decaratörle Güvenliğini Sağlama
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if  "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu Sayfayı Görüntülemek İçin Lütfen Giriş Yapın","danger")
            return redirect(url_for("login"))
    return decorated_function
#Kullanıcı Kayıt Formu
class RegisterForm(Form):
    name = StringField("İsim Soyisim", validators=[validators.length(min=4, max=25)])
    username = StringField("Kullanıcı Adı", validators=[validators.length(min=5, max=35)])
    email = StringField("Email Adresi", validators=[validators.Email(message="Lütfen geçerli bir email adresi giriniz.")])
    password = PasswordField("Parola", validators=[
        validators.EqualTo(fieldname="confirm", message="Parolanız uyuşmuyor.")
    ])
    confirm = PasswordField("Parola Doğrula")
class LoginForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Parola")
# Eklenen kısım
class ChangeEmailForm(Form):
    current_email = StringField("Mevcut E-posta")
    new_email = StringField("Yeni E-posta", validators=[validators.Email(message="Lütfen geçerli bir email adresi giriniz.")])
class ChangePasswordForm(Form):
    new_password = PasswordField("Yeni Parola", validators=[
        validators.EqualTo(fieldname="confirm", message="Yeni parolanız uyuşmuyor.")
    ])
    confirm = PasswordField("Yeni Parola Doğrula")
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)

    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = form.password.data
        with mysql.connection.cursor() as cursor:
            sorgu = "INSERT INTO users(name, email, username, password) VALUES (%s, %s, %s, %s)"
            cursor.execute(sorgu, (name, email, username, password))
            mysql.connection.commit()

        flash("Başarıyla Kayıt Oldunuz.", "success")
        return redirect(url_for("login"))
    else:
        return render_template("register.html", form=form)
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        username = form.username.data
        password_entered = form.password.data
        cursor = mysql.connection.cursor()
        sorgu = "SELECT * FROM users WHERE username = %s"
        result = cursor.execute(sorgu, (username,))
        if result > 0:
            data = cursor.fetchone()
            real_password = data["password"]
            if password_entered == real_password:
                flash("Başarıyla giriş yaptınız.", "success")
                session["logged_in"] = True
                session["username"] = username
                return redirect(url_for("index"))
            else:
                flash("Parolayı Yanlış Girdiniz..", "danger")
                return redirect(url_for("login"))
        else:
            flash("Böyle bir Kullanıcı Adı Bulunamadı.", "danger")
    return render_template("login.html", form=form)
# Eklenen kısım
@app.route('/change_email', methods=["GET", "POST"])
def change_email():
    form = ChangeEmailForm(request.form)
    if request.method == "POST" and form.validate():
        new_email = form.new_email.data
        with mysql.connection.cursor() as cursor:
            sorgu = "UPDATE users SET email = %s WHERE username = %s"
            cursor.execute(sorgu, (new_email, session["username"]))
            mysql.connection.commit()
        flash("E-posta başarıyla değiştirildi.", "success")
        return redirect(url_for("dashboard"))
    return render_template("change_email.html", form=form)
# Eklenen kısım
@app.route('/change_password', methods=["GET", "POST"])
def change_password():
    form = ChangePasswordForm(request.form)
    if request.method == "POST" and form.validate():
        new_password = form.new_password.data
        with mysql.connection.cursor() as cursor:
            sorgu = "UPDATE users SET password = %s WHERE username = %s"
            cursor.execute(sorgu, (new_password, session["username"]))
            mysql.connection.commit()
        flash("Parola başarıyla değiştirildi.", "success")
        return redirect(url_for("dashboard"))
    return render_template("change_password.html", form=form)
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
#Karakter Ekleme
@app.route("/addarticle", methods=["GET", "POST"])
def addarticle():
    form = ArticleForm(request.form)

    if request.method == "POST" and form.validate():
        KARAKTER = form.KARAKTER.data
        LVL = form.LVL.data
        

        cursor = mysql.connection.cursor()
        sorgu = "INSERT INTO articles(KARAKTER, LVL) VALUES(%s, %s)"
        cursor.execute(sorgu, (KARAKTER, LVL))
        mysql.connection.commit()
        cursor.close()

        flash("Karakter Başarıyla Eklendi", "success")
        return redirect(url_for("addarticle"))
    
    # Güncel veritabanı tablosunu çek
    cursor = mysql.connection.cursor()
    sorgu = "SELECT * FROM articles"
    cursor.execute(sorgu)
    articles = cursor.fetchall()
    cursor.close()

    return render_template("addarticle.html", form=form, articles=articles)

#Karakter Form
class SmallStringField(StringField):
    widget = TextInput()
class ArticleForm(Form):
    KARAKTER = SmallStringField("Hangi Karakter ?", validators=[validators.length(min=4, max=7)])
    LVL = SmallStringField("Karakterinizin Kaç LVL")
if __name__ == "__main__":
    app.run(debug=True, port=5000)

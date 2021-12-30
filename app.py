from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
import random
import string
from flask_mail import Mail, Message
import re

app = Flask(__name__)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='kaps4332@gmail.com',
    MAIL_PASSWORD='Kapil8875'
)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:admin123@localhost/student'
app.secret_key = 'ghjhjhq/213763fbf'
db = SQLAlchemy(app)
mail = Mail(app)
urlinfo = db.Table('urlinfo', db.metadata, autoload=True, autoload_with=db.engine)
userDetails = db.Table('userDetails', db.metadata, autoload=True, autoload_with=db.engine)


@app.route('/')
def shortcut():
    return render_template('index.html')


@app.route("/urlshortner")
def urlshortner():
    url = request.args.get('link')
    if url == '':
        return render_template('index.html', error2="Please enter valid url")
    custom_url = request.args.get('link1')
    if custom_url == '':
        while True:
            encrypted_url = createEncrypted_url()
            url_query = db.session.query(urlinfo).filter_by(encryptedurl=encrypted_url).one_or_none()
            print(url_query)
            if url_query is None:
                break
        # print(encrypted_url)
        if 'userid' in session:
            id = session['userid']
            insert_query = urlinfo.insert().values(originalUrl=url, encryptedurl=encrypted_url, is_Active=1,
                                                   created_by=id)

        else:
            insert_query = urlinfo.insert().values(originalUrl=url, encryptedurl=encrypted_url, is_Active=1)

        db.session.execute(insert_query)
        db.session.commit()
        final_encrypted_url = 'srt.ct/' + encrypted_url
    else:
        url_query = db.session.query(urlinfo).filter_by(encryptedurl=custom_url).one_or_none()
        if url_query is None:
            if 'userid' in session:
                id = session['userid']
                insert_query = urlinfo.insert().values(originalUrl=url, encryptedurl=custom_url, is_Active=1,
                                                       created_by=id)
            else:
                insert_query = urlinfo.insert().values(originalUrl=url, encryptedurl=custom_url, is_Active=1)

            db.session.execute(insert_query)
            db.session.commit()
            final_encrypted_url = 'srt.ct/' + custom_url
        else:
            if 'userid' in session:
                flash("url already exist")
                return redirect('/home')
            else:
                return render_template("index.html", error3="url already exist")
    if 'userid' in session:
        return redirect('/home')
    else:
        return render_template('index1.html', finalencryptedurl=final_encrypted_url, url=url)


def createEncrypted_url():
    # letter='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    letter = string.ascii_letters + string.digits
    encrypted_url = ''
    for i in range(6):
        encrypted_url = encrypted_url + ''.join(random.choice(letter))
    return encrypted_url


@app.route('/<url>')
def dynamicUrl(url):
    url_query = db.session.query(urlinfo).filter_by(encryptedurl=url).one_or_none()
    if url_query[1] is None:
        return render_template('index.html', error='url does not exist')
    print(url_query[1])
    return redirect(url_query[1])


@app.route('/SignUp')
def SignUp():
    if 'userid' in session:
        return redirect('/home')
    else:
        return render_template('SignUp.html')


@app.route('/register')
def register():
    email = request.args.get('email')
    username = request.args.get('uname')
    pwd = request.args.get('pwd')
    if email == None or username == None or pwd == None:
        return render_template('SignUp.html', error1="Please fill all details")
    email_check = re.fullmatch("^([a-z\d\._-]+)@([a-z\d-]+)\.([a-z]{2,8})(\.[a-z]{2,8})?$", email)
    if email_check is None:
        return render_template('SignUp.html',
                               error1="Please enter valid mail id or it should be in lowercase letters instead of uppercase")
    psw_check = re.fullmatch("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", pwd)
    if psw_check is None:
        return render_template("SignUp.html", error1="Password should be of required format")
    username_check = re.fullmatch("[a-zA-Z_\s]{5,20}", username)
    if username_check is None:
        return render_template("Signup.html", error1="Name should be between 5 to 20 letters without any digits and special symbol except (_)")
    result_mail = db.session.query(userDetails).filter_by(emailId=email).one_or_none()
    if result_mail is None:
        insert_query = userDetails.insert().values(emailId=email, userName=username, password=pwd, is_Active=1)
        db.session.execute(insert_query)
        db.session.commit()
        return redirect('/Login')
    else:
        return render_template('SignUp.html', error="MailId already exist")


@app.route('/Login')
def Login():
    if 'userid' in session:
        return redirect('/home')
    else:
        return render_template('login.html')


@app.route('/checkLoginIn')
def checkLogIn():
    email = request.args.get('email')
    password = request.args.get('pwd')
    if email == None or password == None:
        return render_template('login.html', error="Please Fill all Details")
    result_mail = db.session.query(userDetails).filter_by(emailId=email).one_or_none()
    if result_mail is None:
        return render_template('login.html', error='you are not registered')
    else:
        if password == result_mail[3]:
            session['email'] = email
            session['userid'] = result_mail[0]
            return redirect('/home')
        else:
            return render_template('Login.html', error='your password is not correct')


# @app.route('/google')
# def google():
#     return render_template('google.html')


@app.route('/home')
def home():
    if 'userid' in session:
        # email = session['email']
        id = session['userid']
        creator_query = db.session.query(urlinfo).filter_by(created_by=id).all()
        return render_template('updateUrl.html', data=creator_query)
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('userid', None)
    return render_template('login.html')


@app.route('/editUrl', methods=['post'])
def editUrl():
    if 'userid' in session:
        email = session['email']
        print(email)
        id = request.form.get('id')
        url = request.form.get('orignalurl')
        encrypted = request.form.get('encrypted')
        return render_template("editUrl.html", url=url, encrypted=encrypted, id=id)
    else:
        return render_template('login.html')


@app.route('/updateUrl', methods=['post'])
def updateUrl():
    if 'userid' in session:
        id = request.form.get('id')
        url = request.form.get('orignalurl')
        encrypted = request.form.get('encrypted')
        url_query = db.session.query(urlinfo).filter(urlinfo.c.encryptedurl == encrypted,
                                                     urlinfo.c.pk_urlId != id).one_or_none()
        if url_query is None:
            update_query = urlinfo.update().values(originalUrl=url, encryptedurl=encrypted).where(
                urlinfo.c.pk_urlId == id)
            db.session.execute(update_query)
            db.session.commit()
            return redirect('/home')
        else:
            return render_template("editUrl.html", url=url, encrypted=encrypted, id=id, error='short url already exist')
    return render_template('login.html')


@app.route('/deleteUrl', methods=['post'])
def deleteUrl():
    if 'userid' in session:
        id = request.form.get('id')
        db.session.query(urlinfo).filter_by(pk_urlId=id).delete()
        db.session.commit()
        return redirect('/home')
    return render_template('login.html')


@app.route('/askmail')
def askmail():
    return render_template("askmail.html")


@app.route('/forgetpassword')
def forgetpassword():
    email = request.args.get('email')
    email_check = re.fullmatch("^([a-z\d\._-]+)@([a-z\d-]+)\.([a-z]{2,8})(\.[a-z]{2,8})?$", email)
    if email_check is None:
        return render_template('askemail.html',
                               error="Please enter valid mail id or it should be in lowercase letters instead of uppercase")
    pswd_query = db.session.query(userDetails.c.password).filter_by(emailId=email).one_or_none()
    if pswd_query is None:
        return render_template('askmail.html', error="email is not correct")
    randomnumber = ''
    letter = string.digits
    for i in range(6):
        randomnumber = randomnumber + ''.join(random.choice(letter))
    body = 'Your forget password OTP is ' + randomnumber
    msg = Message(subject='Forget Password Email', sender='kaps4332@gmail.com',
                  recipients=[email], body=body)
    msg.cc = ['kartik12@gmail.com']
    mail.send(msg)
    # update_query = "update userDetails set otp ='{}' where emailId= '{}'".format(randomnumber, email)
    update_query = userDetails.update().values(otp=randomnumber).where(
        userDetails.c.emailId == email)
    db.session.execute(update_query)
    db.session.commit()
    return render_template('updatepassword.html', email=email)


@app.route('/updatepassword')
def updatepassword():
    email = request.args.get('email')
    otp = request.args.get("otp")
    password = request.args.get("new-psw")
    psw_check = re.fullmatch("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password)
    if psw_check is None:
        return render_template("updatepassword.html", error1="Password should be of required format")
    mail_query = db.session.query(userDetails.c.otp).filter_by(emailId=email).one_or_none()
    pswd_query = db.session.query(userDetails.c.password).filter_by(emailId=email).one_or_none()
    if mail_query[0] == otp:
        if password != pswd_query[0]:
            # update_query = "update userDetails set password ='{}' where emailId= '{}'".format(password, email)
            update_query = userDetails.update().values(password=password).where(
                userDetails.c.emailId == email)
            db.session.execute(update_query)
            db.session.commit()
            return render_template("login.html")
        else:
            return render_template("updatepassword.html", email=email, error="old password! please enter new password")
    else:
        return render_template("updatepassword.html", email=email, error="enter correct otp send to your mailid")


app.run()

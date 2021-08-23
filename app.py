@app.route('/')
def hello_world():
    # connection = connect(host="localhost", database="student", user="root", password="admin123"')
    # cur = connection.cursor()
    return render_template('index.html')

@app.route("/urlshortner")
def urlshortner():
    # letter='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    url = request.args.get('link')
    customurl = request.args.get('link1')
    connection = connect(host="localhost", database="student", user="root", password="admin123"")
    cur = connection.cursor()
    # encryptedurl = ''
    if customurl == '':
        while True:
            encryptedurl = createEncryptedurl()
            query1 = "select * from urlinfo where encryptedUrl='{}'".format(encryptedurl)
            cur.execute(query1)
            xyz = cur.fetchone()
            print(xyz)
            if xyz is None:
                break
        print(encryptedurl)
        if 'userid' in session:
            id = session['userid']
            query = "insert into urlinfo(originalUrl,encryptedUrl,is_Active, created_by) values('{}','{}',1,'{}')".format(
                url, encryptedurl, id)
        else:
            query = "insert into urlinfo(originalUrl,encryptedUrl,is_Active) values('{}','{}',1)".format(url,
                                                                                                         encryptedurl)
        cur = connection.cursor()
        cur.execute(query)
        connection.commit()
        finalencryptedurl = 'sd.in/' + encryptedurl
    else:
        query1 = "select * from urlinfo where encryptedUrl='{}'".format(customurl)
        cur.execute(query1)
        xyz = cur.fetchone()
        if xyz is None:
            if 'userid' in session:
                id = session['userid']
                query2 = "insert into urlinfo(originalUrl,encryptedUrl,is_Active, created_by) values('{}','{}',1,'{}')".format(
                    url, customurl, id)
            else:
                query2 = "insert into urlinfo(originalUrl,encryptedUrl,is_Active) values('{}','{}',1)".format(url,
                                                                                                              customurl)
            cur.execute(query2)
            connection.commit()
            finalencryptedurl = 'sd.in/' + customurl
        else:
            return "url already exist"
    if 'userid' in session:
        return redirect('/home')
    else:
        return render_template('index.html', finalencryptedurl=finalencryptedurl, url=url)


def createEncryptedurl():
    letter = string.ascii_letters + string.digits
    encryptedurl = ''
    for i in range(6):
        encryptedurl = encryptedurl + ''.join(random.choice(letter))
    print(encryptedurl)
    return encryptedurl

@app.route('/<url>')
def dynamicUrl(url):
    connection = connect(host='localhost', database='kartik', user='root', password='kartik14')
    query1 = "select * from urlinfo where encryptedUrl='{}'".format(url)
    cur = connection.cursor()
    cur.execute(query1)
    originalurl = cur.fetchone()
    print(originalurl)
    if originalurl is None:
        return render_template('index.html')
    print(originalurl[1])
    return redirect(originalurl[1])


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
        return render_template('SignUp.html', error1="Please fill correct all details")
    connection = connect(host="localhost", database="kartik", user="root", password="kartik14")
    cur = connection.cursor()
    query1 = "select * from userDetails where emailId='{}'".format(email)
    cur.execute(query1)
    xyz = cur.fetchone()
    if xyz is None:
        query = "insert into userDetails(emailId,userName,password,is_Active) values('{}','{}','{}',1)".format(email,
                                                                                                               username,
                                                                                                               pwd)
        cur = connection.cursor()
        cur.execute(query)
        connection.commit()
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
    connection = connect(host="localhost", database="kartik", user="root", password="kartik14")
    cur = connection.cursor()
    query1 = "select * from userDetails where emailId='{}'".format(email)
    cur.execute(query1)
    xyz = cur.fetchone()
    print(xyz)
    if xyz is None:
        return render_template('login.html', xyz='you are not registered')
    else:
        if password == xyz[3]:
            session['email'] = email
            session['userid'] = xyz[0]
            # return render_template('UserHome.html')
            # mailbhejo()
            return redirect('/home')
        else:
            return render_template('Login.html', xyz='your password is not correct')



@app.route('/home')
def home():
    if 'userid' in session:
        # email = session['email']
        id = session['userid']
        print(id)
        connection = connect(host="localhost", database="kartik", user="root", password="kartik14")
        cur = connection.cursor()
        query1 = "select * from urlinfo where created_by={}".format(id)
        cur.execute(query1)
        data = cur.fetchall()
        return render_template('updateUrl.html', data=data)
    return render_template('login.html')

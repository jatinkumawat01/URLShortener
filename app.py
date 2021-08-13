@app.route('/')
def hello_world():
    # connection = connect(host='localhost', database='kartik', user='root', password='kartik14')
    # cur = connection.cursor()
    return render_template('index.html')

@app.route("/urlshortner")
def urlshortner():
    # letter='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    url = request.args.get('link')
    customurl = request.args.get('link1')
    connection = connect(host="localhost", database="student", user="root", password="admin123")
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
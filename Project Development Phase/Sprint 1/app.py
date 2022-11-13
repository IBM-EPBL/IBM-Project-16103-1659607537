from flask import Flask, render_template, request, redirect, url_for, session, flash
import ibm_db
import re
import hashlib
str=hashlib.sha256()
str_hex=str.hexdigest()

app = Flask(__name__)

app.secret_key='a'

conn= ibm_db.connect("DATABASE=;HOSTNAME=;PORT=;SECURITY=SSL;SSLServerCertificate=;UID=;PWD=",' ',' ')

@app.route('/')
def homer():
    session['loggedin']=False
    return render_template('login.html')



@app.route('/login',methods=['GET','POST'])
def login():
    global userid
    msg=''
    if request.method =='POST':
        username=request.form['username']
        password=request.form['password']
        str=hashlib.sha256(password.encode())
        password=str.hexdigest() 
        sql= "SELECT * FROM USERS WHERE USERNAME=? AND PASSWORD=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            rows=[]
            session['loggedin']=True
            session['id']=account['USERNAME']
            userid= account['USERNAME']
            session['USERNAME']= account['USERNAME']
            msg='Logged in Successfully !'
            #for floral shirt
            sql="SELECT * FROM PRODUCT WHERE PCAT='floral'"
            stmt=ibm_db.exec_immediate(conn,sql)
            rowse=ibm_db.fetch_assoc(stmt)
            while rowse != False:
                rows.append(rowse)
                rowse = ibm_db.fetch_assoc(stmt)
            print(rows)
            #for Pant
            pants=[]
            sql="SELECT * FROM PRODUCT WHERE PCAT='pant'"
            stmt=ibm_db.exec_immediate(conn,sql)
            rowse=ibm_db.fetch_assoc(stmt)
            while rowse != False:
                pants.append(rowse)
                rowse = ibm_db.fetch_assoc(stmt)
            print(rows)
            return render_template('store.html',productsa=rows,pant=pants)

        else:
            msg='Invalid Username/Password'
    return render_template('login.html',msg=msg)


@app.route('/register',methods=['GET','POST'])
def register():
    msg=''
    if request.method== 'POST':
        USERNAME= request.form['username']
        EMAIL= request.form['email']
        PASSWORD=request.form['password']
        sql="SELECT * FROM USERS WHERE USERNAME=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,USERNAME)
        ibm_db.execute(stmt)
        account= ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg='Account already Exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+',EMAIL):
            msg='Invalid email address !' 
        elif not re.match(r'[A-Za-z0-9]+',USERNAME):
            msg='Username should only contain Alphabet and numbers !'
        else:
            str=hashlib.sha256(PASSWORD.encode())
            PASSWORD=str.hexdigest() 
            insert_sql="INSERT INTO USERS VALUES(?,?,?)"
            prep_stmt= ibm_db.prepare(conn,insert_sql)
            ibm_db.bind_param(prep_stmt,1,USERNAME)
            ibm_db.bind_param(prep_stmt,2,EMAIL)
            ibm_db.bind_param(prep_stmt,3,PASSWORD)
            ibm_db.execute(prep_stmt)
            msg='Registered Successfully !'
    elif request.method=='POST':
            msg='Please fill out the form !'
    return render_template('register.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('logged in',None)
    session.pop('id',None)
    session.pop('username',None)
    session['loggedin']=False

    return render_template('login.html')



if __name__=='__main__':
    app.run(host='0.0.0.0')





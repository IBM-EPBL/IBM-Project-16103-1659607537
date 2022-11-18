from flask import Flask, render_template, request, redirect, url_for, session, flash
import ibm_db
import re
import hashlib
from flask_mail import Mail, Message

app = Flask(__name__)
mail= Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'abcdef1234@gmail.com'
app.config['MAIL_PASSWORD'] = '*****'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

app.secret_key='a'

conn= ibm_db.connect("DATABASE=abcd;HOSTNAME=abcb.databases.appdomain.cloud;PORT=12345;SECURITY=SSL;SSLServerCertificate=certificate.crt;UID=abc1234;PWD=pass",' ',' ')
st=[]
total=0
@app.route('/')
def homer():
    session['loggedin']=False
    return render_template('login.html')



@app.route('/login',methods=['GET','POST'])
def login():
    global userid
    global emaile
    msg=''
    if request.method =='POST':
        username=request.form['username']
        password=request.form['password']
        strwe=hashlib.sha256(password.encode())
        password=strwe.hexdigest() 
        sql= "SELECT * FROM USERS WHERE USERNAME=? AND PASSWORD=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            emaile=account["EMAIL"]
            session['loggedin']=True
            session['id']=account['USERNAME']
            userid= account['USERNAME']
            session['USERNAME']= account['USERNAME']
            msg='Logged in Successfully !'
            return redirect(url_for('store'))

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
            stwr=hashlib.sha256(PASSWORD.encode())
            PASSWORD=stwr.hexdigest() 
            cart=""
            insert_sql="INSERT INTO USERS VALUES(?,?,?,?)"
            prep_stmt= ibm_db.prepare(conn,insert_sql)
            ibm_db.bind_param(prep_stmt,1,USERNAME)
            ibm_db.bind_param(prep_stmt,2,EMAIL)
            ibm_db.bind_param(prep_stmt,3,PASSWORD)
            ibm_db.bind_param(prep_stmt,4,cart)
            ibm_db.execute(prep_stmt)
            teamid="PNT2022TMID37167"
            msg='Registered Successfully !'
            msg = Message('Hello', sender = 'abcdef@gmail.com', recipients =[EMAIL])
            msg.body = "Hello "+USERNAME+" You have Succefully Registered in Tailored"
            mail.send(msg)
            return "Sent"
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



@app.route('/cart')
def cart():
    if(session['loggedin']==True):

        rows=[]
        carts=[]
        USERNAME=session['id']
        sql="SELECT CART FROM USERS WHERE USERNAME=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,USERNAME)
        ibm_db.execute(stmt)
        carts= ibm_db.fetch_assoc(stmt)
        cartes=carts["CART"]
        st=list(cartes.split("-"))
        
        total=0
        th=str('-'.join(st))
        for id in st:
            if(id!=''):
                tem=[]
                sql="SELECT * FROM PRODUCT WHERE PID=?"
                stmt=ibm_db.prepare(conn,sql)
                ibm_db.bind_param(stmt,1,id)
                ibm_db.execute(stmt)
                tem=ibm_db.fetch_assoc(stmt)
                rows.append(tem)
                total+=tem["PPRICE"]
        return render_template('cart.html',carts=rows,total=total,pro=th)
        
    else:
        return render_template('login.html',msg='Please Login !')

    


@app.route('/addcart',methods=['GET','POST'])
def addcart():
    carts=[]
    PID=""
    carte=""
    PID= request.form['PID']
    USERNAME=session['id']
    sql="SELECT CART FROM USERS WHERE USERNAME=?"
    stmt=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,USERNAME)
    ibm_db.execute(stmt)
    carts=ibm_db.fetch_assoc(stmt)
    cartes=carts["CART"]
    print(cartes)
    teamid="PNT2022TMID37167"

    st=list(cartes.split("-"))
    if PID not in st:
        st.append(PID)
        carte='-'.join(st)
        #updation of cart
        insql="UPDATE USERS SET CART=? WHERE USERNAME=?"
        stmt=ibm_db.prepare(conn,insql)
        ibm_db.bind_param(stmt,1,carte)
        ibm_db.bind_param(stmt,2,USERNAME)
        ibm_db.execute(stmt)
    return ('',204)

@app.route('/store')
def store():
    rows=[]
    if(session['loggedin']==True):

        #for floral shirt
        sql="SELECT * FROM PRODUCT WHERE PCAT='floral' AND STOCK>0"
        stmt=ibm_db.exec_immediate(conn,sql)
        rowse=ibm_db.fetch_assoc(stmt)
        while rowse != False:
            rows.append(rowse)
            rowse = ibm_db.fetch_assoc(stmt)
        print(rows)
        #for Pant
        pants=[]
        sql="SELECT * FROM PRODUCT WHERE PCAT='pant' AND STOCK>0"
        stmt=ibm_db.exec_immediate(conn,sql)
        rowse=ibm_db.fetch_assoc(stmt)
        while rowse != False:
            pants.append(rowse)
            rowse = ibm_db.fetch_assoc(stmt)
        print(rows)
        ms=session['id']
        teamid="PNT2022TMID37167"
        return render_template('store.html',productsa=rows,pant=pants,names=ms)
    else:
        return render_template('login.html',msg='Please Login !')


@app.route('/delete',methods=['GET','POST'])
def delete():
    PID=""
    product=request.form['prod']
    st=list(product.split("-"))
    USERNAME=session['id']
    PID=request.form['PID']
    print(PID)
    print(product)
    if PID in st:
        st.remove(PID)
        carte='-'.join(st)
        #updation of cart
        insql="UPDATE USERS SET CART=? WHERE USERNAME=?"
        stmt=ibm_db.prepare(conn,insql)
        ibm_db.bind_param(stmt,1,carte)
        ibm_db.bind_param(stmt,2,USERNAME)
        ibm_db.execute(stmt)
    return cart()



@app.route('/order',methods=['GET','POST'])
def order():
    name=request.form['name']
    hno=str(request.form['hno'])
    area=request.form['area']
    city=request.form['city']
    state=request.form['state']
    mno=str(request.form['mno'])
    product=request.form['prod']
    totals=request.form['total']
    oida="0"
    lasts=''
    teamid="PNT2022TMID37167"
    sta="open"
    USERNAME=session['id']
    address=name+","+hno+","+area+","+city+","+state+","+"+91"+mno
    sql="SELECT last FROM order WHERE OID=?"
    stmt=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,oida)
    ibm_db.execute(stmt)
    data=ibm_db.fetch_assoc(stmt)
    oid=int(data["LAST"])+1
    tem=str(oid)
    sql="INSERT INTO order VALUES(?,?,?,?,?,?)"
    stmt=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,tem)
    ibm_db.bind_param(stmt,2,product)
    ibm_db.bind_param(stmt,3,address)
    ibm_db.bind_param(stmt,4,totals)
    ibm_db.bind_param(stmt,5,lasts)
    ibm_db.bind_param(stmt,6,sta)
    ibm_db.execute(stmt)
    teamid="PNT2022TMID37167"
    if(totals!=0):
        #for stock
        sql="SELECT CART FROM USERS WHERE USERNAME=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,USERNAME)
        ibm_db.execute(stmt)
        carts= ibm_db.fetch_assoc(stmt)
        cartes=carts["CART"]
        st=list(cartes.split("-"))
        print(st)
        msg = Message('Hello', sender = 'abcdef@gmail.com', recipients =[emaile])
        msg.body = "Hello "+USERNAME+" You have Succefully ordered in Tailored"
        mail.send(msg)
        for pro in st:
            if(pro!=''):
                sql="SELECT STOCK FROM PRODUCT WHERE PID=?"
                stmt=ibm_db.prepare(conn,sql)
                ibm_db.bind_param(stmt,1,pro)
                ibm_db.execute(stmt)
                stocke= ibm_db.fetch_assoc(stmt)
                sat=int(stocke["STOCK"])
                sat=sat-1
                print(sat)
                sql="UPDATE PRODUCT SET STOCK=? WHERE PID=?"
                stmt=ibm_db.prepare(conn,sql)
                ibm_db.bind_param(stmt,1,sat)
                ibm_db.bind_param(stmt,2,pro)
                ibm_db.execute(stmt)
                
        
        sql="UPDATE USERS SET CART='' WHERE USERNAME=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,USERNAME)
        ibm_db.execute(stmt)
        sql="UPDATE ORDER SET LAST=? WHERE OID=?"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,tem)
        ibm_db.bind_param(stmt,2,oida)
        ibm_db.execute(stmt)

    
    return redirect(url_for('cart'))
    

if __name__=='__main__':
    app.run(host='0.0.0.0')





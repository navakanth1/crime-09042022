from flask import Flask, request, render_template, session
import sqlite3

from flask_session import Session
from werkzeug.utils import redirect
from datetime import date

connection = sqlite3.connect("report.db",check_same_thread=False)
table1 = connection.execute("select * from sqlite_master where type = 'table' and name = 'crime'").fetchall()
table2 = connection.execute("select * from sqlite_master where type = 'table' and name = 'user'").fetchall()

if table1!=[]:
    print("Table already exists")
else:
    connection.execute('''create table crime(
                            id integer primary key autoincrement,
                            description text,
                            remarks text,
                            date text);''')
    print("Table created")
if table2!=[]:
    print("Table already exists")
else:
    connection.execute('''create table user(
                            id integer primary key autoincrement,
                            name text,
                            address text,
                            email text,
                            phone integer,
                            password text);''')
    print("Table created successfully")

user = Flask(__name__)

user.config["SESSION_PERMANENT"] = False
user.config["SESSION_TYPE"] = "filesystem"
Session(user)


@user.route('/',methods=['GET','POST'])
def Login_admin():
    if request.method == 'POST':
        getUsername = request.form["name"]
        getPassword = request.form["pass"]
        print(getUsername)
        print(getPassword)
        if getUsername == "admin" and getPassword == "12345":
            return redirect('/dashboard')
        else:
            return redirect('/')
    return render_template("adminlogin.html")

@user.route('/dashboard')
def Admin_dashboard():
    return render_template("admindashboard.html")

@user.route('/view')
def View_report():
    cursor = connection.cursor()
    count = cursor.execute("select * from crime")

    result = cursor.fetchall()
    return render_template("view.html",crime=result)


@user.route('/sort',methods=['GET','POST'])
def Search_crime():
    if request.method == 'POST':
        getDate = str(request.form["date"])
        cursor = connection.cursor()
        count = cursor.execute("select * from crime where date='"+getDate+"' ")
        result = cursor.fetchall()
        if result is None:
            print("There is no Crime on",getDate)
        else:
            return render_template("sortdate.html",crime=result,status=True)
    else:
        return render_template("sortdate.html",crime=[],status=False)



@user.route('/register',methods=['GET','POST'])
def User_register():
    if request.method == 'POST':
        getName = request.form["name"]
        getAddress = request.form["address"]
        getEmail = request.form["email"]
        getPhone = request.form["phone"]
        getPass = request.form["pass"]
        print(getName,getAddress,getEmail,getPhone)
        try:
            connection.execute("insert into user(name,address,email,phone,password) \
            values('"+getName+"','"+getAddress+"','"+getEmail+"',"+getPhone+",'"+getPass+"')")
            connection.commit()
            print("Inserted Successfully")
            return redirect('/complaint')
        except Exception as err:
            print(err)
    return render_template("register.html")

@user.route('/user',methods=['GET','POST'])
def Login_user():
    if request.method == 'POST':
        getEmail = request.form["email"]
        getPass = request.form["pass"]
        cursor = connection.cursor()
        query = "select * from user where email='"+getEmail+"' and password='"+getPass+"' "
        result = cursor.execute(query).fetchall()
        if len(result)>0:
            for i in result:
                getName = i[1]
                getId = i[0]
                session["name"] = getName
                session["id"] = getId
                if (getEmail == i[3] and getPass == i[5]):
                    print("password correct")
                    return redirect('/complaint')

                else:
                    return render_template("userlogin.html",status=True)
    else:
        return render_template("userlogin.html",status=False)

@user.route('/userpage')
def userpage():
    if not session.get("name"):
        return redirect('/')
    else:
        return render_template("userpage.html")


@user.route('/complaint',methods=['GET','POST'])
def Report_crime():
    if request.method == 'POST':
        getDescrip = request.form["description"]
        getRemark = request.form["remark"]
        print(getDescrip)
        print(getRemark)
        getDate = str(date.today())
        cursor = connection.cursor()
        query = "insert into crime(description,remarks,date) values('"+getDescrip+"','"+getRemark+"','"+getDate+"')"
        cursor.execute(query)
        connection.commit()
        print(query)
        print("Inserted Successfully")
        return redirect('/user')
    return render_template("complaint.html")

@user.route('/update',methods=['GET','POST'])
def Update_user():
    global getUser
    if request.method == 'POST':
        getUser = request.form["name"]
        cursor = connection.cursor()
        count = cursor.execute("select * from user where name='"+getUser+"' ")
        return redirect('/edit')
    return render_template("update.html",status=True)


@user.route('/edit',methods=['GET','POST'])
def User_edit():
    if request.method == 'POST':
        getName = request.form["name"]
        getAddress = request.form["address"]
        getEmail = request.form["email"]
        getPhone = request.form["phone"]
        getPass = request.form["pass"]
        connection.execute("update user set name='"+getName+"',address='"+getAddress+"',email='"+getEmail+"',phone="+getPhone+",password='"+getPass+"' where name='"+getUser+"'")
        connection.commit()
        print("Edited Successfully")
        return redirect('/user')


    return render_template("edituser.html")

@user.route('/logout')
def Logout():
    session["name"] = None
    return redirect('/')



if __name__=="__main__":
    user.run()
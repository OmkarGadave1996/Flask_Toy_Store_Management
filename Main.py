from flask import Flask,render_template,redirect,request,session
from werkzeug.utils import secure_filename
import mysql.connector

# Created instance
app = Flask(__name__)   
app.secret_key = "OmyaG"

# It will Show all records from Database
# Change  Database according to your machine
# Create tables also
def showAllRecords():
    # This will connect to database
    mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="******", #There must be your mysql's password   
                database = '*****' # here your database name                       
                )
    cursor = mydb.cursor()
    sql = "select * from Toy" #first create table in your database
    cursor.execute(sql)
    records = cursor.fetchall()    #All records of Toys stored in records
    return render_template("showAllRecords.html", toys=records) #This will Connect to html page and provide records 

def ViewDetails(Id):
    mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="******",   
                database = '*****'                        
                )
    cursor = mydb.cursor()
    sql = "select * from toy where Id=%s" # This will give only one record
    val = (Id,)
    cursor.execute(sql,val)
    record = cursor.fetchone()  
    return render_template("ViewDetails.html",toy = record)

def addToCart():
    # Session is client side server management used to store reord on client machine
    if("uname" not in session): 
            return redirect("/Login") # this will redirect to Login if the seesion id is not matching
    else:
        mydb = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="*****",   
                    database = '*****'                        
                    )
        cursor = mydb.cursor()
        uname = session["uname"] #This will create session id
        Id = request.form["Id"] #tis is data collect from html page id's data store in ID
        qty = request.form["qty"] #and qty's data store in qty
        sql = "select count(*) from MyCart where username=%s and Id=%s" #This will check that data is present in Mycart or not
        val = (uname,Id)
        cursor.execute(sql,val)
        result = cursor.fetchone()
        if(result[0] == 0): #This will execute while data is not present in the Mycart table
            sql = "insert into MyCart(Id,qty,username) values(%s,%s,%s)"    
            val = (Id,qty,uname)
            cursor.execute(sql,val)
            mydb.commit() #This will add the data in Mycart table
            mydb.close()
            return redirect("/ShowAllCartItems")
        else:
            return "Item already present in cart.."
    
def showAllCartItems():
    mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="******",   
                database = '*****'                        
                )
    cursor = mydb.cursor()
    sql = '''select t.Id,t.name,t.price,
             t.image_url,m.qty from toy t 
             inner join mycart m on t.Id = m.Id 
             and m.username=%s'''
    val = (session["uname"],)
    cursor.execute(sql,val)
    records = cursor.fetchall()

    sql1 = "select sum(price*qty) from cartitems_vw where username=%s" #view=virtual table created on statement
    val1 = (session["uname"],)
    cursor.execute(sql1,val1)
    sum = cursor.fetchone()[0]
    session["total"] = sum #total store in session

    return render_template("showAllCartItems.html",toys = records)

def RemoveItem(Id):
    mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="******",   
                database = '*****'                        
                )
    cursor = mydb.cursor()
    sql = "delete from mycart where username=%s and Id=%s"
    val = (session["uname"],Id)
    cursor.execute(sql,val)
    mydb.commit()
    mydb.close()
    return redirect("/ShowAllCartItems")

def updateItem():
    mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="******",   
                database = '*****'                        
                )
    cursor = mydb.cursor()
    uname = session["uname"]
    Id = request.form["Id"]
    qty = request.form["qty"]
    sql = "update mycart set qty=%s where Id=%s and username=%s"
    val = (qty,Id,uname)
    cursor.execute(sql,val)
    mydb.commit()
    mydb.close()
    return redirect("/ShowAllCartItems")
    
def MakePayment():
    if(request.method == "GET"):
        return render_template("MakePayment.html")
    else:
        cardno = request.form["cardno"]
        cvv = request.form["cvv"]
        expiry = request.form["expiry"]
        mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="******",   
                database = '*****'                        
                )
        cursor = mydb.cursor()
        sql = "select count(*) from carddetails where cardno=%s and cvv=%s and expiry=%s" #as like mycart its check in carddetail table
        val = (cardno,cvv,expiry)
        cursor.execute(sql,val)
        record = cursor.fetchone()
        if(int(record[0])==1): #but this time this must be 1 because user must present in table
            amount = session["total"]
            sql1="update carddetails set amount = amount - %s where cardno=%s" # this will delete from buyer account
            sql2="update carddetails set amount = amount + %s where cardno=222" # this will add in seller account
            val1=(amount,cardno)
            val2=(amount,)
            cursor.execute(sql1,val1)
            cursor.execute(sql2,val2)
            
            #This is like order master saves information of purchased item, buyer name and time
            sql3 = "insert into Transaction_history select Id,name,price,qty,username,now(),%s from cartitems_vw where username=%s"
            val3 = (amount,session["uname"])
            cursor.execute(sql3,val3)
            
            sql4 = "delete from Mycart where username = %s" # after transaction this will delete the records from mycart 
            val4 = (session["uname"],)
            cursor.execute(sql4,val4)

            mydb.commit()
            mydb.close()    
            return redirect("/")
        
def Login():
    if(request.method == "GET"):
        return render_template("Login.html")
    else:
        uname = request.form["uname"]
        pwd = request.form["pwd"]
        mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="******",   
                database = '*****'                        
                )
        cursor = mydb.cursor()
        sql = "select count(*) from user_info where username=%s and password=%s"
        val = (uname,pwd)
        cursor.execute(sql,val)
        count = cursor.fetchone() 
        count = int(count[0])
        if(count==1): # this check user is present in table
            session["uname"] = uname
            return redirect("/")
        else:
            return redirect("/Login")

def Signup():
    if(request.method == "GET"):
        return render_template("Signup.html")
    else:
        mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="******",   
                database = '*****'                        
                )
        cursor = mydb.cursor()
        uname = request.form["uname"]
        pwd = request.form["pwd"]
        sql = "select count(*) from user_info where username=%s and password=%s"
        val = (uname,pwd)
        cursor.execute(sql,val)
        result = cursor.fetchone()
        if(result[0] == 0): #if user not present this will add user
            email = request.form["email"]
            sql = "insert into user_info values(%s,%s,%s)"    
            val = (uname,pwd,email)
            cursor.execute(sql,val)
            mydb.commit()
            mydb.close()
            return redirect("/Login")
        else:
            return redirect("/Signup")
                
def SignOut():
    session.clear() # this will clear information stored on client machine
    return redirect("/")

@app.route('/Adminlogin', methods=["GET","POST"])
def Adminlogin():
    if(request.method == "GET"):
        return render_template("Adminlogin.html")
    else:
        aname = request.form["aname"]
        pwd = request.form["pwd"]
        mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="******",   
                database = '*****'                        
                )
        cursor = mydb.cursor()
        sql = "select count(*) from admin_info where username=%s and password=%s and role='Admin' "
        val = (aname,pwd)
        cursor.execute(sql,val)
        count = cursor.fetchone() 
        count = int(count[0])
        if(count==1):
            session["aname"] = aname
            return redirect("/AdminHome")
        else:
            return redirect("/Adminlogin")

@app.route("/AdminHome")
def Adminhome():
    if("aname in session"):
        mydb =  mysql.connector.connect(
                host="localhost",
                user="root",
                password="******",   
                database = '*****'                        
                )
        cursor = mydb.cursor()
        sql = "select * from Toy"
        cursor.execute(sql)
        records = cursor.fetchall()
        return render_template("AdminHome.html",toys=records)
    else:
       return redirect("/Adminlogin")

@app.route("/Remove/<id>")
def Remove(id):
    mydb =  mysql.connector.connect(
                host="localhost",
                user="root",
                password="******",   
                database = '*****'                        
                )
    cursor = mydb.cursor()
    sql = 'delete from Toy where Id=%s'
    val = (id,)
    cursor.execute(sql,val)
    mydb.commit()
    mydb.close()
    return redirect("/AdminHome")

@app.route("/edit/<id>",methods=["GET","POST"])
def edit(id):
    mydb =  mysql.connector.connect(
                host="localhost",
                user="root",
                password="******",   
                database = '*****'                        
                )
    cursor = mydb.cursor()
    if(request.method == "GET"):
        sql = "select * from toy where Id=%s"
        val = (id,)
        cursor.execute(sql,val)
        item = cursor.fetchone
        return render_template("edittoy.html",toy=item)
    else:
        tname = request.form["tname"]
        price = request.form["price"]
        qty   = request.form["qty"]
        image = request.form["image"]
        sql = "update toy set Name=%s,price=%s,qty=%s,image_url=%s where Id=%s"
        val = (tname,price,qty,image,id)
        cursor.execute(sql,val)
        mydb.commit()
        mydb.close()        
        return redirect("/AdminHome")
    
@app.route("/AddRecord",methods=["GET","POST"])
def AddRecord():
    if("aname" not in session):
        return redirect("/Adminlogin")
    else:
        if(request.method == "GET"):
            return render_template("addrecord.html")
        else:
            tname = request.form["tname"]
            price = request.form["price"]
            qty   = request.form["qty"]
            f = request.files["image"]
            f.save("static\\images\\product"+secure_filename(f.filename)) # this will save image in machine
            mydb = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="******",   
                    database = '******'                        
                    )
            cursor = mydb.cursor()
            sql = "insert into toy(Name,price,qty,image_url) values(%s,%s,%s,%s)"
            val = (tname,price,qty,f.filename)
            cursor.execute(sql,val)
            mydb.commit()
            mydb.close()
            return redirect("/AdminHome")

app.add_url_rule('/','', showAllRecords)
app.add_url_rule('/Login','Login', Login,methods=["GET","POST"])
app.add_url_rule('/Signup','Signup', Signup,methods=["GET","POST"])
app.add_url_rule('/ViewDetails/<Id>','abc', ViewDetails)
app.add_url_rule('/addToCart','addToCart', addToCart,methods=["GET","POST"])
app.add_url_rule('/ShowAllCartItems','ShowAllCartItems', showAllCartItems)
app.add_url_rule('/updateItem','updateItem', updateItem,methods=["GET","POST"])
app.add_url_rule('/RemoveItem/<Id>','RemoveItem', RemoveItem)
app.add_url_rule('/MakePayment','MakePayment', MakePayment,methods=["GET","POST"])
app.add_url_rule("/SignOut",'signout',SignOut)


        

if(__name__ == "__main__"):
    app.run(debug=True)
import pymongo
from flask import Flask, request, render_template , session, redirect
import datetime
from bson import ObjectId
app = Flask(__name__)
app.secret_key = "Saikumar"
my_client = pymongo.MongoClient('mongodb://localhost:27017')
my_db = my_client["Train_Booking"]
admin_col = my_db['admin']
customer_col = my_db['customer']
train_col = my_db['train']
compartment_col = my_db['compartment']
schedule_col = my_db['schedule']
booking_col = my_db['booking']
payment_col = my_db['payment']
ticket_col = my_db['ticket']

count = admin_col.count_documents({})
if count == 0:
    admin = {"Admin_Email": "admin@gmail.com", "Admin_Password": "admin"}
    admin_col.insert_one(admin)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/adminlog")
def adminlog():
    return render_template("adminlog.html")

@app.route("/adminlog1", methods=['post'])
def adminlog1():
    Admin_Email = request.form.get("Admin_Email")
    Admin_Password = request.form.get("Admin_Password")
    query = {"Admin_Email":Admin_Email , "Admin_Password":Admin_Password}
    admin = admin_col.find_one(query)
    if admin != None:
        session['admin_id'] = str(admin['_id'])
        session['role'] = 'Admin'
        return redirect("admin_home")
    else:
        return render_template("message.html" , message="Fail to Log")

@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")

@app.route("/customerlog")
def customerlog():
    return render_template("customerlog.html")

@app.route("/customerlog1", methods = ['post'])
def customerlog1():
    customer_email = request.form.get("customer_email")
    customer_password = request.form.get("customer_password")
    query = {"customer_email": customer_email, "customer_password": customer_password}
    count = customer_col.count_documents(query)
    if count > 0:
        customer = customer_col.find_one(query)
        session['customer_id'] = str(customer['_id'])
        session['role'] = 'customer'
        return render_template("customer_home.html")
    else:
        return render_template("message.html", message="Fail to Login")

@app.route("/customer_home")
def customer_home():
    return render_template("customer_home.html")

@app.route("/customerreg")
def customerreg():
    return render_template("customerreg.html")

@app.route("/customerreg1", methods = ['post'])
def customerreg1():
    customer_name = request.form.get("customer_name")
    customer_email = request.form.get("customer_email")
    customer_phone = request.form.get("customer_phone")
    customer_password = request.form.get("customer_password")
    gender = request.form.get("gender")
    age = request.form.get("age")
    query = {"$or": [{"customer_email": customer_email}, {"customer_phone": customer_phone}]}
    count = customer_col.count_documents(query)
    if count == 0:
        customer = {"customer_name": customer_name, "customer_email": customer_email, "customer_phone": customer_phone, "customer_password": customer_password, "gender": gender, "age": age}
        customer_col.insert_one(customer)
        return render_template("message.html", message="Customer Registration Successfull")
    else:
        return render_template("message.html", message="Already Exists")


@app.route("/add_train")
def add_train():
    return render_template("add_train.html")

@app.route("/add_train1", methods = ['post'])
def add_train1():
    train_name = request.form.get("train_name")
    train_number = request.form.get("train_number")
    query = {"train_name": train_name}
    count = train_col.count_documents(query)
    if count == 0:
        train = {"train_name": train_name, "train_number": train_number}
        train_col.insert_one(train)
        return redirect("/view_train")
    else:
        return render_template("amessage.html", message="Fail to Add")

@app.route("/view_train")
def view_train():
    trains = train_col.find()
    return render_template("view_train.html", trains=trains, get_train_id=get_train_id)

def get_train_id(train_id):
    query = {"train_id": ObjectId(train_id)}
    compartments = compartment_col.find(query)
    return compartments

@app.route("/add_compartment")
def add_compartment():
    trains = train_col.find()
    return render_template("add_compartment.html", trains=trains)

@app.route("/add_compartment1", methods = ['post'])
def add_compartment1():
    train_id = request.form.get("train_id")
    no_of_seats = request.form.get("no_of_seats")
    compartment_name = request.form.get("compartment_name")
    class_type = request.form.get("class_type")
    price_per_seat = request.form.get("price_per_seat")
    query = {"train_id": ObjectId(train_id), "compartment_name": compartment_name, "no_of_seats": no_of_seats, "class_type": class_type, "price_per_seat": price_per_seat}
    compartment_col.insert_one(query)
    return render_template("amessage.html", message="Compartment Added")

@app.route("/add_schedule")
def add_schedule():
    train_id = request.args.get("train_id")
    return render_template("add_schedule.html",train_id=train_id)

@app.route("/add_schedule1", methods = ['post'])
def add_schedule1():
    train_id = request.form.get("train_id")
    platform_number = request.form.get("platform_number")
    from_station = request.form.get("from_station")
    to_station = request.form.get("to_station")
    date = request.form.get("date")
    start_date_time = request.form.get("start_date_time")
    end_date_time = request.form.get("end_date_time")
    start_date_time = start_date_time.replace("T", ' ')
    end_date_time = end_date_time.replace("T", ' ')
    start_date_time = datetime.datetime.strptime(start_date_time, "%Y-%m-%d %H:%M")
    end_date_time = datetime.datetime.strptime(end_date_time, "%Y-%m-%d %H:%M")
    start_date = str(start_date_time.date())
    query = {"train_id": ObjectId(train_id),"platform_number":platform_number,"from_station": from_station,"to_station": to_station,"date": date,"start_date":start_date,"start_date_time":start_date_time,"end_date_time":end_date_time}
    schedule_col.insert_one(query)
    return render_template("amessage.html", message="Schedule Added")

@app.route("/view_schedule")
def view_schedule():
    source = request.args.get("source")
    destination = request.args.get("destination")
    date = request.args.get("date")
    train_id = request.args.get("train_id")
    trains = train_col.find()
    if source == None:
        source = ''
    if destination == None:
        destination = ''
    if train_id == None:
        train_id = ''
    if date == None or date == '':
        date = str(datetime.datetime.now().date())
    if train_id == '':
        if source == '' and destination == '':
            query = {"date": date}
        elif source == '' and destination != '':
            query = {"date": date, "to_station": destination}
        elif source != '' and destination == '':
            query = {"date": date, "from_station": source}
        elif source != '' and destination != '':
            query = {"date": date, "from_station": source, "to_station": destination}
    else:
        if source == '' and destination == '':
            query = {"date": date, "train_id": ObjectId(train_id)}
        elif source == '' and destination != '':
            query = {"date": date, "to_station": destination, "train_id": ObjectId(train_id)}
        elif source != '' and destination == '':
            query = {"date": date, "from_station": source, "train_id": ObjectId(train_id)}
        elif source != '' and destination != '':
            query = {"date": date, "from_station": source, "to_station": destination, "train_id": ObjectId(train_id)}
    schedules = schedule_col.find(query)
    schedules = list(schedules)
    return render_template("view_schedule.html", schedules=schedules,destination=destination,source=source,date=date, get_schedule_id=get_schedule_id, trains=trains, get_train_id_by_schedules=get_train_id_by_schedules, formate_date_time=formate_date_time, get_compartment_by_train_id=get_compartment_by_train_id,str=str, train_id=train_id)

def get_schedule_id():
    schedules = schedule_col.find()
    stations = []
    for schedule in schedules:
        stations.append(schedule['from_station'])
        stations.append(schedule['to_station'])
    stations = set(stations)
    return stations

def get_train_id_by_schedules(schedule_id):
    query = {"_id": ObjectId(schedule_id)}
    schedule = schedule_col.find_one(query)
    train_id = schedule['train_id']
    query = {"_id": ObjectId(train_id)}
    train = train_col.find_one(query)
    return train

def get_compartment_by_train_id(train_id):
    query = {"train_id": train_id}
    compartments = compartment_col.find(query)
    return compartments

@app.route("/book")
def book():
    compartment_id = request.args.get("compartment_id")
    schedule_id = request.args.get("schedule_id")
    query = {"_id":ObjectId(schedule_id)}
    schedule = schedule_col.find_one(query)
    query = {"_id":ObjectId(compartment_id)}
    compartment = compartment_col.find_one(query)
    train_id = compartment['train_id']
    query = {"_id": ObjectId(train_id)}
    train = train_col.find_one(query)
    return render_template("book.html",compartment=compartment,train=train,schedule=schedule, int=int,compartment_id=compartment_id,schedule_id=schedule_id,is_seat_booked=is_seat_booked)

@app.route("/book_seat", methods = ['post'])
def book_seat():
    date = str(datetime.datetime.now().date())
    customer_id = session['customer_id']
    schedule_id = request.form.get("schedule_id")
    compartment_id = request.form.get("compartment_id")
    query = {"_id": ObjectId(compartment_id)}
    compartment = compartment_col.find_one(query)
    selected_seats = []
    for i in range(1, int(compartment['no_of_seats'])+1):
        selected_seat = request.form.get(str(i))
        if selected_seat != None:
            selected_seats.append(i)
    query = {"schedule_id": ObjectId(schedule_id),"compartment_id":ObjectId(compartment_id),"customer_id": ObjectId(customer_id),"date":date,"seats":selected_seats,"status":"Payment Pending"}
    result = booking_col.insert_one(query)
    booking_id = result.inserted_id
    total_amount = int(compartment['price_per_seat'])*len(selected_seats)
    return render_template("book_seat.html",booking_id=booking_id,total_amount=total_amount, selected_seats=selected_seats)

@app.route("/pay", methods = ['post'])
def pay():
    booking_id = request.form.get("booking_id")
    total_amount = request.form.get("total_amount")
    date = str(datetime.datetime.now().date())
    card_type = request.form.get("card_type")
    card_holder_name = request.form.get("card_holder_name")
    card_number = request.form.get("card_number")
    expiry_date = request.form.get("expiry_date")
    cvv = request.form.get("cvv")
    payment = {"booking_id":ObjectId(booking_id),"total_amount":total_amount,"date":date,"card_type":card_type,"card_holder_name":card_holder_name,"card_number":card_number,"expiry_date":expiry_date,"cvv":cvv,"status":"Transaction Successfull"}
    payment_col.insert_one(payment)
    query = {"_id":ObjectId(booking_id)}
    query1 = {"$set": {"status": "Payment Successfully","total_amount":total_amount}}
    booking_col.update_one(query,query1)
    booking = booking_col.find_one(query)
    passengers = []
    for seat in booking['seats']:
        passenger_name = request.form.get("passenger_name"+str(seat))
        age = request.form.get("age"+str(seat))
        gender = request.form.get("gender"+str(seat))
        passengers.append({"passenger_name": passenger_name, "age": age, "gender": gender})
        query = {"booking_id": ObjectId(booking_id),"passenger_name": passenger_name, "age": age, "gender": gender,"seat":seat,"date":date,"status":"Ticked Confirmed"}
        ticket_col.insert_one(query)
    query = {"_id": ObjectId(session['customer_id'])}
    print(query)
    query2 = {"$set": {"passengers": passengers}}
    print(query2)
    customer_col.update_one(query, query2)
    return render_template("cmessage.html" , message="Payment Successfully")

@app.route("/view_bookings")
def view_bookings():
    if session["role"] == 'Admin':
        compartment_id = request.args.get('compartment_id')
        schedule_id = request.args.get('schedule_id')
        query = {"compartment_id": ObjectId(compartment_id),"schedule_id":ObjectId(schedule_id) }
    else:
        customer_id = session['customer_id']
        query = {"customer_id":ObjectId(customer_id)}
    bookings = booking_col.find(query)
    return render_template("view_bookings.html",bookings=bookings,get_booking_id=get_booking_id,get_tickets_by_booking_id=get_tickets_by_booking_id)

def get_tickets_by_booking_id(booking_id):
    query = {"booking_id": ObjectId(booking_id)}
    tickets = ticket_col.find(query)
    return tickets

def get_booking_id(booking_id):
    query = {"_id": ObjectId(booking_id)}
    booking = booking_col.find_one(query)
    schedule_id = booking['schedule_id']
    query3 = {"_id": ObjectId(schedule_id)}
    schedule = schedule_col.find_one(query3)
    compartment_id = booking['compartment_id']
    query1 = {"_id": ObjectId(compartment_id)}
    compartment = compartment_col.find_one(query1)
    train_id = compartment['train_id']
    query2 = {"_id": ObjectId(train_id)}
    train = train_col.find_one(query2)
    return compartment,train,schedule

@app.route("/view_payment")
def view_payment():
    booking_id = request.args.get("booking_id")
    query = {"booking_id": ObjectId(booking_id)}
    payment = payment_col.find_one(query)
    return render_template("view_payment.html",payment=payment)

@app.route("/cancel_ticket")
def cancel_ticket():
    booking_id = request.args.get("booking_id")
    query = {"_id": ObjectId(booking_id)}
    query2 = {"$set": {"status":"Ticket Cancelled"}}
    booking_col.update_one(query,query2)
    query = {"booking_id": ObjectId(booking_id)}
    query2 = {"$set": {"status": "Payment Returned"}}
    payment_col.update_one(query, query2)
    return render_template("cmessage.html" , message="Ticket Cancelled")

def formate_date_time(date):
    date = datetime.datetime.strptime(str(date)[:-3],"%Y-%m-%d %H:%M")
    date = str(date.date())+" "+str(date.strftime("%I"))+":"+str(date.strftime("%M"))+" "+str(date.strftime("%p"))
    return date

def is_seat_booked(compartment_id,seat,schedule_id):
    query = {"compartment_id":compartment_id,"schedule_id":schedule_id, "status":"Payment Successfully"}
    count = booking_col.count_documents(query)
    if count == 0 :
        return False
    bookings = booking_col.find(query)
    for booking in bookings:
        if int(seat) in booking['seats']:
            return True
    return False


@app.route("/logout")
def logout():
    session.clear()
    return render_template("index.html")

app.run(debug=True)
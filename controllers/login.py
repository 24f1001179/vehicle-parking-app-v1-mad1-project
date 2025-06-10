from flask import Flask, session, request
from flask import render_template, url_for, redirect
from controllers.bp import generalbp
from controllers.adminDashboard import dashboard, totalNoOfType, sumOfTotalCosts
from controllers.userDashboard import dashboard
from dbInit import db
from models.userInfo import User, Admin, Address
from sqlalchemy.exc import IntegrityError

@generalbp.route("/signIn", methods = ["GET", "POST"])
def signIn() :
    if request.method == "GET" :
        return render_template("general/signIn.html")
    elif request.method == "POST" :
        type = request.form["type"]
        email = request.form["email"]
        password = request.form["password"]
        if type == "user" :
            if userAuth(email, password) :
                return redirect(url_for("user.dashboard"))
        elif type == "admin" :
            if adminAuth(email, password) :
                return redirect(url_for("admin.dashboard"))
        return redirect(url_for("general.signIn"))

def userAuth(email, password) :
    user = db.session.execute(db.select(User).filter_by(email = email, password = password)).scalars().first()
    if user is not None :
        session["id"] = user.id
        session["type"] = "user"
        return True
    return False

def adminAuth(email, password) :
    admin = db.session.execute(db.select(Admin).filter_by(email = email, password = password)).scalars().first() #scalars() is used to get the model object directly
    if admin is not None :
        session["id"] = admin.id
        session["type"] = "admin"
        return True
    return False

@generalbp.route("/signUp", methods = ["GET", "POST"])
def signUp() :
    if request.method == "GET" :
        return render_template("general/signUp.html")
    elif request.method == "POST" :
        email = request.form["email"]
        password = request.form["password"]
        #checking if the email or password is already taken
        user1 = db.session.execute(db.select(User).filter_by(email = email)).scalars().first()
        user2 = db.session.execute(db.select(User).filter_by(password = password)).scalars().first()
        if user1 is None and user2 is None : #proceed if email or password is not taken
            session["email"] = email #add it in session in order to get the value in /signUp/additionalDetails page
            session["password"] = password
            return redirect(url_for("general.additionalDetails"))
        return redirect(url_for("general.signUp")) #else redirect to the sign up page again
    
@generalbp.route("/signUp/additionalDetails", methods = ["GET", "POST"])
def additionalDetails() :
    if request.method == "GET" :
        return render_template("general/additionalDetails.html")
    elif request.method == "POST" :
        email = session.pop("email", None)
        password = session.pop("password", None) #if password is not present in session then None is returned. Without None KeyError is thrown.
        firstName = request.form["firstName"]
        lastName = request.form["lastName"]
        age = request.form["age"]
        streetName = request.form["streetName"]
        locality = request.form["locality"]
        subLocality = request.form["subLocality"]
        city = request.form["city"]
        state = request.form["state"]
        pinCode = request.form["pinCode"]
        address = Address(streetName = streetName, locality = locality, subLocality = subLocality, city = city, state = state, pinCode = pinCode)
        user = User(email = email, password = password, firstName = firstName, lastName = lastName, age = age)
        if createUser(address, user) :
            return redirect(url_for("user.dashboard"))
        return redirect(url_for("general.signUp")) #if some error occured when inserting the record then redirect to the sign up page

def createUser(address, user) :
    try :
        db.session.add(address)
        db.session.flush() #creates the autoincrement id but does not commit
        user.address = address
        db.session.add(user)
        db.session.commit()
        session["id"] = user.id
        session["type"] = "user"
        return True
    except IntegrityError as e :
        db.session.rollback() #roll back if some error occurs and commit is not done
        return False

def floorTens(i) :
    no = pow(10, len(str(i)) - 1)
    return ( i // no ) * no

@generalbp.route("/", methods = ["GET"])
def landingPage() :
    d = {"Skip The Queue" : ["Reserve Your Spot In Advance And Be Ensured Guaranteed Availability When You Arrive.", "check2-all"], "Flexibile Cancellations" : ["Change Of Plans? Easily Cancel Your Reservation At Any Time Free Of Cost.", "trash2"], "Seamless Payments" : ["Automatic Cost Computation Enabling Faster Payments Without Having To Wait In Lines.", "paypal"], "Track History" : ["Effortlessly Acces Your Complete List Of Reservations And Past Parking Sessions.", "clock-history"], "Insightful Summary" : ["Make Smarter Parking Choices Using Summary Charts.", "bar-chart-fill"]}
    di = {"Parking Lots" : floorTens(totalNoOfType("ParkingLot")), "Parking Spots" : floorTens(totalNoOfType("ParkingSpot")), "Parkings" : floorTens(totalNoOfType("ReservedParkingSpot")), "Revenue Generated" : floorTens(sumOfTotalCosts())}
    return render_template("general/landingPage.html", d = d, di = di)
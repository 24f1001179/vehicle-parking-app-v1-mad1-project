from flask import Flask, request, session
from flask import render_template, url_for, redirect
from dbInit import db
from controllers.bp import adminbp 
from models.parkingInfo import ParkingLot, ParkingSpot, ReservedParkingSpot
from models.userInfo import User, Address
from sqlalchemy.exc import IntegrityError

@adminbp.before_request
def restrict() :
    if session.get("type") != "admin" :
        return redirect(url_for("general.signIn"))

@adminbp.route("/dashboard", methods = ["GET", "POST"])
def dashboard() :
    if request.method == "GET" :
        return render_template("adminDashboard.html", parkingLots = viewParkingLots())
    if request.method == "POST" :
        id = request.form.get("parkingLotId") #returns None if parkingLotId is not present in request.form #this happens when user performs action create
        action = request.form["action"]
        if action == "create" :
            session["action"] = action
            session["id"] = False
            return redirect(url_for("admin.parkingLotAction"))
        elif action == "edit" :
            parkingLot = getParkingLot(id)
            session["action"] = action
            session["id"] = id
            return redirect(url_for("admin.parkingLotAction"))
        elif action == "delete" :
            deleteParkingLot(getParkingLot(id))
            return render_template("adminDashboard.html", parkingLots = viewParkingLots())

@adminbp.route("/dashboard/action", methods = ["GET", "POST"])
def parkingLotAction() :
    id = session.get("id")
    action = session.get("action")
    if id :
        parkingLot = getParkingLot(id)
    else :
        address = Address(streetName = "", locality = "", subLocality = "", city = "", state = "", pinCode = "")
        parkingLot = ParkingLot(landmark = "", noOfParkingSpots = "", pricePerHr = "")
        parkingLot.address = address
    if request.method == "GET" :
        return render_template("parkingLotAction.html", action = action, pl = parkingLot)
    elif request.method == "POST" :
        oldNoOfParkingSpots = parkingLot.noOfParkingSpots
        newNoOfParkingSpots = request.form["nps"]
        parkingLot.address.streetName = request.form["n"]
        parkingLot.address.locality = request.form["l"]
        parkingLot.address.subLocality = request.form["sl"]
        parkingLot.address.city = request.form["c"]
        parkingLot.address.state = request.form["s"]
        parkingLot.address.pinCode = request.form["p"]
        parkingLot.landmark = request.form["la"]
        #parkingLot.noOfParkingSpots = request.form["nps"]  #no need to update as -= 1 is dont in deleteParkingSpot function which is called by updateParkingLot function
        parkingLot.pricePerHr = request.form["pph"]
        if action == "create" :
            createParkingLot(parkingLot, newNoOfParkingSpots) 
        elif action == "edit" : 
            if(not updateParkingLot(parkingLot, oldNoOfParkingSpots, newNoOfParkingSpots)) :
                return redirect(url_for("admin.parkingLotAction"))
        session.pop("action")
        session.pop("id")
        return redirect(url_for("admin.dashboard"))

def getParkingLot(id) :
    return db.session.execute(db.select(ParkingLot).filter_by(id = id)).scalars().first()

def createParkingLot(parkingLot, nps) :
    try :
        db.session.add(parkingLot)
        db.session.commit()
        id = parkingLot.id
        for i in range(nps) :
            parkingSpot = ParkingSpot(status = False, parkingLotId = id)
            db.session.add(parkingSpot)
            parkingLot.parkingSpots += 1
        db.session.commit()
    except IntegrityError as e :
        db.session.rollback()

def viewParkingLots() :
    parkingLots = db.session.execute(db.select(ParkingLot)).scalars().all()
    return parkingLots

def updateParkingLot(parkingLot, onps, nps) :
    try :
        id = parkingLot.id
        diff = int(onps) - int(nps)
        if(diff < 0) :
            for i in range(abs(diff)) :
                parkingSpot = ParkingSpot(status = False, parkingLotId = id)
                db.session.add(parkingSpot)
                db.session.commit()
                parkingLot.noOfParkingSpots += 1
            db.session.add(parkingLot)
            db.session.commit()
        elif(diff > 0) :
            for i in range(diff) :
                if(deleteParkingSpot(parkingLot) == None) :
                    return False
            db.session.add(parkingLot)
            db.session.commit()
        return True
    except IntegrityError as e :
        db.session.rollback()

def deleteParkingLot(parkingLot) :
    address = parkingLot.address
    parkingSpots = parkingLot.parkingSpots
    db.session.delete(address)
    db.session.delete(parkingLot)
    for i in range(len(parkingSpots)) :
        db.session.delete(parkingSpots[i])
    db.session.commit()

def viewParkingSpots(parkingLot) :
    return parkingLot.parkingSpots

def createParkingSpots(parkingLot) :
    id = parkingLot.id 
    parkingSpot = ParkingSpot(status = False, parkingLotId = id)
    db.session.add(parkingSpot)
    db.session.commit()

def deleteParkingSpot(parkingLot) :
    parkingSpots = parkingLot.parkingSpots
    for parkingSpot in parkingSpots :
        if parkingSpot.status == False :
            parkingLot.noOfParkingSpots -= 1
            db.session.add(parkingLot)
            db.session.delete(parkingSpot)
            db.session.commit()
            return parkingSpot
    return None

def viewUsers() :
    users = db.session.execute(db.select(User)).scalars().all()
    return users
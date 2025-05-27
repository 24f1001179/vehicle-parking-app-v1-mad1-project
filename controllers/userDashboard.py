from flask import Flask, request, session
from flask import render_template, url_for, redirect
from controllers.bp import userbp 
from dbInit import db
from models.userInfo import User
from models.parkingInfo import ParkingSpot, ReservedParkingSpot, ParkingLot
from controllers.adminDashboard import viewParkingLots
from datetime import datetime
from math import ceil

@userbp.before_request
def restrict() :
    if session.get("type") != "user" :
        return redirect(url_for("general.signIn"))

@userbp.route("/dashboard", methods = ["GET", "POST"])
def dashboard() :
    if request.method == "GET" :
        return render_template("user/userDashboard.html", parkingLots = viewParkingLots())
    elif request.method == "POST" :
        session["parkingLotId"] = request.form["parkingLotId"]
        return redirect(url_for("user.vehicleNo"))
    return render_template("user/userDashboard.html", parkingLots = viewParkingLots())

@userbp.route("/dashboard/details", methods = ["GET", "POST"])
def vehicleNo() :
    if request.method == "GET" :
        return render_template("user/userVehicleNo.html")
    elif request.method == "POST" :
        vehicleNo = request.form["vehicleNo"]
        if createReservedParkingSpot(vehicleNo) :
            return redirect(url_for("user.reserved"))
        else :
            return redirect(url_for("user.dashboard"))
    return render_template("user/userVehicleNo.html")

@userbp.route("/dashboard/reserved", methods = ["GET", "POST"])
def reserved() :
    if request.method == "GET" :
        reserved = currentReservedParkingSpot()
        return render_template("user/reservedSpot.html", reservedParkingSpot = reserved)
    elif request.method == "POST" :
        id = request.form["reservedParkingSpotId"]
        action = request.form["action"]
        if action == "release" :
            deleteReservedParkingSpot(id)
        elif action == "occupy" :
            addParkingTimestamp(id)
            return redirect(url_for("user.reserved"))
        elif action == "vaccate" :
            addLeavingTimestampAndTotalCost(id)
        return redirect(url_for("user.dashboard"))
    return render_template("user/reservedSpot.html")

@userbp.route("/dashboard/history", methods = ["GET"])
def history() :
    return render_template("user/reservedSpotHistory.html", reservedParkingSpots = viewAllReservedParkingSpots())

def addParkingTimestamp(id) :
    now = datetime.now()
    reservedParkingSpot = getReservedParkingSpot(id)
    reservedParkingSpot.parkingTimestamp = now
    reservedParkingSpot.parkingSpot.status = True
    db.session.commit()

def addLeavingTimestampAndTotalCost(id) :
    now = datetime.now()
    reservedParkingSpot = getReservedParkingSpot(id)
    reservedParkingSpot.leavingTimestamp = now
    hrs = (reservedParkingSpot.leavingTimestamp - reservedParkingSpot.parkingTimestamp).total_seconds() / 3600
    totalCost = ceil(hrs) * reservedParkingSpot.parkingSpot.parkingLot.pricePerHr
    reservedParkingSpot.totalCost = totalCost
    reservedParkingSpot.parkingSpot.status = False
    db.session.commit()

def getReservedParkingSpot(id) :
    return db.session.execute(db.select(ReservedParkingSpot).filter_by(id = id)).scalars().first()

def deleteReservedParkingSpot(id) :
    db.session.delete(getReservedParkingSpot(id))
    db.session.commit()

def createReservedParkingSpot(vehicleNo) :
    if currentReservedParkingSpot() is None:
        parkingLotId = session.pop("parkingLotId")
        aParkingSpot = db.session.execute(db.select(ParkingSpot).filter_by(status = False, parkingLotId = parkingLotId)).scalars().first()
        thisUser = db.session.execute(db.select(User).filter_by(id = session["id"])).scalars().first()
        if aParkingSpot is None :
            return False
        reservedParkingSpot = ReservedParkingSpot(parkingSpot = aParkingSpot, user = thisUser, vehicleNumber = vehicleNo)
        db.session.add(reservedParkingSpot)
        db.session.commit()
        return True 
    return False

def viewAllReservedParkingSpots() :
    return db.session.execute(db.select(ReservedParkingSpot).filter_by(userId = session["id"])).scalars().all()

def currentReservedParkingSpot() :
    return db.session.execute(db.select(ReservedParkingSpot).filter_by(userId = session["id"], totalCost = None)).scalars().first()

@userbp.route("/dashboard/summary", methods = ["GET"])
def summary() :
    if request.method == "GET" :
        return render_template("user/summary.html", reservedParkingSpots = viewAllReservedParkingSpots() )
    
@userbp.route("/dashboard/searchResults", methods = ["POST"])
def searchResults() :
    type = request.form["type"]
    searchValue = request.form["searchValue"].lower()
    newRecs = []
    model = globals()[type]
    for i in db.session.execute(db.select(model)).scalars().all() :
        j = i.__str__()
        if searchValue in j :
            newRecs.append(j[0])
    searchResult = db.session.execute(db.select(model).filter(model.id.in_(newRecs))).scalars().all()
    if type == "ParkingLot" :
        return render_template("user/userDashboard.html", parkingLots = searchResult)

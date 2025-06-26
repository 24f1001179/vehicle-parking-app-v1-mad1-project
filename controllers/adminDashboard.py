from flask import Flask, request, session
from flask import render_template, url_for, redirect
from dbInit import db
from controllers.bp import adminbp 
from models.parkingInfo import ParkingLot, ParkingSpot, ReservedParkingSpot
from models.userInfo import User, Address
from sqlalchemy.exc import IntegrityError
from sqlalchemy import nulls_first, desc
import matplotlib.pyplot as plt

@adminbp.before_request
def restrict() :
    if session.get("type") != "admin" :
        return redirect(url_for("general.signIn"))

@adminbp.route("/dashboard", methods = ["GET", "POST"])
def dashboard() :
    if request.method == "GET" :
        return render_template("admin/adminDashboard.html", parkingLots = viewParkingLots())
    if request.method == "POST" :
        id = request.form.get("parkingLotId") #returns None if parkingLotId is not present in request.form #this happens when user performs action create
        action = request.form["action"]
        if action == "create" :
            session["action"] = action
            session["id"] = id
            return redirect(url_for("admin.parkingLotAction"))
        elif action == "edit" :
            session["action"] = action
            session["id"] = id
            return redirect(url_for("admin.parkingLotAction"))
        elif action == "delete" :
            deleteParkingLot(getParkingLot(id))
            return redirect(url_for("admin.dashboard"))
        elif action == "details" :
            session["action"] = action
            session["id"] = id
            return redirect(url_for("admin.parkingLotAction"))
        elif action == "add1" :
            parkingLot = getParkingLot(id)
            createParkingSpot(parkingLot)
            parkingLot.noOfParkingSpots += 1
            db.session.add(parkingLot)
            db.session.commit()
            return redirect(url_for("admin.dashboard"))
        elif action == "delete1" :
            parkingLot = getParkingLot(id)
            if len(db.session.execute(db.select(ParkingSpot).filter_by(parkingLotId = id, status = False)).scalars().all()) > 0 :
                deleteParkingSpot(parkingLot)
                parkingLot.noOfParkingSpots -= 1
                db.session.add(parkingLot)
                db.session.commit()
            return redirect(url_for("admin.dashboard"))
    return render_template("admin/adminDashboard.html", parkingLots = viewParkingLots())

@adminbp.route("/dashboard/searchResults", methods = ["POST"])
def searchResults() :
    type = request.form["type"]
    searchValue = request.form["searchValue"].lower()
    newRecs = []
    model = globals()[type]
    for i in db.session.execute(db.select(model)).scalars().all() :
        j = i.__str__()
        if searchValue in j :
            newRecs.append(j.split(" ")[0])
    if type == "ReservedParkingSpot" :
        for i in db.session.execute(db.select(User)).scalars().all() :
            j = i.__str__()
            if searchValue in j :
                print(j[0])
                for k in i.reservedParkingSpots :
                    newRecs.append(k.__str__().split(" ")[0])    
    searchResult = db.session.execute(db.select(model).filter(model.id.in_(newRecs))).scalars().all()
    if type == "ParkingLot" :
        return render_template("admin/adminDashboard.html", parkingLots = searchResult)
    elif type == "User" :
        return render_template("admin/displayUsers.html", users = searchResult)
    elif type == "ReservedParkingSpot" :
        return render_template("admin/reservationHistory.html", reservedParkingSpots = searchResult)
    return 

@adminbp.route("/dashboard/action", methods = ["GET", "POST"])
def parkingLotAction() :
    id = session.get("id")
    action = session.get("action")
    if id is not None :
        parkingLot = getParkingLot(id)
    else :
        address = Address(streetName = "", locality = "", subLocality = "", city = "", state = "", pinCode = "")
        parkingLot = ParkingLot(landmark = "", noOfParkingSpots = 0, pricePerHr = 0)
        parkingLot.address = address
    noOfOccupiedParkingSpots = len((db.session.execute(db.select(ParkingSpot).filter_by(status = True, parkingLotId = id)).scalars().all()))
    noOfVacantParkingSpots = len((db.session.execute(db.select(ParkingSpot).filter_by(status = False, parkingLotId = id)).scalars().all()))
    if request.method == "GET" :
        return render_template("admin/parkingLotAction.html", action = action, pl = parkingLot, noops = noOfOccupiedParkingSpots, novps = noOfVacantParkingSpots)
    elif request.method == "POST" :
        oldNoOfParkingSpots = parkingLot.noOfParkingSpots
        newNoOfParkingSpots = int(request.form["nps"])
        parkingLot.address.streetName = request.form["n"]
        parkingLot.address.locality = request.form["l"]
        parkingLot.address.subLocality = request.form["sl"]
        parkingLot.address.city = request.form["c"]
        parkingLot.address.state = request.form["s"]
        parkingLot.address.pinCode = request.form["p"]
        parkingLot.landmark = request.form["la"]
        #parkingLot.noOfParkingSpots = request.form["nps"]  #no need to update as -= 1 is dont in deleteParkingSpot function which is called by updateParkingLot function
        parkingLot.pricePerHr = int(request.form["pph"])
        if action == "create" :
            createParkingLot(parkingLot, newNoOfParkingSpots) 
        elif action == "edit" : 
            updateParkingLot(parkingLot, oldNoOfParkingSpots, newNoOfParkingSpots)
        session.pop("action")
        session.pop("id")
        return redirect(url_for("admin.dashboard"))

def getParkingLot(id) : 
    return db.session.execute(db.select(ParkingLot).filter_by(id = id)).scalars().first()

def createParkingLot(parkingLot, nps) : 
    try :
        db.session.add(parkingLot)
        db.session.flush()
        for i in range(nps) :
            createParkingSpot(parkingLot)
        parkingLot.noOfParkingSpots = nps 
        db.session.commit()
    except IntegrityError as e :
        db.session.rollback()

def viewParkingLots() : 
    return db.session.execute(db.select(ParkingLot)).scalars().all()

def updateParkingLot(parkingLot, onps, nps) :
    try :
        db.session.add(parkingLot)
        db.session.flush()
        diff = onps - nps
        if(diff < 0) : #if parking spots have to be added
            for i in range(abs(diff)) :
                createParkingSpot(parkingLot)
            parkingLot.noOfParkingSpots = nps
        elif(diff > 0) : #if parking spots have to be removed
            for i in range(diff) :
                if(deleteParkingSpot(parkingLot) == None) :
                    i -= 1
                    break
            parkingLot.noOfParkingSpots = onps - i - 1
        db.session.commit()
    except IntegrityError as e :
        db.session.rollback()

def deleteParkingLot(parkingLot) : 
    address = parkingLot.address
    parkingSpots = parkingLot.parkingSpots
    db.session.delete(address)
    db.session.delete(parkingLot)
    for i in range(len(parkingSpots)) :
        if parkingSpots[i].status == True :
            db.session.rollback()
            break
        db.session.delete(parkingSpots[i])
    db.session.commit()
    db.session.expire_all()

def viewParkingSpots(parkingLot) : 
    return parkingLot.parkingSpots

def createParkingSpot(parkingLot) : 
    id = parkingLot.id 
    parkingSpot = ParkingSpot(status = False, parkingLotId = id)
    db.session.add(parkingSpot)
    #parkingLot.noOfParkingSpots += 1
    #db.session.add(parkingLot)
    #db.session.commit()

def deleteParkingSpot(parkingLot) : 
    parkingSpots = parkingLot.parkingSpots
    for parkingSpot in parkingSpots :
        if parkingSpot.status == False :
            db.session.delete(parkingSpot)
            #parkingLot.noOfParkingSpots -= 1
            #db.session.add(parkingLot)
            db.session.commit()
            return True
    return None

def viewUsers() : 
    return db.session.execute(db.select(User)).scalars().all()

def viewHistory() :
    return db.session.execute(db.select(ReservedParkingSpot).order_by(nulls_first(desc(ReservedParkingSpot.parkingTimestamp)))).scalars().all()

@adminbp.route("/dashboard/users", methods = ["GET"])
def users() :
    if request.method == "GET" :
        users = db.session.execute(db.select(User)).scalars().all()
        return render_template("admin/displayUsers.html", users = users)

@adminbp.route("/dashboard/history", methods = ["GET"])
def history() :
    if request.method == "GET" :
        return render_template("admin/reservationHistory.html", reservedParkingSpots = viewHistory())

def viewAllReservedParkingSpots() :
    return db.session.execute(db.select(ReservedParkingSpot).order_by(nulls_first(desc(ReservedParkingSpot.parkingTimestamp)))).scalars().all()

def getParkingLotsUsedByUsersLiUsingReservedParkingSpots() :
    return [i.parkingSpot.parkingLot.id for i in db.session.execute(db.select(User)).scalars().first().reservedParkingSpots if i.parkingSpot is not None]

def frequentlyUsedParkingLot() :
    parkingLotIds = getParkingLotsUsedByUsersLiUsingReservedParkingSpots()
    return getParkingLot(max(set(parkingLotIds), key = parkingLotIds.count))

def sumOfTotalCosts() :
    reservedParkingSpots = viewAllReservedParkingSpots()
    sum = 0
    for i in reservedParkingSpots :
        if i.totalCost is not None:
            sum += i.totalCost 
    return sum

def plotPiePlotOfParkingLotsUsed() :
    plt.figure()
    li = getParkingLotsUsedByUsersLiUsingReservedParkingSpots()
    labels = sorted(set(li))
    countLi = [li.count(i) for i in labels]
    plt.pie(countLi, labels = [("Lot#" + str(i)) for i in labels], rotatelabels = True, labeldistance = 0.5)
    plt.savefig("static/images/plot1.png")

def plotLinePlotOfTotalCosts() :
    plt.figure()
    costLi = [i.totalCost for i in viewAllReservedParkingSpots()]
    xAxis = [i for i in range(0, len(costLi))]
    plt.plot(xAxis, costLi)
    plt.xlabel("Parkings")
    plt.ylabel("Total Costs")
    plt.grid(True)
    plt.savefig("static/images/plot2.png")

def noOfOccupiedParkingSpotsRN() :
    return len(db.session.execute(db.select(ParkingSpot).filter_by(status = True)).scalars().all())

def totalNoOfType(type) :
    model = globals()[type]
    return len(db.session.execute(db.select(model)).scalars().all())

@adminbp.route("/dashboard/summary", methods = ["GET"])
def summary() :
    if request.method == "GET" :
        plotPiePlotOfParkingLotsUsed()
        plotLinePlotOfTotalCosts()
        return render_template("admin/summary.html", parkingLot = frequentlyUsedParkingLot(), cost = sumOfTotalCosts(), noOfParkings = totalNoOfType("ReservedParkingSpot"), noOfOccupiedParkingSpotsRN = noOfOccupiedParkingSpotsRN(), noOfParkingLots = totalNoOfType("ParkingLot"), noOfParkingSpots = totalNoOfType("ParkingSpot"))
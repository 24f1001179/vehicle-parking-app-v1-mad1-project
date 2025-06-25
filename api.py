from flask import jsonify
from flask_restful import Resource
from dbInit import db
from models.userInfo import User, Address
from models.parkingInfo import ParkingLot

class UserApi(Resource) :
    def get(self, firstName) :
        user = db.session.execute(db.select(User).filter_by(firstName = firstName)).scalars().first()
        if user:
            return {
                "id" : user.id,
                "firstName" : user.firstName, 
                "lastName" : user.lastName, 
                "age" : user.age, 
                "email" : user.email,
            }, 200
        else :
            return "User Not Found", 404
    
class ParkingLotApi(Resource) :
    def get(self, city) :
        city = city.title()
        parkingLots = db.session.execute(db.select(ParkingLot).join(Address).filter(Address.city == city)).scalars().all()
        if len(parkingLots) > 0:
            li = [{"id" : i.id, "landmark" : i.landmark, "noOfParkingSpots" : i.noOfParkingSpots, "pricePerHr" : i.pricePerHr} for i in parkingLots]
            return li, 200
        else :
            return "No Parking Lots In This City", 404

    

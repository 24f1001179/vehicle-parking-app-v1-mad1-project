from dbInit import db 

class ParkingLot(db.Model) :
    __tablename__ = "parkinglot"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    landmark = db.Column(db.String)
    noOfParkingSpots = db.Column(db.Integer)
    pricePerHr = db.Column(db.Integer)
    addressId = db.Column(db.Integer, db.ForeignKey("address.id"))
    address = db.relationship("Address", uselist = False, backref = "parkingLot") #parking lot and address is 1 - 1
    parkingSpots = db.relationship("ParkingSpot", backref = "parkingLot") #parking lot and parking spot is 1 - M
    def __str__(self) :
        return "{} {} {} {} {}".format(self.id, self.landmark.lower(), self.noOfParkingSpots, self.pricePerHr, self.address.__str__())

class ParkingSpot(db.Model) :
    __tablename__ = "parkingspot"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    parkingLotId = db.Column(db.Integer, db.ForeignKey("parkinglot.id"))
    status = db.Column(db.Boolean)
    reservedParkingSpots = db.relationship("ReservedParkingSpot", backref = "parkingSpot") #parking spot and reserved parking spot is 1 - M


class ReservedParkingSpot(db.Model) :
    __tablename__ = "reservedparkingspot"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    parkingSpotId = db.Column(db.Integer, db.ForeignKey("parkingspot.id"))
    userId = db.Column(db.Integer, db.ForeignKey("user.id"))
    parkingTimestamp = db.Column(db.DateTime)
    leavingTimestamp = db.Column(db.DateTime)
    totalCost = db.Column(db.Integer)
    vehicleNumber = db.Column(db.String)
    def __str__(self) :
        return "{} {} {} {} {}".format(self.id, self.parkingTimestamp, self.leavingTimestamp, self.totalCost, self.vehicleNumber)
    
'''
ParkingLot
Parking Lot and Address is 1 – 1
Parking Lot and Parking Spot is 1 - M
•	id (Primary Key) (Auto Increment) (Integer)
•	landmark (String)
•	noOfParkingSpots (Integer)
•	pricePerHr (Integer)
•	addressId (Foreign Key) (Integer)
ParkingSpot
Parking Spot and Reserved Parking Spot is 1 - M
•	id (Primary Key) (Auto Increment) (Integer)
•	parkingLotId (Foreign Key) (Integer)
•	status (Boolean)
ReservedParkingSpot
•	id (Primary Key) (Auto Increment) (Integer)
•	parkingSpotId (Foreign Key) (Integer)
•	userId (Foreign Key) (Integer)
•	parkingTimestamp (DateTime)
•	leavingTimestamp (DateTime)
•	totalCost (Integer)
•	vehicleNumber (String)
'''
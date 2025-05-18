from dbInit import db

class User(db.Model) :
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    firstName = db.Column(db.String)
    lastName = db.Column(db.String)
    age = db.Column(db.Integer)
    addressId = db.Column(db.Integer, db.ForeignKey("address.id"))
    email = db.Column(db.String, unique = True)
    password = db.Column(db.String, unique = True)
    address = db.relationship("Address", backref = "users") #user and address is M - 1
    reservedParkingSpots = db.relationship("ReservedParkingSpot", backref = "user") #user and reserved parking spot is 1 - M
    def __str__(self) :
        return "{} {} {} {} {} {}".format(self.id, self.firstName.lower(), self.lastName.lower(), self.age, self.email.lower(), self.address.__str__())

class Address(db.Model) :
    __tablename__ = "address"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    streetName = db.Column(db.String)
    locality = db.Column(db.String)
    subLocality = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    pinCode = db.Column(db.String)
    def __str__(self) :
        return "{} {} {} {} {} {} {}".format(self.id, self.streetName.lower(), self.locality.lower(), self.subLocality.lower(), self.city.lower(), self.state.lower(), self.pinCode)

class Admin(db.Model) :
    __tablename__= "admin"
    id = db.Column(db.Integer, primary_key = True, server_default = "1")
    email = db.Column(db.String)
    password = db.Column(db.String)
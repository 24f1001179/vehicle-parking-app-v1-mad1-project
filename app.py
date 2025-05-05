from flask import Flask
from dbInit import db

app = Flask(__name__, template_folder = "templates")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db.init_app(app)

from models.userInfo import User, Address, Admin
from models.parkingInfo import ParkingLot, ParkingSpot, ReservedParkingSpot

if __name__ == "__main__" :
    with app.app_context() :
        db.create_all()
        if not Admin.query.first() :
            admin = Admin(email = "jskarthik45@gmail.com", password = "abcd1234")
            db.session.add(admin)
            db.session.commit()
    app.run(debug = True)
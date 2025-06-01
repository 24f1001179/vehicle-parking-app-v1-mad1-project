from flask import Flask
from dbInit import db

app = Flask(__name__, template_folder = "templates")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SECRET_KEY"] = "7b802e16987d92cb41311357a106ff83a65b79e60d0942c91a2b9950477acdc8" #secret key for sessions

db.init_app(app)

from models.userInfo import User, Address, Admin
from models.parkingInfo import ParkingLot, ParkingSpot, ReservedParkingSpot

from controllers.bp import userbp, adminbp, generalbp
import controllers.login

app.register_blueprint(userbp, url_prefix = "/user")
app.register_blueprint(adminbp, url_prefix = "/admin")
app.register_blueprint(generalbp, url_prefix = "/")

if __name__ == "__main__" :
    with app.app_context() :
        db.create_all()
        if not Admin.query.first() :
            admin = Admin(email = "24f1001179@ds.study.iitm.ac.in", password = "password")
            db.session.add(admin)
            db.session.commit()
    app.run(host = "0.0.0.0", debug = True)
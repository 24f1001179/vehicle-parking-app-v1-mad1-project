from flask import Flask, request, session
from flask import render_template, url_for, redirect
from controllers.bp import userbp 
from dbInit import db
from models.userInfo import User

@userbp.before_request
def restrict() :
    if session.get("type") != "user" :
        return redirect(url_for("general.signIn"))

@userbp.route("/dashboard", methods = ["GET"])
def dashboard() :
    return render_template("userDashboard.html")
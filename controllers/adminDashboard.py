from flask import Flask, request, session
from flask import render_template, url_for, redirect
from controllers.bp import adminbp 

@adminbp.before_request
def restrict() :
    if session.get("type") != "admin" :
        return redirect(url_for("general.signIn"))

@adminbp.route("/dashboard", methods = ["GET"])
def dashboard() :
    return render_template("adminDashboard.html")
from flask import Flask, request
from flask import render_template, url_for, redirect
from controllers.bp import adminbp 

@adminbp.route("/dashboard", methods = ["GET"])
def dashboard() :
    return render_template("adminDashboard.html")
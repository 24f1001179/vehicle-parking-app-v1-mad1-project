from flask import Flask, request
from flask import render_template, url_for, redirect
from controllers.bp import userbp 

@userbp.route("/dashboard", methods = ["GET"])
def dashboard() :
    return render_template("userDashboard.html")
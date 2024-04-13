from flask import Flask, render_template, request
from pymysql import connections
import os
import random
import argparse
import boto3


app = Flask(__name__)

DBHOST = os.environ.get("DBHOST") or "localhost"
DBUSER = os.environ.get("DBUSER") or "root"
DBPWD = os.environ.get("DBPWD") or "pw"
DATABASE = os.environ.get("DATABASE") or "employees"
DBPORT = int(os.environ.get("DBPORT"))

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN = os.environ.get("AWS_SESSION_TOKEN")

HEADER = (
    os.environ.get("HEADER")
    or "Trupal Chaudhary | Vaishnavi Barot | Keerthigan Lalitharan"
)

bucket_name = os.environ.get("BUCKETNAME") or "bucket-k8s-final-project"
key = os.environ.get("KEY") or "bg1.jpg"

# Create a connection to the MySQL database
db_conn = connections.Connection(
    host=DBHOST, port=DBPORT, user=DBUSER, password=DBPWD, db=DATABASE
)
output = {}
table = "employee"

# Fetching images

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
)
image_location = "static/images"
if not os.path.exists(image_location):
    os.makedirs(image_location)

local_imgpath = os.path.join(image_location, "bg.jpg")
s3.download_file(bucket_name, key, local_imgpath)

# Logging background image download location
print(f"Downloaded the image from s3://{bucket_name}/{key}")


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("addemp.html", HEADER=HEADER)


@app.route("/about", methods=["GET", "POST"])
def about():
    return render_template("about.html", HEADER=HEADER)


@app.route("/addemp", methods=["POST"])
def AddEmp():
    emp_id = request.form["emp_id"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    primary_skill = request.form["primary_skill"]
    location = request.form["location"]

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:

        cursor.execute(
            insert_sql, (emp_id, first_name, last_name, primary_skill, location)
        )
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name

    finally:
        cursor.close()

    print("all modification done...")
    return render_template("addempoutput.html", name=emp_name, HEADER=HEADER)


@app.route("/getemp", methods=["GET", "POST"])
def GetEmp():
    return render_template("getemp.html", HEADER=HEADER)


@app.route("/fetchdata", methods=["GET", "POST"])
def FetchData():
    emp_id = request.form["emp_id"]

    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location from employee where emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id))
        result = cursor.fetchone()

        # Add No Employee found form
        output["emp_id"] = result[0]
        output["first_name"] = result[1]
        output["last_name"] = result[2]
        output["primary_skills"] = result[3]
        output["location"] = result[4]

    except Exception as e:
        print(e)

    finally:
        cursor.close()

    return render_template(
        "getempoutput.html",
        id=output["emp_id"],
        fname=output["first_name"],
        lname=output["last_name"],
        interest=output["primary_skills"],
        location=output["location"],
        HEADER=HEADER,
    )


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=81, debug=True)

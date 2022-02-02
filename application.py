# Required imports
from requests import get
import json
import os
import re
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from google.oauth2 import id_token
from google.auth.transport import requests
import base64
import datetime
from mailjet_rest import Client

# Import helper functions we created from helpers.py
from helpers import login_required, get_next_contact, get_contacts, get_relationship_type, message_maker, get_message_id, make_html_message, check_alerts

# Expressing the client id from gooale API
CLIENT_ID = "1002099622195-c25lvju4t2milljjicj045aeqi0m96np.apps.googleusercontent.com"

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///closefromafar.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Sign in Function
@app.route("/signin", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":


        # Recieveing the token and the full name from the signin.html file
        data = request.values
        helper = data["idtoken"].split()
        token = helper[0]
        user_name = helper[1]
        for i in range(len(helper)):
            if i > 1:
                user_name += " " + helper[i]

        # Verify the integrity of the ID token - https://developers.google.com/identity/sign-in/web/backend-auth
        try:
            # Specify the CLIENT_ID of the app that accesses the backend:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

            # ID token is valid. Get the user's Google Account ID from the decoded token.
            user_id = idinfo['sub']
            user_email = idinfo['email']
        except ValueError:
            # Invalid token
            pass

        # Query database to see if the user already exists
        rows = db.execute("SELECT * FROM users_google WHERE id = ?", user_id)

        # Add username to DB (users_google) if it is not exist
        if len(rows) != 1:
            db.execute("INSERT INTO users_google (id, email, name) VALUES (?, ?, ?)", user_id, user_email, user_name)

        # Remember which user has logged in
        session['user_id'] = user_id
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("signin.html")


# Log out function
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# Home Page function
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show The contacts"""
    if request.method == "GET":
        # Get the contacts of this user from DB
        contacts = get_contacts(session['user_id'])
        # Access weather.gov API for sever weather alerts
        alerts = check_alerts()

        # If the user has contacts
        if len(contacts) > 0:

            return render_template("index.html", contacts = contacts, alerts = alerts)
        else:
            return  render_template("index.html")

    # if the method is POST
    else:
        return render_template("index.html")


# Contacts Function
@app.route("/contacts", methods=["GET", "POST"])
@login_required
def contacts():

    # Get updated contact list
    contact_list = get_contacts(session['user_id'])

    if request.method == "GET":
        # Return page with updated contact list
        return render_template("contacts.html", contacts = contact_list)

    else:
        # Ensure that everything was submitted correctly
        if not request.form.get("first") or not request.form.get("last") or not request.form.get("email"):
            return render_template("contacts.html", text = "Please provide a valid email and full name of the contact", contacts = contact_list)

        # If everything submitted OK
        else:
            # Store relevant contact information in variables
            honorifics = request.form.get("honorifics")
            first = request.form.get("first")
            last = request.form.get("last")
            email = request.form.get("email")
            birthday = request.form.get("birthday")
            country = request.form.get("country")
            frequency = request.form.get("frequency")
            relationship = request.form.get("relationship")
            last_contact = request.form.get("last_contact")
            if request.form.get("state") != None:
                state = request.form.get("state")
            sign_off = request.form.get("sign_off")

            # check when was contacted last.
            # If not - start the clock from inserted time.
            if last_contact == '':
                last_contact = datetime.datetime.now().date()
                date_time_obj = datetime.datetime.now()
            else:
                date_time_obj = datetime.datetime.strptime(last_contact, '%Y-%m-%d')

            # Get initial next contact
            next_contact = get_next_contact(date_time_obj, frequency, birthday)

            # Convert Next Contact from datetime object to regular date
            next_contact = next_contact.date()
            owner = session["user_id"]

            # Insert the contact into the DB
            db.execute("INSERT INTO contacts (honorifics, first, last, email, birthday, country, frequency, relationship, last_contact, next_contact, owner, state, sign_off) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        honorifics, first, last, email, birthday, country, frequency, relationship, last_contact, next_contact, owner, state, sign_off)

            contact_id = db.execute("SELECT id FROM contacts WHERE owner = ?", owner)[-1]["id"]

            message_id = get_message_id(owner, contact_id)

        # Get updated contact list through the get_contacts function
        contact_list = get_contacts(session['user_id'])
        # Refresh the page with the updated contacts
        return render_template("contacts.html", contacts = contact_list)


# Calendar Function
@app.route("/calendar", methods=["GET"])
@login_required
def calendar():
    # Recieve the contacts list for the user
    contacts = get_contacts(session['user_id'])
    # Send everything to calendar.html
    if len(contacts) > 0:
        return render_template("calendar.html", contacts = contacts)
    else:
        return render_template("calendar.html")


# Delete a contact from the DB
@app.route("/delete/", methods=['POST'])
@login_required
def delete_contact():
    # Get contact per delete button
    contact = request.form.get("tag","")

    # Remove contact from database
    db.execute("DELETE FROM contacts WHERE owner = ? AND id = ?", session["user_id"], contact)

    # Get updated contact list
    contact_list = get_contacts(session["user_id"])

    # Refresh contact page with updated contacts
    return render_template("contacts.html", contacts = contact_list)


# Generate a new message for the contact
@app.route("/newMessage/", methods=['POST'])
@login_required
def new_message():
    # Get contact per new message button
    contact_id = request.form.get("tag","")

    # Generate new message
    message_id = get_message_id(session["user_id"], contact_id)

    # Refresh page with updated message id for contacts
    return render_template("index.html", contacts = get_contacts(session["user_id"]), alerts = check_alerts())


# Function that updates the DB when you talked with a contact
@app.route("/update/", methods=['POST'])
@login_required
def update_contact():
    # Get contact id from the talked button in home page
    contact_id = request.form.get("tag","")

    # last_contact equals today's date
    last_contact = datetime.datetime.now()

    # Find the frequency and birthday of that contact - change into 1 execute instead of 2!!!
    data = db.execute("SELECT frequency from contacts WHERE owner = ? AND id = ?", session["user_id"], contact_id)
    frequency = data[0]['frequency']
    data1 = db.execute("SELECT birthday from contacts WHERE owner = ? AND id = ?", session["user_id"], contact_id)
    birthday = data1[0]['birthday']
    # get next contact date
    next_contact = get_next_contact(last_contact, frequency, birthday)

    # Update information in the database
    last_contact = last_contact.date()
    next_contact = next_contact.date()
    db.execute("UPDATE contacts SET last_contact = ?, next_contact = ? WHERE owner = ? AND id = ?", last_contact, next_contact, session["user_id"], contact_id)

    # Get updated contact list
    contact_list = get_contacts(session["user_id"])
    # Refresh home page with updated contacts
    return render_template("index.html", contacts = contact_list, alerts = check_alerts())


# Send new message
@app.route("/sendMail/", methods=['POST'])
@login_required
def send_mail():

    # Get contact per new message button
    contact_id = request.form.get("tag","")

    # Get contact information from DB
    contact = db.execute("SELECT * FROM contacts WHERE id = ? AND owner = ?", contact_id, session['user_id'])[0]

    # Creating the message content to send
    message = message_maker(session['user_id'], contact['id'], contact['message_id'])

    # Creating the html message (email content)
    html_message = make_html_message(message)

    # Get user name
    user_name = db.execute("SELECT * FROM users_google where id = ?", session['user_id'])[0]['name']

    # Setting up API
    api_key = 'd222bcea8959302fa0bcd473898dd8b2'
    api_secret = '814a7549fd7c892e5e2ec1317f9ff801'
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')

    # Data for email
    data = {
      'Messages': [
        {
          "From": {
            "Email": "fromafarclose@gmail.com",
            "Name": user_name
          },
          "To": [
            {
              "Email": contact['email'],
              "Name": contact['first'] + " " + contact['last']
            }
          ],
          "Subject": "Hey",
          "TextPart": message,
          "HTMLPart": html_message,
          "CustomID": "closeFromAfarMessages"
        }
      ]
    }
    result = mailjet.send.create(data=data)
    print(result.status_code)
    print(result.json())

    # Update contact
    update_contact()
    # Generate new message
    message_id = get_message_id(session["user_id"], contact_id)

    # Refresh page with updated message id for contacts
    return redirect("/")
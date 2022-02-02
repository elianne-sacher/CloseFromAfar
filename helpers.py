# Required imports
from requests import get
import json
import os
import requests
import urllib.parse
import datetime
from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps
import random
from collections import Counter
import string


# Global Variables for Contact Frequency
DAILY = 1
WEEKLY = 7
MONTHLY = 30
QUARTERLY = 120
ANNUALLY = 365


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///closefromafar.db")


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect("/signin")
        return f(*args, **kwargs)
    return decorated_function


# Function that calculates the next contact date
def get_next_contact(last_contact, frequency, birthday):
    # Compute initial next contact
    if frequency == 'Daily':
        next_contact = last_contact + datetime.timedelta(days=DAILY)
    elif frequency == 'Weekly':
        next_contact = last_contact + datetime.timedelta(days=WEEKLY)
    elif frequency == 'Monthly':
        next_contact = last_contact + datetime.timedelta(days=MONTHLY)
    elif frequency == 'Quarterly':
        next_contact = last_contact + datetime.timedelta(days=QUARTERLY)
    # If only on birthday is selected contact set next contact to the birthday
    elif frequency == 'Only on Birthday' and birthday != '':
        # Convert birthday to datetime object for comparison
        birthday_date = datetime.datetime.strptime(birthday, '%Y-%m-%d')
        # Update birthday year to current year
        birthday_date = birthday_date.replace(year = datetime.datetime.now().year)
        # Check if birthday has passed yet
        if birthday_date > datetime.datetime.now():
            # If birthday has not passed set next contact to birthday
            next_contact = birthday_date
            return next_contact
        else:
            # If birthday has passed update birthday date to next year and set next contact to birthday
            birthday_date = birthday_date.replace(year = datetime.datetime.now().year + 1)
            next_contact = birthday_date
            return next_contact
    else:
        # Last option is contact on annual basis
        next_contact = last_contact + datetime.timedelta(days=ANNUALLY)

    # Check if birthday is yet to pass and comes before next contact
    if birthday != '':
        birthday_date = datetime.datetime.strptime(birthday, '%Y-%m-%d')
        birthday_date = birthday_date.replace(year = datetime.datetime.now().year)

        # Conditions for setting a birthday before next contact
        # Make sure the birthday didn't pass already and that it is earlier than last contact
        if birthday_date > datetime.datetime.now() and birthday_date < next_contact:
            next_contact = birthday_date
        # Else if next year's birthday is earlier than next contact set it to be next contact
        else:
            birthday_date = birthday_date.replace(year = datetime.datetime.now().year + 1)
            if birthday_date < next_contact:
                next_contact = birthday_date
    return next_contact


# Function to get sorted list (by next contact) of user's contacts (reminder to move this function to helpers.py and import it)
def get_contacts(user):
    # Get user's contacts
    contacts = db.execute("SELECT * FROM contacts WHERE owner =  ? ORDER BY next_contact ASC", user)

    # For every contact in the contacts list
    for contact in contacts:

        # Generate a new message
        contact["message"] = message_maker(user, contact["id"], contact["message_id"])

        # Make sure that next contact is equal to birthdate if it is earlier
        if contact["birthday"] != "":
            birthday_date = datetime.datetime.strptime(contact["birthday"], '%Y-%m-%d')
            birthday_date = birthday_date.replace(year = datetime.datetime.now().year)

            if birthday_date.date() < datetime.datetime.now().date():
                birthday_date = birthday_date.replace(year = datetime.datetime.now().year + 1)
                contact["birthday"] = birthday_date.strftime('%Y-%m-%d')

    return contacts


# Check relationship type
def get_relationship_type(contact_info):
    # check if family
    if contact_info['relationship'] == 'Nuclear Famiy' or contact_info['relationship'] == 'Extended Family':
        return 'family'
    # check if friend
    elif contact_info['relationship'] == 'Friend-like-Family' or contact_info['relationship'] == 'Friend':
        return 'friend'
    # check if partner
    elif 'Significant Other' == contact_info['relationship']:
        return 'partner'
    # check if coworker
    elif 'Coworker' == contact_info['relationship']:
        return 'coworker'
    # if not anything else than just other
    return 'all'


# creates the messages to send a contact (reminder to move this function to helpers.py and import it)
def message_maker(user_id, contact_id, message_id):

    sign_offs = {"friend": ["Sincerely", "Yours", "Miss you tons", "Miss ya", "Love"],
                 "family": ["Sincerely", "Yours", "Miss you tons", "Miss ya", "Love", "Love ya", "Love you so much"],
                 "partner": ["Sincerely", "Yours", "Miss you tons", "Miss ya", "Love", "Love ya", "Love you", "Love you so much"],
                 "coworker": ["Kind regards", "Sincerely"],
                 "all": ["Kind regards", "Sincerely"]}
    # gets contact information
    contact_info = db.execute("SELECT * FROM contacts WHERE owner =  ? AND id = ?", user_id, contact_id)[0]

    # get the message templet
    message_templet = db.execute("SELECT * FROM messages WHERE id = ?", message_id)[0]['message']
    # update log
    db.execute("INSERT INTO message_log (user_id, contact_id, message_id) VALUES (?, ?, ?)", user_id, contact_id, message_id)

    # replaces place holdes
    message_templet = message_templet.replace("[honorifics]", contact_info['honorifics'])
    message_templet = message_templet.replace("[contact_first_name]", contact_info['first'])
    message_templet = message_templet.replace("[contact_last_name]", contact_info['last'])
    message_templet = message_templet.replace("[location]", contact_info['country'])

    # replace sign off place holder
    # if there is no tailored sign off generates one
    if contact_info['sign_off'] == '' or contact_info['sign_off'] == None:
        relationship = get_relationship_type(contact_info)
        user_name = db.execute("SELECT name FROM users_google WHERE id = ?", user_id)[0]['name']
        sign_off = random.choice(sign_offs[relationship]) + ', ' + user_name
        message_templet = message_templet.replace("[sign_off]", sign_off)
    # if there is a tailored sign off input it instead
    else:
        message_templet = message_templet.replace("[sign_off]", contact_info['sign_off'])

    return message_templet


# creates the messages to send a contact (reminder to move this function to helpers.py and import it)
def get_message_id(user_id, contact_id):

    # gets contact information
    contact_info = db.execute("SELECT * FROM contacts WHERE owner =  ? AND id = ?", user_id, contact_id)[0]

    relationship = get_relationship_type(contact_info)

    # checks if birthday for birthday messages and if so selects these messages types
    if contact_info["birthday"] != '' and datetime.datetime.now().date() == datetime.datetime.strptime(contact_info["birthday"], '%Y-%m-%d').date():
        messages = db.execute("SELECT * FROM messages WHERE type = 'birthday' AND (relationship = ? OR relationship = 'all')", relationship)
        convos = db.execute("SELECT * FROM message_log JOIN messages ON message_log.message_id = messages.id WHERE user_id =  ? AND contact_id = ? AND type = 'birthday'", user_id, contact_id)
    # if not selects the general messages
    else:
        messages = db.execute("SELECT * FROM messages WHERE type = 'general' AND (relationship = ? OR relationship = 'all')", relationship)
        convos = db.execute("SELECT * FROM message_log JOIN messages ON message_log.message_id = messages.id WHERE user_id =  ? AND contact_id = ? AND type = 'general'", user_id, contact_id)

    # counts how many times a message with a unique message_id has been used
    messages_used = dict(Counter([d['message_id'] for d in convos]))

    # Checks for unused messages
    is_used_all_messages = True
    for message in messages:
        if message['id'] not in messages_used.keys():
            message_id = message['id']
            is_used_all_messages = False
            break

    # if all were used, selects the one that was used the least
    if is_used_all_messages:
        message_id = min(messages_used, key=messages_used.get)

    # Update contacts
    db.execute("UPDATE contacts SET message_id = ? WHERE owner = ? AND id = ?", message_id, session['user_id'], contact_id)
    return message_id


def make_html_message(message):

    html_message = '<p>'

    for c in message:
        html_message += c
        # checking whether the char is punctuation.
        if c in string.punctuation:
            html_message += '</p><p>'
    html_message += '</p>'

    return html_message


def check_alerts():
    # Get list of states
    states = db.execute("SELECT id,state FROM contacts WHERE owner =  ? AND state != 'None'", session["user_id"])
    state_list = list()
    # Initialize set of alerts for the relevant states
    final_alerts = set()
    # Initialize potential search query addition
    search_query = ''
    # If there are states in the contacts
    if len(states) != 0:
        # Fill the list of states and build the search query
        for i in range(0,len(states)):
            if states[i]['state'] != "NA":
                state_list.append(states[i]['state'])
                search_query += states[i]['state']
                # Add commas until the last state
                if i < len(states) - 1:
                    search_query += ','
        # Create and retrieve weather API query
        response = get("https://api.weather.gov/alerts?active=true&status=actual&area=%s&severity=extreme" % search_query)
        # Convert query to json
        json_data = json.loads(response.text)
        # If there are current weather alerts for the states given fill the set of alerts
        if json_data.get('features'):
            for i in state_list:
                for j in range(0, len(json_data['features'])):
                    if i in json_data['features'][j]['properties']['geocode']['UGC'][0]:
                        final_alerts.add(i)
    # Return the set of alerts
    return final_alerts
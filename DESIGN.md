# Design - Close From Afar

To implement our web application, we used the knowledge of Python, SQLite, JavaScript, Jinja, HTML5, and CSS from lectures and the web.
Our server is implemented with Python, Flask, and SQLite databases.
The client-side is implemented by using HTML and CSS for design, JavaScript to have multiple functions, and jinja to receive data from the server.
We use Flask to interact with the client-side. We used @login_required in all server functions, other than sign in and sign out, to prevent
users from entering specific pages in our website (with GET through the URL) without signing in first.

# Technical Overview
Using the Flask framework our project folder is comprised of a static folder (holding all CSS and js files), a templates folder (holding all HTML files), application.py
which runs the main functions on the server-side, helpers.py which holds helper functions for application.py, relevant JSON credential files for Google's API, closefromafar.db
(our SQLlite database), design.MD (detailing the thoughts behind the app's design), and README.md (a user manual).

# Sign in

We implemented a sign in with Google accounts with the help of Google API. By doing so, users do not need to register for our website,
to remember any new password, or to worry that their password is not secured in the database. We use a users_google table in our database that stores
the user's id, user's email, and user's full name - all are received from Google after signing in. Every time a user signs in we check if their user id is
in our database, and if not, we store it.

We decided to use Google sign-in because we believe it makes for a more secure and industry-grade tool by routing all authentication through Google's API.
Additionally, we can build upon the current application's features and add more Google API services to the web app which will synergize with Google's login.

The user's session is saved to enable them to access the web site's other pages and they will only be logged out when the user decides to sign out.

# General layout
All pages within the app have a navbar at the top which offers the user an easy way to navigate between the home page, calendar, and contact manager as well as
return to the sign-in page to log out.

The navbar adjusts according to the device that is accessing the website with a more concise version displayed for mobile users.

In order to give the user a feeling that they are using a real web app and not some 90s looking webpage we present all the data on the home page and contact manager
in a window that (using shadows) pops a bit out of the page. All of the layout and website design was built using HTML and CSS. The calendar was built using a
free library called FullCalendarIO which also allows for specialized themes and CSS adjustments.

# Data storage
A key part of the app's success relies on the effective storage of users, contacts, and messages. We used SQLlite for all our data storage needs.

The closefromafar.db database includes four tables: users google, contacts, messages, and message_log. Below you can find a brief overview of the structure of each table:

Users google --> stores three fields ID (given by Google's authentication service), email (the one they are using), and name.

Contacts --> stores 14 fields per contact. The owner field is used to identify the user to whom this contact is connected (they "own" the relationship).
The other fields are used for message generation as well as accessing weather.gov's API to track for extreme weather alerts in the contact's location.

Messages --> stores 4 fields: ID (Primary Key), relationship (the type of relationship that this message would apply to), type (the type of message: birthday/general), and message (the text of the message templet).

Message log --> stores a log of the messages that were seen by the user and the passed (both rejected and used ones).
The table has 5 fields: ID (Primary Key), user_id (id of the user that viewed the message), contact_id (the contact the user view this specific message for), message_id (id of message templet), and timestamp (of when it was inputted into the log).

# Home page
After signing in, the home button is displayed in place of the sign-in button allowing the user to enter the app.

If a user does not have any contacts they will see a welcome message as well as for instructions as to how to start adding contacts to their account.

If the user does already have contacts then the homepage is used as the primary information dashboard. A large table presents information about each contact,
the suggested next message date, the suggested next message, a column that will display a red alert if there is extreme weather in the contact's location, and
four buttons that offer essential functionality.

On our home page, we have a large table that presents information about each contact, our navbar at the top, and 4 buttons for each contact.
The table is made by HTML and CSS, and the data we receive is from the server-side with the help of get_contact, represented in the HTML with jinja.
The generated suggested message is created by a message template taken from the DB based on the contact's information, the user's information, and the message_id of said contact.
Messages are generated by using the python function message_maker.
The message_id for each contact is gathered from the DB and is inputted in the table by using the python function get_message_id.
The function get_message_id gets the id of a specific message (from messages table) that matches the connection both in relationship type and in message type  (birthday or general).
The selected message's id will be the least used message per connection (user to contact). This is assessed by going over the log table of the interaction between the said user and contact.

# Add contact
Users can click on the contact's button in the menu and add contacts that they want to keep in touch with. Each contact must have a full name, a valid
email address, type of relationship, and the frequency of contact. A user should choose to add more data on each contact in the correct fields to
receive better-suggested messages from our server - more on that later! After the server receives the data on each contact from the user, it stores the data in
an SQLite table called contacts. Each contact has it's own id, the owner's id (which equals to user id in the users_google table), birthday, last contact,
next contact, which country they are currently in, honorifics, and a custom sign off to have when writing for the contact.

# Delete contact
After adding all our contacts, we can delete contacts from the contacts page. In the table, made by HTML and CSS, we receive some of our contact information
and the option to delete one of our contacts. All the data we have in the table is sorted to have the contacts that we need to contact first at the top
of our table. We created get_contacts, a helper function that receives sorted data from our contacts table based on the current user id.
Under the hood, if a user wants to delete contacts, the server receives a POST request, along with a contact id when the user clicks the delete button.
On the server-side, we delete the contact from our contacts table. In our delete statement, we delete the contact if the owner is only this current user,
to avoid other users who try to manipulate the HTML data (with Chrome's inspect) to send our server a different contact id and by doing restrict them from
deleting other users' contacts.

# Messages
The id of a specific message is also stored for each contact in the contacts table. This field will be refreshed every time a user contacts a contact or if the user refreshes the message.
The message_id is updated by using the get_message_id function that selects messages matching the connection (user to contact), occasion (based on date), and frequency of use (selects least used messages).
The generation of messages is provided by the function message_maker that takes the message_id and returns a message tailored to the contact_id and the user_id.
Email messages will also be generated in HTML with the use of the function make_html_message that formats the message from message_maker to HTML format.
The connections' (user to contact) seen messages (both the ones the user has seen but has chosen not to use and the ones the user chose to use) will be logged in the log database for quality assurance purposes.
The log database is used to assess the number of times a message has been used for a certain connection (user to contact).

# Our 4 buttons for each contact have the following purpose:
1. The V button - Updates the database that our last contact with this contact is today and generates a new suggested next contact.
We pass to our server the contact's id and the server uses the DateTime python library to receive today's date and updates the contact database table.
We also use get next contact, another helper function that calculates the suggested next contact based on the contact's frequency
(that the user added when created each contact) and last contact.
2. Message button - sends the suggested message to the contact's email, with the help of mailjet API, and updates the database with the same update function
we used the V button that we contact this contact today.
3. Copy to clipboard - Implemented in javascript, when a user clicks this button the suggested message is being copied to his/her clipboard. This functionality
helps our users to send our generated messages on other platforms, other than email.
4. Refresh button - Generates a new message for a contact, based on the information provided when created the contact and on the log table (giving preference to least used messages).

# All 4 buttons are implemented visually with HTML and CSS, and each, other than copy to clipboard, sends a unique POST request for our server.
Weather alerts - if a contact is in the US, we used weather.gov API to generate weather alerts in our homepage table. We passed alerts to our client-side
and with jinja conditional, we add a "🔴" next to a contact that has weather alerts in his/her area. This functionality helps you reach out to them and make
sure they are safe.

# Use of the National Weather Service API
In order to implement the severe weather alert functionality, we access the national weather service's API and query for extreme weather alerts in the states
in which the user has contacts. This query is constructed in python and then passed to the client-side using Jinja.

# -- Calendar page --
Implemented with HTML, CSS, and javascript, we show each user a full calendar with the dates he should contact his/her contacts. We used the helper function
get contacts to send the data to the client-side and with the help of FullCalendarIO, we added events to each user's calendar.

# -- Sign out --
A user can sign out by clicking the sign out button. When a user clicks it, we use Google's auth2.signOut function that signs out the user. Moreover, we
use session.clear() to clear the user's session and avoiding them from entering the website without signing in first.
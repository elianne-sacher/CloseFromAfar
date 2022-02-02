# Close from Afar

Close from Afar is a web app that is designed to help you keep track and stay in touch with your friends, family, colleagues, coworkers, etc.

## Non-Technical Description

Close from Afar allows users to login with their Google accounts and input contacts into the web app and then suggests, based on the characterstics of the relationship and contact, <br />
when each person should be contacted, suggests a message to send them, and offers functionality for sending the message (email / copy to clipboard). <br />
The dates at which each person should be contacted next can be viewed in the table on the homepage or on the calendar page. Moreover, by linking up to Weather.gov's <br />
API, Close from Afar monitors the U.S. for severe weather alerts in your contact's area and informs you if there is an alert. That way you can always make sure <br />
your friends, family, coworkers, and acquaintances are doing OK!

## User Guide

    Log in using your Gmail account
    Click on home (will appear after a slight delay during the authentication)
    Click on the contacts icon
    Click on add contact
    Input contact details
    Repeat add contact for all your contacts
    Click on home icon
    View your contacts in order of next contact date
    View your contacts' birthday if it is ealier than the suggested next contact
    Use either the email button or copy to clipboard to send the suggested message on the suggested date
    After contacting someone click the check button to tell Close from Afar that they have been contacted
    If you would like a different message click the refresh button to generate a new message
    If you want to delete a contact delete it in the contacts page
    Click on the calendar icon to see when you should contact all of your network
    Click log out --> sign out to sign out of Close from Afar


## General App Features

    Users can create an account through Google OAUTH2
    Users can add relationships
    Users can categorize relationships
    Users can input information about each relationship
    Users can define how often they would like to contact each relationship
    Users can view all their relationships
    Users can view their contacts' birthdays
    Users can delete relationships
    Users recieve custom suggested messages per contact
    Users recieve custom birthday messages when a contact's birthday is today
    Users can email relatioships the suggested message
    Users can tailor their sign-offs
    Users can copy to clipboard suggested messages
    Users can refresh the suggested message
    Users can update the next contact date
    Users can view all next contact dates on a calendar
    Users can see severe weather alerts
    Users can sign out
    Site works on mobile and desktop


## Technical Description

Close from Afar is a Flask-based web application written using Python, Javascript, HTML5, SQLite CSS, and Jinja. The application stores contact and user information in an <br />
SQLlite database. Login and account authentication is run through Google's OAUTH2 authentication API. Weather reports are received from Weather.gov's API.

## Technologies Used

Python
Javascript
HTML5
CSS
Flask
Jinja
SQLlite
Mailjet
Google.oauth2
FullCalendarIO
Other libraries

## API Credentials

Video example of how to prepare the API credentials: https://youtu.be/UN5_e3SK2Y0

    1. Go to https://console.developers.google.com/apis/credentials
    2. Click on the project dropdown menu in the top left corner
    3. Click on new project
    4. Create a new project
    5. In your new project click on "Create Credentials"
    6. Click on "OAuth client ID"
    7. Go to OAuth consent screen if prompted and click "External"
    8. Click create
    9. Fill out app name (Can be 'closefromafar')
    10. Insert user support gmail
    11. Insert email addresses under developer contact information
    12. Click save and continue until you get to dashboard and click back to dashboard
    13. Click credentials
    14. Click "Create Credentials"
    15. Select "Web application"
    16. In another tab open the CS50 IDE and open the project folder, "final"
    17. Run "pip install mailjet_rest" in the terminal
    18. Run "flask run" while in the "final" folder
    19. Copy the URL that flask gives you
        It will look something like this: https://41ee639f-27e3-4739-b373-33718b199e98-ide.cs50.xyz:8080
    20. Return to the Create OAuth Client ID tab
    21. Under Authorized JavaScript Origins add two links: (Note that you should delete hte )
        1. The URL you copied from the IDE flask but without the :8080 and make sure you change https to http.
            It will look something like this: http://41ee639f-27e3-4739-b373-33718b199e98-ide.cs50.xyz
        2. http://localhost:8080
    22. Under Authorized Redirect URLs add: the same 2 links under Authorized JavaScript Origins
    23. Click create
    24. Copy "Your Client ID"
    25. Return to the IDE
    26. Paste "Your Client ID" on line 20 of application.py
        CLIENT_ID = "{{ PASTE YOUR CLIENT ID}}"
    27. Paste "Your Client ID" on line 26 of signin.html
        <meta name="google-signin-client_id" content="{{ PASTE YOUR CLIENT ID}}">
    28. Paste the URL you copied from the IDE before on line 58 of signin.html
        The same as you used in the client credentials - but add /signin and make sure it is http and not https.
        Will look similar to (but with your link):
            xhr.open('POST', 'http://41ee639f-27e3-4739-b373-33718b199e98-ide.cs50.xyz/signin');
    29. Save and run flask again
    Attached is a video we created that walks through this process: https://youtu.be/UN5_e3SK2Y0

## Installation

```bash
pip install mailjet_rest
```

## Usage

To run the application:
```//In terminal
CD final
flask run
```
App infrustructure overview:
    Final - holds all the files and folders for the application to run
    Static - holds all CSS and calendar JS files
    Templates - holds all HTML files
    Application.py - holds all the main Python functions that run the backend of the application
    Helpers.py - holds helper function for the backend of the application
    closefromafar.db - SQLlite database holding information about the users, contacts, and messages

## Potential improvements

More suggested messages, customizable templates, sign-offs
More datafields on contacts to have increasingly relevant suggested messages
Narrow weather alerts to a smaller region per contact and expand globally
Added communication functionality (send through Facebook, SMS, Whatsapp...)
Add playful arch-nemesis relationship category that suggests clever disses to send to your arch-nemeses
Utilize ReactNative to convert the app to iOS and Android

## Authors

Project authors:
    Elianne Sacher
    Ido Burstein
    Ty Geri

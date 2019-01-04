#!/usr/bin/env python3
#
# A Catalog webapp that allows users to manage items witin categories

# General python imports
import random
import string
import requests
import json
import httplib2

# Used to create a flow object from the client_secrets file
from oauth2client.client import flow_from_clientsecrets

# Used to catch errors when exchanging an authorization code for an accesstoken
from oauth2client.client import FlowExchangeError

# Flask Imports
from flask import Flask, request, render_template
from flask import redirect, url_for, flash, session, jsonify, make_response

# Import in object to CRUD data
from dbconnect import DBConnect

app = Flask(__name__)

# Loads in file containing client secret
CLIENT_ID = json.loads(open('secret/client_secrets.json',
                            'r').read())['web']['client_id']


# Renders login page and ensures that the login request is coming from the
# appropriate source
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase +
                                  string.digits) for x in xrange(32))
    session['state'] = state
    return render_template('login.html', STATE=state)


# Implements google login
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Verify that the token the client sends the server matches the one
    # that was sent
    if request.args.get('state') != session['state']:
        # If they do not match then respond with an error
        response = make_response(json.dumps('Invalid state token'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # If the state tokens match then we take our code
    code = request.data
    # Try to use the one time code and exchange it for a
    # credentials object
    try:
        # Create oauth flow object and adds client secret key info to
        # that object
        oauth_flow = flow_from_clientsecrets('secret/client_secrets.json',
                                             scope='')
        # Specify that this the one time code flow this server sends off
        oauth_flow.redirect_uri = 'postmessage'
        # Init exchange
        credentials = oauth_flow.step2_exchange(code)
    # Handle the case where an error occurs during the exchange
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the\
        authorization code'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check to see if there is a valid access token inside of the
    # returned credentials
    access_token = credentials.access_token
    url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'\
          % access_token
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result['error']), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Compare id in the credentials object against the id returned
    # by the google api server
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps('Token user ID does not\
        match given user ID'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Compare client IDs
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps('Token client ID does not\
        match the apps ID'), 401)
        print('Token client ID does not match the apps ID')
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check if the user is already logged into the system
    stored_credentials = session.get('credentials')
    stored_gplus_id = session.get('gplus_id')
    if stored_credentials is not None and stored_gplus_id == gplus_id:
        response = make_response(json.dumps('Current user is\
        already logged in'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store credentials and google plus id in this session
    session['credentials'] = credentials.access_token
    session['gplus_id'] = gplus_id

    # Get more information about the user from the google plus api
    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)
    # Store user info in login session
    session['username'] = data['email']
    session['email'] = data['email']
    session['picture'] = data['picture']

    db = DBConnect()
    userID = db.getUserIDByEmail(session['email'])
    if userID is None:
        db.createUser(session['username'],
                      session['email'],
                      session['picture'])
        userID = db.getUserIDByEmail(session['email'])

    session['user_id'] = userID
    output = ''
    output += '<h1>Welcome, '
    output += session['username']
    return output


# Logout
@app.route('/gdisconnect')
def gdisconnect():
    # Check if a user is connected
    access_token = session.get('credentials')
    if access_token is None:
        print('Access token is none')
        return render_template('disconnected.html', message='Current\
        user not connected')
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    # If we get the ok from google then go ahead and disconnect
    if result['status'] == '200':
        del session['credentials']
        del session['gplus_id']
        del session['username']
        del session['email']
        del session['picture']
        return render_template('disconnected.html', message='You have\
        been successfully disconnected!')
    else:
        # If not then the access token is likely expired so we
        # clear the user data anyways
        del session['credentials']
        del session['gplus_id']
        del session['username']
        del session['email']
        del session['picture']
        result = h.request(url, 'GET')[0]
        if result['status'] == '200':
            return render_template('disconnected.html', message='You have\
            been successfully disconnected!')
        return render_template('disconnected.html', message='Disconnect\
        Failed!')


# Display cathegories and top items in each category
@app.route('/')
@app.route('/catalog')
def catalog():
    db = DBConnect()
    categories = db.getAllCategories()
    recentItems = db.getAllRecentItems()
    return render_template('categories.\
html', categories=categories, recentItems=recentItems)


# Add in a new category
@app.route('/catalog/new', methods=['GET', 'POST'])
def newCategory():
    if request.method == 'POST':
        # Get name from the posted form
        name = request.form['name'].strip()
        # Verify that a name was entered
        if name:
            db = DBConnect()
            # Check if this category already exsists
            if not db.categoryNameUsed(name):
                # Add the new category
                db.addCategory(name, 1)
                # Redirect to catalog page
                return redirect(url_for('catalog'))
                # If the category was not added, redirect the
                # user to the error page
            return redirect(url_for('error', error='This name\
            was already used'))
        return redirect(url_for('error', error='You need to enter a name'))

    if request.method == 'GET':
        user = session.get('username')
        if user is None:
            return redirect(url_for('showLogin'))
        return render_template('newCategory.html')


# Show items in a selected catagory
@app.route('/catalog/<string:category_name>')
def showCategory(category_name):
    db = DBConnect()
    categories = db.getAllCategories()
    items = db.getItemsByCategory(category_name)
    count = db.getItemCountByCategory(category_name)
    return render_template('showCategory.html',
                           categories=categories,
                           items=items,
                           categoryName=category_name,
                           numberOfItems=count)


# Shows the description for a selected item
@app.route('/catalog/<string:category_name>/<string:item_name>')
def showItem(category_name, item_name):
    db = DBConnect()
    selectedItem = db.getItemByName(item_name)
    userEmail = session.get('email')
    userID = db.getUserIDByEmail(userEmail)
    if userID != selectedItem.user.id:
        return render_template('publicShowItem.html\
', selectedItem=selectedItem, categoryName=category_name)
    return render_template('showItem.html\
', selectedItem=selectedItem, categoryName=category_name)


# Edit the name of a selected category
@app.route('/catalog/<string:category_name>/edit', methods=['GET', 'POST'])
def editCategory(category_name):
    if request.method == 'GET':
        return 'Getting template for editing category :%s' % category_name

    if request.method == 'POST':
        return 'Editing category :%s and redirecting\
        to catalog page' % category_name


# Add a new Item
@app.route('/catalog/<string:category_name>/new', methods=['GET', 'POST'])
def newItem(category_name):
    if request.method == 'POST':
        # Strip off the extra spaces the user may have entered
        name = request.form['name'].strip()
        description = request.form['description']
        # Ensure we have needed item info
        if name and description:
            db = DBConnect()
            isUsed = db.itemNameUsed(name)
            # Check if the item name has already been used somewhere else
            if not isUsed['used']:
                category = db.getCategoryByName(category_name)
                userID = db.getUserIDByEmail(session['email'])
                db.addItem(name, description, category.id, userID)
                return redirect(url_for('showItem\
', category_name=category_name, item_name=name))
            return redirect(url_for('error', error='This\
            item name has already been used'))
        return redirect(url_for('error', error='You need to enter\
        both a name and description'))

    if request.method == 'GET':
        user = session.get('username')
        if user is None:
            return redirect(url_for('showLogin'))
        return render_template('newItem.html', categoryName=category_name)


# Edit an Item
@app.route('/catalog/<string:category_name>/<string:item_name>\
/edit', methods=['GET', 'POST'])
def editItem(category_name, item_name):
    db = DBConnect()
    item = db.getItemByName(item_name)
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        categoryName = request.form['category']
        if name and description and categoryName:
            category = db.getCategoryByName(categoryName)
            db.editItem(item, name, description, category.id)
            return redirect(url_for('showItem',
                                    category_name=category.name,
                                    item_name=name))

    if request.method == 'GET':
        # Authorization check before serving the edit page
        userEmail = session.get('email')
        userID = db.getUserIDByEmail(userEmail)
        if userID != item.user.id:
            return redirect(url_for('error', error='You are not\
            authorized to edit this item'))
        categories = db.getAllCategories()
        return render_template('editItem.html',
                               selectedItem=item,
                               categories=categories)


# Delete an Item
@app.route('/catalog/<string:category_name>/<string:item_name>\
/delete', methods=['GET', 'POST'])
def deleteItem(category_name, item_name):
    db = DBConnect()
    item = db.getItemByName(item_name)
    if request.method == 'POST':
        db.deleteItem(item)
        return redirect(url_for('showCategory', category_name=category_name))

    if request.method == 'GET':
        # Authorization check before serving the delete page
        userEmail = session.get('email')
        userID = db.getUserIDByEmail(userEmail)
        if userID != item.user.id:
            return redirect(url_for('error', error='You are not\
            authorized to delete this item'))
        return render_template('deleteItem.html',
                               categoryName=category_name,
                               itemName=item_name)


# Error page
@app.route('/catalog/error/<string:error>')
def error(error):
    return render_template('errorpage.html', error=error)


# JSON endpoint, contains all categories and items
@app.route('/catalog.json')
def catalogJSON():
    user = session.get('username')
    if user is None:
        return redirect(url_for('showLogin'))
    db = DBConnect()
    categories = db.getAllCategories()
    # Building the json object to be returned
    total = {'Category': []}
    for c in categories:
        items = db.getItemsByCategory(c.name)
        total['Category'].append({'id': c.id, 'name': c.name,
                                 'items': [i.serialize for i in items]})
    return jsonify(total)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)

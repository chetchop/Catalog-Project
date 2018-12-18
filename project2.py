import sys, os, random, string

from flask import Flask, request, render_template, redirect, url_for, flash, session
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/database")
from dbconnect import DBConnect

# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"


@app.route('/login')
def showlogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange (32))
    session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = session.get('access_token')
    stored_gplus_id = session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    session['access_token'] = credentials.access_token
    session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    session['username'] = data['email']
    session['picture'] = data['picture']
    session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += session['username']
    output += '!</h1>'
    output += '<img src="'
    output += session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % session['username'])
    print "done!"
    return output


# Display cathegories and top items in each category
@app.route('/')
@app.route('/catalog')
def catalog():
    db = DBConnect()
    categories = db.getAllCategories()
    recentItems = db.getAllRecentItems()
    return render_template('main.html', categories=categories, recentItems=recentItems)

# Add in a new category
@app.route('/catalog/new', methods=['GET','POST'])
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
                # If the category was not added, redirect the user to the error page
            return redirect(url_for('error', error='This name was already used'))
        return redirect(url_for('error', error='You need to enter a name'))
            # Insert message flashing here, secret key shit must be done first 
    if request.method == 'GET':
        return render_template('newCategory.html')

# Show items in a selected catagory
@app.route('/catalog/<string:category_name>')
def showCategory(category_name):
    db = DBConnect()
    categories = db.getAllCategories()
    items = db.getItemsByCategory(category_name)
    count = db.getItemCountByCategory(category_name)
    return render_template('showCategory.html', categories=categories, items=items, 
    categoryName=category_name, numberOfItems=count)


# Shows the description for a selected item 
@app.route('/catalog/<string:category_name>/<string:item_name>')
def showItem(category_name, item_name):
    db = DBConnect()
    selectedItem = db.getItemByName(item_name)
    return render_template('showItem.html', selectedItem=selectedItem, categoryName=category_name)


# Edit the name of a selected category
@app.route('/catalog/<string:category_name>/edit', methods=['GET', 'POST'])
def editCategory(category_name):
    if request.method == 'GET':
        return 'Getting template for editing category :%s' % category_name

    elif request.method == 'POST':
        return 'Editing category :%s and redirecting to catalog page' % category_name


# Add a new Item
@app.route('/catalog/<string:category_name>/new', methods=['GET', 'POST'])
def newItem(category_name):
    if request.method == 'POST':       
        name = request.form['name'].strip()
        description = request.form['description']

        if name and description:
            db = DBConnect()
            isUsed = db.itemNameUsed(name)

            if not isUsed['used']:
                category = db.getCategoryByName(category_name)
                db.addItem(name, description, category.id, 1)
                return redirect(url_for('showItem', category_name=category_name, item_name=name))
            return redirect(url_for('error', error='This item name has already been used'))

        return redirect(url_for('error', error='You need to enter both a name and description'))

    if request.method == 'GET':
        return render_template('newItem.html', categoryName=category_name)


# Edit an Item
@app.route('/catalog/<string:category_name>/<string:item_name>/edit', methods=['GET', 'POST'])
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
            return redirect(url_for('showItem', category_name=category.name, item_name=name))
    if request.method == 'GET':     
        categories = db.getAllCategories()
        return render_template('editItem.html', selectedItem=item, categories=categories)
    
        

# Delete an Item
@app.route('/catalog/<string:category_name>/<string:item_name>/delete', methods=['GET', 'POST'])
def deleteItem(category_name, item_name):
    if request.method == 'POST':
        db = DBConnect()
        item = db.getItemByName(item_name)
        db.deleteItem(item)
        return redirect(url_for('showCategory', category_name=category_name))
    if request.method == 'GET':
        return render_template('deleteItem.html', categoryName=category_name, itemName=item_name)

# Error page
@app.route('/catalog/error/<string:error>')
def error(error):
    return render_template('errorpage.html', error=error)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)


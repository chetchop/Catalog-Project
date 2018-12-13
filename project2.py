from flask import Flask, request

app = Flask(__name__)

# Display cathegories and top items in each category
@app.route('/')
@app.route('/catalog')
def catalog():
    return 'John eats loud as fuck'

# Add in a new category
@app.route('/catalog/new', methods=['GET','POST'])
def newCategory():
    if request.method == 'GET':
        return 'Getting the template for adding a new category'
    
    elif request.method == 'POST':
        return 'Adding in new category and redirecting back to catalog page'

# Edit the name of a selected category
@app.route('/catalog/<string:category_name>/edit', methods=['GET', 'POST'])
def editCategory(category_name):
    if request.method == 'GET':
        return 'Getting template for editing category :%s' % category_name

    elif request.method == 'POST':
        return 'Editing category :%s and redirecting to catalog page' % category_name

# Show items in a selected catagory
@app.route('/catalog/<string:category_name>')
def showCategory(category_name):
    return 'Getting template for showing items in category: %s' % category_name


# Shows the description for a selected item 
@app.route('/catalog/<string:category_name>/<string:item_name>')
def showItem(category_name, item_name):
    return 'This is showing category: %s and item: %s' % (category_name, item_name)


@app.route('/catalog/<string:category_name>/new', methods=['GET', 'POST'])
def newItem(category_name):
    if request.method == 'GET':
        return 'This will return the template for adding in a new item in category %s' % category_name
    elif request.method == 'POST':
        return 'This will add in a new item in the category %s' % category_name

@app.route('/catalog/<string:category_name>/<string:item_name>/edit', methods=['GET', 'POST'])
def editItem(category_name, item_name):
    if request.method == 'GET':
        return 'This will return the template for editing the %s item in category %s' % (item_name, category_name)
    elif request.method == 'POST':
        return 'This will edit the %s item in the category %s' % (item_name, category_name)

@app.route('/catalog/<string:category_name>/<string:item_name>/delete', methods=['GET', 'POST'])
def deleteItem(category_name, item_name):
    if request.method == 'GET':
        return 'This will return the template for deleting the %s item in category %s' % (item_name, category_name)
    elif request.method == 'POST':
        return 'This will delete the %s item in the category %s' % (item_name, category_name)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
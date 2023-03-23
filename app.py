from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Catalog, Base, Book, User
from flask import session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from google.auth.transport import requests
from google.oauth2.credentials import Credentials
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "The Bookshelf"


engine = create_engine('sqlite:///bookscatalog.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
sessionDB = DBSession()

# JSON ENDPOINT return all the catalogs


@app.route('/catalogs/JSON')
def allCatalogsJSON():
    catalog = sessionDB.query(Catalog).all()
    return jsonify(Catalogs=[i.serialize for i in catalog])


# JSON ENDPOINT return specific catalog and its books
@app.route('/catalogs/<int:catalog_id>/JSON')
def catalogJSON(catalog_id):
    catalog = sessionDB.query(Catalog).filter_by(id=catalog_id).one()
    books = sessionDB.query(Book).filter_by(
        catalog_id=catalog_id).all()
    return jsonify(Books=[i.serialize for i in books])


# JSON ENDPOINT return specific book
@app.route('/catalogs/<int:catalog_id>/book/<int:book_id>/JSON')
def bookJSON(catalog_id, book_id):
    book = sessionDB.query(Book).filter_by(id=book_id).one()
    return jsonify(Book=book.serialize)

# all the bookshelf data.


@app.route('/data/JSON')
def dataJSON():
    catalogs = sessionDB.query(Catalog).all()
    catalogsJSON = [c.serialize for c in catalogs]
    for c in range(len(catalogsJSON)):
        books = [i.serialize for i in sessionDB.query(Book).filter_by(
            catalog_id=catalogsJSON[c]["id"]).all()]
        if books:
            catalogsJSON[c]["books"] = books
    return jsonify(Catalogs=catalogsJSON)


@app.route('/')
@app.route('/home')
def homepage():
    return render_template('home.html')


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    session['state'] = state
    return render_template('login.html', STATE=state)


# use google account to login to the web-app
@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
    Handles the Google login process.

    Returns:
        A JSON response indicating whether the login was successful or not.
    """

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

    response = requests.get(url, headers={'Authorization': f'Bearer {access_token}'})
    response.raise_for_status()
    result = response.json()

    if result.get('error') is not None:
        error_msg = result.get('error')
        raise Exception(f"Error in access token info: {error_msg}")

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        raise Exception("Token's user ID doesn't match given user ID.")

    if result['issued_to'] != CLIENT_ID:
        raise Exception("Token's client ID does not match app's.")


    # Store the access token and gplus_id in the session for later use.
    session['access_token'] = credentials.access_token
    session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # Store user info in the session for later use.
    session['username'] = data['name']
    session['picture'] = data['picture']
    session['email'] = data['email']

    # Create user if it doesn't exist in the database.
    user_id = getUserID(session['email'])
    if not user_id:
        user_id = createUser(session)
    session['user_id'] = user_id

    # Return a success response.
    response = make_response(json.dumps('Login successful.'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response

    
    # Set up the credentials and gplus_id
    credentials = Credentials.from_authorized_user_info(authorized_user_info, scopes)
    gplus_id = authorized_user_info['sub']

    # Call the handle_login function to handle the login process
    handle_login(credentials, gplus_id)



    # Constants
USERINFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"
DEFAULT_IMAGE_SIZE = 300
DEFAULT_IMAGE_BORDER_RADIUS = 150

def get_user_info(access_token):
    """Get user info from the Google API."""
    params = {'access_token': access_token, 'alt': 'json'}
    response = requests.get(USERINFO_URL, params=params)

    if not response.ok:
        raise ValueError('Error getting user info')

    return response.json()

def create_user_if_not_exists(session):
    """Create a new user if the user does not exist."""
    email = session.get('email')

    if not email:
        raise ValueError('Email is missing in session')

    user_id = getUserID(email)

    if not user_id:
        user_id = createUser(session)

    session['user_id'] = user_id

def generate_output_html(session):
    """Generate the output HTML with the user info."""
    username = session.get('username')
    picture = session.get('picture')

    if not username or not picture:
        raise ValueError('Username or picture is missing in session')

    output = '<h1>Welcome, {}!</h1>'.format(username)
    output += '<img src="{}" style="width: {}px; height: {}px; border-radius: {}px; -webkit-border-radius: {}px; -moz-border-radius: {}px;">'.format(
        picture, DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_BORDER_RADIUS, DEFAULT_IMAGE_BORDER_RADIUS, DEFAULT_IMAGE_BORDER_RADIUS)
    flash("You are now logged in as {}".format(username))
    return output

# Main function
def handle_login(credentials, gplus_id):
    """Handle the login process."""
    session['access_token'] = credentials.access_token
    session['gplus_id'] = gplus_id

    data = get_user_info(credentials.access_token)

    session['username'] = data.get('name')
    session['picture'] = data.get('picture')
    session['email'] = data.get('email')

    create_user_if_not_exists(session)

    output = generate_output_html(session)

    print("Done!")
    return output


# function to add the new user to database


def createUser(session):
    newUser = User(name=session['username'], email=session['email'])
    sessionDB.add(newUser)
    sessionDB.commit()
    user = sessionDB.query(User).filter_by(email=session['email']).one()
    return user.id

# function to get the info of the user from database


def getUserInfo(user_id):
    user = sessionDB.query(User).filter_by(id=user_id).one()
    return user

# function to search for the userID


def getUserID(email):
    try:
        user = sessionDB.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None


# DISCONNECT - Revoke a current user's token and reset their session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = session.get('access_token')
    if access_token is None:
        print ('Access Token is None')
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print ('result is ',result)
    if result['status'] == '200':
        del session['access_token']
        del session['gplus_id']
        del session['username']
        del session['email']
        del session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("you are now logged-out")
        return redirect(url_for('homepage'))
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/catalogs')
def catalogs():
    catalog = sessionDB.query(Catalog).all()
    return render_template('catalogs.html', catalog=catalog)


@app.route('/catalogs/<int:catalog_id>/book')
def catalogBooks(catalog_id):
    catalog = sessionDB.query(Catalog).filter_by(id=catalog_id).one()
    books = sessionDB.query(Book).filter_by(catalog_id=catalog_id)
    return render_template(
        'books.html', catalog=catalog, books=books, catalog_id=catalog_id)


#################################
# process for the book pages
#################################
@app.route('/catalogs/<int:catalog_id>/book/new', methods=['GET', 'POST'])
def newBook(catalog_id):
    if request.method == 'POST':
        addedBook = Book(name=request.form['name'], description=request.form['description'], author_name=request.form['author_name'],
                         publish_year=request.form['publish_year'], catalog_id=catalog_id, user_id=session['user_id'])
        sessionDB.add(addedBook)
        sessionDB.commit()
        flash("The book %s added successfully " % request.form['name'])
        return redirect(url_for('catalogBooks', catalog_id=catalog_id))
    else:
        return render_template('newBook.html', catalog_id=catalog_id)


@app.route('/catalogs/<int:catalog_id>/book/<int:book_id>/edite', methods=['GET', 'POST'])
def editBook(catalog_id, book_id):
    editedBook = sessionDB.query(Book).filter_by(id=book_id, user_id=session['user_id']).one_or_none()
    if editedBook is None:
        flash("You can edit only the book you created.")
        return redirect(url_for('catalogBooks', catalog_id=catalog_id))

    if request.method == 'POST':
        form_data = request.form.to_dict(flat=True)
        for key in ['name', 'description', 'author_name', 'publish_year']:
            if key in form_data:
                setattr(editedBook, key, form_data[key])
        sessionDB.commit()
        flash(f"The book {form_data['name']} updated successfully.")
        return redirect(url_for('catalogBooks', catalog_id=catalog_id))

    return render_template('editBook.html', catalog_id=catalog_id, book=editedBook)



@app.route('/catalogs/<int:catalog_id>/book/<int:book_id>/delete', methods=['GET', 'POST'])
def deleteBook(catalog_id, book_id):
    bookToDelete = sessionDB.query(Book).filter_by(id=book_id).one()
    if bookToDelete.user_id == session['user_id']:
        if request.method == 'POST':
            sessionDB.delete(bookToDelete)
            sessionDB.commit()
            flash("The book %s deleted successfully " % bookToDelete.name)
            return redirect(url_for('catalogBooks', catalog_id=catalog_id))
        else:
            return render_template('deleteBook.html', catalog_id=catalog_id, book=bookToDelete)
    else:
        flash("You can delete only the Book you create it")
        return redirect(url_for('catalogBooks', catalog_id=catalog_id))


#################################
# process for the catalog pages
#################################
@app.route('/catalogs/new', methods=['GET', 'POST'])
def newCatalog():

    if request.method == 'POST':
        addedCatalogs = Catalog(
            name=request.form['name'], user_id=session['user_id'])
        sessionDB.add(addedCatalogs)
        sessionDB.commit()
        flash("The catalog %s added successfully " % request.form['name'])
        return redirect(url_for('catalogs'))
    else:
        return render_template('newCatalog.html')


@app.route('/catalogs/<int:catalog_id>/edit', methods=['GET', 'POST'])
def editCatalog(catalog_id):
    editedCatalog = sessionDB.query(Catalog).filter_by(id=catalog_id).one()
    if editedCatalog.user_id == session['user_id']:
        if request.method == 'POST':
            if request.form['name']:
                editedCatalog.name = request.form['name']
            sessionDB.add(editedCatalog)
            sessionDB.commit()
            flash("The catalog %s updated successfully " %
                  request.form['name'])
            return redirect(url_for('catalogs'))
        else:
            return render_template('editCatalog.html', catalog_id=catalog_id, catalog=editedCatalog)
    else:
        flash("You can edit only the Catalogs you create it")
        return redirect(url_for('catalogs'))


@app.route('/catalogs/<int:catalog_id>/delete', methods=['GET', 'POST'])
def deleteCatalog(catalog_id):
    deletedCatalog = sessionDB.query(Catalog).filter_by(id=catalog_id).one()
    if deletedCatalog.user_id == session['user_id']:
        if request.method == 'POST':
            sessionDB.delete(deletedCatalog)
            sessionDB.commit()
            flash("The catalog %s deleted successfully " % deletedCatalog.name)
            return redirect(url_for('catalogs'))
        else:
            return render_template('deleteCatalog.html', catalog=deletedCatalog)
    else:
        flash("You can delete only the Catalogs you create it")
        return redirect(url_for('catalogs'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

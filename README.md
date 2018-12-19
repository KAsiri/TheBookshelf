
# The Bookshelf
#### Its a web app for organizing books by catalogs to help building a shelves for easy access the books.

## Setup Requirements:-
- Python  (https://www.python.org)
- Vagrant v2.2.0  (https://www.vagrantup.com/downloads.html) 
- VirtualBox v5.1.38  (https://www.vagrantup.com/downloads.html)
- OAuth 2.0 client IDs (https://console.developers.google.com/)

## Programing Languages and frameworks
- HTML
- CSS
- JavaScript
- Bootstrap
- Python
- Flask
- OAuth
- SQLite

## Authentication & Authorization
- The app will use a Third party Authentication system (OAuth) provided by Google, The app will only use the name, email and the picture of the user (name and email only will stored on the database) and will create an id for the user first time visiting the app.
- The app will only allow the loggedin user to add a new Catalog or book, and the user can edit or delete Catalog or book which he owns (he created).


## Instructions:-
- Install Vagrant and VirtualBox.
- You can use the Vagrant file in fullstack-nanodegree-vm Repo (https://github.com/udacity/fullstack-nanodegree-vm).
- Clone this project inside the Catalog folder.
- Setup your OAuth 2.0 client IDs by follow this guide (https://docs.google.com/presentation/d/1Ojb7KK96MOlqhZlxNz0vy2m7I6oDkXeEh-KRPWY1w2w/edit#slide=id.p)
- Download Your client_secret.json on the path (/vagrant/catalog)
- Launch the Vagrant VM (vagrant up).
- run the Vagrant VM (vagrant ssh).
- cd to the path (/vagrant/catalog).
- run the file database_setup.py (python database_setup.py).
- run the file seeder.py (python seeder.py) to insert some data on your database.
- run the file app.py (python app.py) to launch The Bookshelf app.
- Access and test the app by visiting (http://localhost:5000) locally.

## Important Notes: 
- The seeder.py will insert some data on the database, it will be owned by user (admin) so no one can edit/delete it.
- The Homepage will depend on the seeder.py file, so if you will not run it you most make change on the (/templates/home.html) file.

## Screenshots:
#### The Homepage
<img src="/Screenshot/Homepage.PNG" alt="Homepage" width="700" height="350">

#### The Login page
<img src="/Screenshot/Login.PNG" alt="Login page" width="700" height="350">

#### The Catalogs page
<img src="/Screenshot/AllCatalogs.PNG" alt="Catalogs page" width="700" height="350">

#### The Books page
<img src="/Screenshot/Books.PNG" alt="Books page" width="700" height="350">

#### The New Book page
<img src="/Screenshot/NewBook.PNG" alt="Book page" width="700" height="350">

## JSON Endpoint:
#### show all the data (Catalogs and its Books)
````
http://localhost:5000/data/JSON
````

#### show all the Catalogs
````
http://localhost:5000/catalogs/JSON
````

#### show all the data of specific Catalog
````
http://localhost:5000/catalogs/<int:catalog_id>/JSON
````

#### show all the data of specific Book
````
http://localhost:5000/catalogs/<int:catalog_id>/book/<int:book_id>/JSON
````

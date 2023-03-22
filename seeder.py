from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Catalog, Base, Book, User

# create engine
engine = create_engine('sqlite:///bookscatalog.db')

# bind metadata to engine
Base.metadata.bind = engine

# create session factory
DBSession = sessionmaker(bind=engine)


def add_user(name, email, session):
    """Adds a user to the database."""
    user = User(name=name, email=email)
    session.add(user)
    session.commit()


def add_catalog(name, user, session):
    """Adds a catalog to the database."""
    catalog = Catalog(name=name, user=user)
    session.add(catalog)
    session.commit()
    return catalog


def add_book(name, description, author_name, publish_year, catalog, user, session):
    """Adds a book to the database."""
    book = Book(name=name, description=description, author_name=author_name, publish_year=publish_year, catalog=catalog, user=user)
    session.add(book)
    session.commit()


def add_sample_data():
    """Adds sample data to the database."""
    # create session
    session = DBSession()

    # add admin user
    add_user(name="Admin", email="admin@admin.c", session=session)

    # add catalogs and books
    admin_user = session.query(User).filter_by(name="Admin").one()

    history_catalog = add_catalog(name="History", user=admin_user, session=session)
    add_book(name="First History Book", description="Description of the First History Book ...", author_name="Author A", publish_year="2005", catalog=history_catalog, user=admin_user, session=session)
    add_book(name="Second History Book", description="Description of the Second History Book ...", author_name="Author B", publish_year="2010", catalog=history_catalog, user=admin_user, session=session)
    add_book(name="Third History Book", description="Description of the Third History Book ...", author_name="Author C", publish_year="2015", catalog=history_catalog, user=admin_user, session=session)

    sciences_catalog = add_catalog(name="Sciences", user=admin_user, session=session)
    add_book(name="First Sciences Book", description="Description of the First Sciences Book ...", author_name="Author D", publish_year="2002", catalog=sciences_catalog, user=admin_user, session=session)
    add_book(name="Second Sciences Book", description="Description of the Second Sciences Book ...", author_name="Author B", publish_year="2008", catalog=sciences_catalog, user=admin_user, session=session)
    add_book(name="Third Sciences Book", description="Description of the Third Sciences Book ...", author_name="Author E", publish_year="2013", catalog=sciences_catalog, user=admin_user, session=session)

    kids_catalog = add_catalog(name="Kids", user=admin_user, session=session)
    add_book(name="First Kids Book", description="Description of the First Kids Book ...", author_name="Author F", publish_year="2010", catalog=kids_catalog, user=admin_user, session=session)
    add_book(name="Second Kids Book", description="Description of the Second Kids Book ...", author_name="Author

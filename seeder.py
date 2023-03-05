from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Catalog, Base, Book, User
 
engine = create_engine('sqlite:///bookscatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Admin
user = User(name = "Admin",email = "admin@admin.c")

session.add(user)
session.commit()

#Books for History
catalog1 = Catalog(name = "History", user = user)

session.add(catalog1)
session.commit()


book1 = Book(name = "First History Book", description = "Description of the First History Book ...", author_name = "Author A", publish_year = "2005", catalog = catalog1, user = user)

session.add(book1)
session.commit()

book2 = Book(name = "Second History Book", description = "Description of the Second History Book ...", author_name = "Author B", publish_year = "2010", catalog = catalog1, user = user)

session.add(book2)
session.commit()

book3 = Book(name = "Third History Book", description = "Description of the Third History Book ...", author_name = "Author C", publish_year = "2015", catalog = catalog1, user = user)

session.add(book3)
session.commit()

#Books for Sciences
catalog2 = Catalog(name = "Sciences", user = user)

session.add(catalog2)
session.commit()


book1 = Book(name = "First Sciences Book", description = "Description of the First Sciences Book ...", author_name = "Author D", publish_year = "2002", catalog = catalog2, user = user)

session.add(book1)
session.commit()

book2 = Book(name = "Second Sciences Book", description = "Description of the Second Sciences Book ...", author_name = "Author B", publish_year = "2008", catalog = catalog2, user = user)

session.add(book2)
session.commit()

book3 = Book(name = "Third Sciences Book", description = "Description of the Third Sciences Book ...", author_name = "Author E", publish_year = "2013", catalog = catalog2, user = user)

session.add(book3)
session.commit()


#Books for Kids
catalog3 = Catalog(name = "Kids", user = user)

session.add(catalog3)
session.commit()


book1 = Book(name = "First Kids Book", description = "Description of the First Kids Book ...", author_name = "Author F", publish_year = "2010", catalog = catalog3, user = user)

session.add(book1)
session.commit()

book2 = Book(name = "Second Kids Book", description = "Description of the Second Kids Book ...", author_name = "Author C", publish_year = "2017", catalog = catalog3, user = user)

session.add(book2)
session.commit()


#Books for Crime
catalog4 = Catalog(name = "Crime", user = user)

session.add(catalog4)
session.commit()


book1 = Book(name = "First Crime Book", description = "Description of the First Crime Book ...", author_name = "Author A", publish_year = "2012", catalog = catalog4, user = user)

session.add(book1)
session.commit()

book2 = Book(name = "Second Crime Book", description = "Description of the Second Crime Book ...", author_name = "Author E", publish_year = "2001", catalog = catalog4, user = user)

session.add(book2)
session.commit()


print "Catalog & Books added!"

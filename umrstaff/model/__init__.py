# -*- coding: utf-8 -*-
"""The application's model objects"""

import zope.sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# Global session manager: DBSession() returns the Thread-local
# session object appropriate for the current web request.
maker = sessionmaker(autoflush=True, autocommit=False)
DBSession = scoped_session(maker)
zope.sqlalchemy.register(DBSession)

# Base class for all of our model classes: By default, the data model is
# defined with SQLAlchemy's declarative extension, but if you need more
# control, you can switch to the traditional method.
DeclarativeBase = declarative_base()

# There are two convenient ways for you to spare some typing.
# You can have a query property on all your model classes by doing this:
# DeclarativeBase.query = DBSession.query_property()
# Or you can use a session-aware mapper as it was used in TurboGears 1:
# DeclarativeBase = declarative_base(mapper=DBSession.mapper)

# Global metadata.
# The default metadata is the one from the declarative base.
metadata = DeclarativeBase.metadata

# If you have multiple databases with overlapping table names, you'll need a
# metadata for each database. Feel free to rename 'metadata2'.
# from sqlalchemy import MetaData
# metadata2 = MetaData()

#####
# Generally you will not want to define your table's mappers, and data objects
# here in __init__ but will want to create modules them in the model directory
# and import them at the bottom of this file.
######


def init_model(engine):
    """Call me before using any of the tables or classes in the model."""
    DBSession.configure(bind=engine)

    # If you are using reflection to introspect your database and create
    # table objects for you, your tables must be defined and mapped inside
    # the init_model function, so that the engine is available if you
    # use the model outside tg2, you need to make sure this is called before
    # you use the model.

    #
    # See the following example:
    #
    # global t_reflected
    # t_reflected = Table("Reflected", metadata,
    #                     autoload=True, autoload_with=engine)
    # mapper(Reflected, t_reflected)
    return DBSession

# Import your model modules here.
from umrstaff.model.auth import User, Group, Permission

from umrstaff.model.staff import Staff
# from umrstaff.model.team_leaders import TeamLeaders
from umrstaff.model.team import Team
from umrstaff.model.team_members import TeamMembers
from umrstaff.model.mailinglist import MailingList
from umrstaff.model.mailing_list_directory import MailingListDirectory
from umrstaff.model.position import Position
# from umrstaff.model.phone_number import PhoneNumber
# from umrstaff.model.phone_directory import PhoneDirectory
# from umrstaff.model.category import Category
# from umrstaff.model.staff_category import StaffCategory


__all__ = ('User', 'Group', 'Permission')

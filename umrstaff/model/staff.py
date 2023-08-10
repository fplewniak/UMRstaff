from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Text

from umrstaff.model import DeclarativeBase, metadata, DBSession

class Staff(DeclarativeBase):
    __tablename__ = 'staff'

    id = Column(Integer, primary_key=True)
    first_name = Column(Text)
    surname = Column(Text)
    user = Column(Text)
    email = Column(Text)

    def add(self, member):
        self.first_name = member.first_name
        self.surname = member.surname
        self.user = member.user
        self.email = member.mailing_list


from collections import namedtuple

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
    email = Column(Text)
    office = Column(Integer)
    office_tel = Column(Text)
    lab = Column(Integer)
    lab_tel = Column(Text)
    perso_tel = Column(Text)
    emergency_contact = Column(Text)
    emergency_tel = Column(Text)
    user = Column(Text)

    def add(self, member):
        self.first_name = member.first_name
        self.surname = member.surname
        self.email = member.email
        self.office = member.office
        self.office_tel = member.office_tel
        self.lab = member.lab
        self.lab_tel = member.lab_tel
        self.perso_tel = member.perso_tel
        self.emergency_contact = member.emergency_contact
        self.emergency_tel = member.emergency_tel
        self.user = member.user

    @staticmethod
    def namedtuple():
        return namedtuple('Staff',
                          ['first_name', 'surname', 'email', 'office', 'office_tel', 'lab', 'lab_tel', 'perso_tel',
                           'emergency_contact', 'emergency_tel', 'user'])

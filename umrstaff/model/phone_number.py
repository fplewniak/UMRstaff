from collections import namedtuple

import pandas
from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Text, Boolean

from umrstaff.model import DeclarativeBase, metadata, DBSession

class PhoneNumber(DeclarativeBase):
    __tablename__ = 'phone_number'

    id = Column(Integer, primary_key=True)
    number = Column(Text)
    location = Column(Text)

    def add(self, phone_number):
        self.number = phone_number.number
        self.location = phone_number.location

    @staticmethod
    def namedtuple():
        return namedtuple('Phone', ['number','location'])

    @staticmethod
    def exists(number):
        return number in list(pandas.read_sql_query('SELECT * from phone_number', DBSession.connection()).number)

    @staticmethod
    def get_id(number):
        if number:
            phone_list = pandas.read_sql_query('SELECT * from phone_number', DBSession.connection())
            rows = (phone_list.loc[(phone_list['number'] == number)])
            return(int(rows.id.iloc[0]))
        return -1

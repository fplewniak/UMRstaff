from collections import namedtuple

import pandas
from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Text, Boolean

from umrstaff.model import DeclarativeBase, metadata, DBSession

class MailingList(DeclarativeBase):
    __tablename__ = 'mailing_lists'

    id = Column(Integer, primary_key=True)
    address = Column(Text)
    description = Column(Text)

    def add(self, email):
        print(type(email))
        self.address = email.address
        self.description = email.description

    @staticmethod
    def namedtuple():
        return namedtuple('MailingList', ['address', 'description'])

    @staticmethod
    def exists(address):
        return address in list(pandas.read_sql_query('SELECT * from mailing_lists', DBSession.connection()).address)

    @staticmethod
    def get_id(address):
        if address:
            email_list = pandas.read_sql_query('SELECT * from mailing_lists', DBSession.connection())
            rows = (email_list.loc[(email_list['address'] == address)])
            return(int(rows.id.iloc[0]))
        return -1

from collections import namedtuple

import pandas
from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Text, Boolean

from umrstaff.model import DeclarativeBase, metadata, DBSession

class PhoneDirectory(DeclarativeBase):
    __tablename__ = 'phone_directory'

    id = Column(Integer, primary_key=True)
    phone_number = Column(Integer, ForeignKey('phone_number.id'))
    staff = Column(Integer, ForeignKey('staff.id'))

    def add(self, phone_directory):
        self.phone_number = phone_directory.phone_number
        self.staff = phone_directory.staff

    @staticmethod
    def namedtuple():
        return namedtuple('PhoneDir', ['phone_number', 'staff'])

    @staticmethod
    def is_not_staff_phone(staff_id, phone_id):
        links = int(pandas.read_sql_query(
            f'SELECT count(*) from phone_directory as pd where  pd.phone_number = {phone_id} and pd.staff = {staff_id}',
            DBSession.connection()).iloc[0])
        return links == 0

    @staticmethod
    def clean(staff_id, number_ids):
        for number_staff in pandas.read_sql_query(
                f'select * from phone_directory where phone_directory.staff = {staff_id}',
                DBSession.connection()).itertuples():
            if number_staff.phone_number not in number_ids:
                DBSession.delete(PhoneDirectory.get_from_id(number_staff.id))

    @staticmethod
    def get_from_id(id_):
        return DBSession.query(PhoneDirectory).filter(PhoneDirectory.id == id_).first()

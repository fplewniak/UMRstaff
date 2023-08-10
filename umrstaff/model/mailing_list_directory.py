from collections import namedtuple

import pandas
from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Text, Boolean

from umrstaff.model import DeclarativeBase, metadata, DBSession

class MailingListDirectory(DeclarativeBase):
    __tablename__ = 'mailing_list_directory'

    id = Column(Integer, primary_key=True)
    email = Column(Integer, ForeignKey('mailing_lists.id'))
    staff = Column(Integer, ForeignKey('staff.id'))

    def add(self, mailing_list_directory):
        self.email = mailing_list_directory.email
        self.staff = mailing_list_directory.staff

    @staticmethod
    def namedtuple():
        return namedtuple('MailingListDir', ['email', 'staff'])

    @staticmethod
    def is_not_staff_email(staff_id, email_id):
        links = int(pandas.read_sql_query(
            f'SELECT count(*) from mailing_list_directory as ed where  ed.email = {email_id} and ed.staff = {staff_id}',
            DBSession.connection()).iloc[0])
        return links == 0

    @staticmethod
    def clean(staff_id, email_ids):
        for email_staff in pandas.read_sql_query(
                f'select * from mailing_list_directory where mailing_list_directory.staff = {staff_id}',
                DBSession.connection()).itertuples():
            if email_staff.email not in email_ids:
                DBSession.delete(MailingListDirectory.get_from_id(email_staff.id))

    @staticmethod
    def get_from_id(id_):
        return DBSession.query(MailingListDirectory).filter(MailingListDirectory.id == id_).first()

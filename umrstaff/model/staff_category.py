from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Text, Boolean

from umrstaff.model import DeclarativeBase, metadata, DBSession

class StaffCategory(DeclarativeBase):
    __tablename__ = 'staff_category'

    id = Column(Integer, primary_key=True)
    category = Column(Integer, ForeignKey('category.id'))
    staff = Column(Integer, ForeignKey('staff.id'))

    def add(self, staff_category):
        self.category = staff_category.category
        self.staff = staff_category.staff

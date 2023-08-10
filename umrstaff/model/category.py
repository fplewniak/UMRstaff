from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Text, Boolean

from umrstaff.model import DeclarativeBase, metadata, DBSession

class Category(DeclarativeBase):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(Text)

    def add(self, category):
        self.name = category.name

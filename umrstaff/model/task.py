from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Text

from umrstaff.model import DeclarativeBase, metadata, DBSession

class Task(DeclarativeBase):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    title = Column(Text)
    description = Column(Text)
    context = Column(Text)

    def add(self, task):
        self.title = task.title
        self.description = task.description
        self.context = task.context

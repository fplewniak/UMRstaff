from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Text

from umrstaff.model import DeclarativeBase, metadata, DBSession

class Workflow(DeclarativeBase):
    __tablename__ = 'workflow'

    id = Column(Integer, primary_key=True)
    process = Column(Integer, ForeignKey('task.id'), nullable=True, index=True)
    taskid = Column(Integer, ForeignKey('task.id'), nullable=True, index=True)
    requires = Column(Integer, ForeignKey('task.id'), nullable=True, index=True)

    def add(self, workflow):
        self.process = workflow.process
        self.taskid = workflow.taskid
        self.requires = workflow.requires

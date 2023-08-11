from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Text

from umrstaff.model import DeclarativeBase, metadata, DBSession

class ProcessStatus(DeclarativeBase):
    __tablename__ = 'process_status'

    id = Column(Integer, primary_key=True)
    process = Column(Integer, ForeignKey('task.id'), nullable=True, index=True)
    staff = Column(Integer, ForeignKey('staff.id'), nullable=True, index=True)
    task = Column(Integer, ForeignKey('task.id'), nullable=True, index=True)
    status = Column(Text)

    def add(self, process_status):
        self.process = process_status.process
        self.staff = process_status.staff
        self.task = process_status.task
        self.status = process_status.status

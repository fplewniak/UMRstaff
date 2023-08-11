from datetime import datetime

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Text

from umrstaff.model import DeclarativeBase, metadata, DBSession

class Position(DeclarativeBase):
    __tablename__ = 'position'

    id = Column(Integer, primary_key=True)
    supervisor = Column(Integer, ForeignKey('staff.id'), nullable=True, index=True)
    staff = Column(Integer, ForeignKey('staff.id'), nullable=True, index=True)
    from_date = Column(Date)
    to_date = Column(Date)
    status = Column(Text)
    org = Column(Text)
    reference = Column(Text)

    def add(self, position):
        self.supervisor = position.supervisor
        self.staff = position.staff
        self.from_date = datetime.strptime(str(position.from_date), '%d/%m/%Y').date()
        self.to_date = datetime.strptime(str(position.to_date), '%d/%m/%Y').date()
        self.status = position.status
        self.org = position.org
        self.reference = position.reference


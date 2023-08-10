from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Text

from umrstaff.model import DeclarativeBase, metadata, DBSession

class Contract(DeclarativeBase):
    __tablename__ = 'contract'

    id = Column(Integer, primary_key=True)
    supervisor = Column(Integer, ForeignKey('staff.id'), nullable=True, index=True)
    staff = Column(Integer, ForeignKey('staff.id'), nullable=True, index=True)
    from_date = Column(Date)
    to_date = Column(Date)
    poste = Column(Text)
    reference = Column(Text)

    def add(self, contract):
        self.supervisor = contract.supervisor
        self.staff = contract.staff
        self.from_date = contract.from_date
        self.to_date = contract.to_date
        self.poste = contract.poste
        self.reference = contract.reference

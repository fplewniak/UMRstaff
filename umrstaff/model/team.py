from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Text

from umrstaff.model import DeclarativeBase, metadata, DBSession

class Team(DeclarativeBase):
    __tablename__ = 'team'

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    rank = Column(Text)

    def add(self, team):
        self.name = team.name
        self.rank = team.rank

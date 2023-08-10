from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Text

from umrstaff.model import DeclarativeBase, metadata, DBSession

class TeamLeaders(DeclarativeBase):
    __tablename__ = 'team_leaders'

    id = Column(Integer, primary_key=True)
    leader = Column(Integer, ForeignKey('staff.id'), nullable=True, index=True)
    team = Column(Integer, ForeignKey('team.id'), nullable=True, index=True)

    def add(self, team_leader):
        self.leader = team_leader.leader
        self.team = team_leader.team

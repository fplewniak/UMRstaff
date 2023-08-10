from collections import namedtuple

import pandas
from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Text

from umrstaff.model import DeclarativeBase, metadata, DBSession

class TeamMembers(DeclarativeBase):
    __tablename__ = 'team_members'

    id = Column(Integer, primary_key=True)
    member = Column(Integer, ForeignKey('staff.id'), nullable=True, index=True)
    team = Column(Integer, ForeignKey('team.id'), nullable=True, index=True)

    def add(self, team_member):
        self.member = team_member.member
        self.team = team_member.team

    @staticmethod
    def namedtuple():
        return namedtuple('TeamMember', ['member', 'team'])

    @staticmethod
    def is_not_team_member(staff_id, team_id):
        links = int(pandas.read_sql_query(
            f'SELECT count(*) from team_members as tm where  tm.team = {team_id} and tm.member = {staff_id}',
            DBSession.connection()).iloc[0])
        return links == 0

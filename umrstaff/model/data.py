from collections import namedtuple
from datetime import datetime

import pandas
import transaction
from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Text

from umrstaff.model import DeclarativeBase, metadata, DBSession
from umrstaff.model.team import Team
from umrstaff.model.staff import Staff
from umrstaff.model.position import Position
from umrstaff.model.team_leaders import TeamLeaders
from umrstaff.model.team_members import TeamMembers
from umrstaff.model.phone_number import PhoneNumber
from umrstaff.model.phone_directory import PhoneDirectory
from umrstaff.model.mailinglist import MailingList
from umrstaff.model.mailing_list_directory import MailingListDirectory
from umrstaff import model


class TeamData():
    def __init__(self, team_id):
        self.id = team_id

    @property
    def name(self):
        query = DBSession.query(Team.name).filter(Team.id == self.id)
        return query.first()[0]

    @property
    def leader(self):
        leader = []
        query = (DBSession.query(Staff.id, Team, TeamMembers)
                 .join(Team, TeamMembers.team == Team.id)
                 .join(Staff, TeamMembers.member == Staff.id)
                 .filter(Team.id == self.id).filter(TeamMembers.is_leader == True))
        for staff_id, _, _ in query.all():
            leader.append(StaffData(staff_id))
        return leader

    @property
    def members(self):
        members = []
        query = (DBSession.query(Staff.id, Team, TeamMembers)
                 .join(Team, TeamMembers.team == Team.id)
                 .join(Staff, TeamMembers.member == Staff.id)).filter(Team.id == self.id)
        for staff_id, _, _ in query.all():
            members.append(StaffData(staff_id))
        return members

    def to_dict(self):
        return {'team_id': self.id,
                'team_name': self.name,
                'team_leader': self.leader,
                'team_members': self.members,
                }

class PositionData():
    def __init__(self, position_id):
        position = DBSession.query(Position).filter(Position.id == position_id).first()
        self.id = position.id
        self.supervisor = StaffData(position.supervisor)
        self.staff = position.staff
        self.from_date = position.from_date
        self.to_date = position.to_date
        self.status = position.status
        self.org = position.org
        self.reference = position.reference

class StaffData():
    def __init__(self, staff_id):
        staff = DBSession.query(Staff).filter(Staff.id == staff_id).first()
        self.id = staff.id
        (self.first_name, self.surname, self.email) = (staff.first_name, staff.surname, staff.email)
        (self.office, self.lab) = (staff.office, staff.lab)
        (self.office_tel, self.lab_tel, self.perso_tel) = (staff.office_tel, staff.lab_tel, staff.perso_tel)
        (self.emergency_contact, self.emergency_tel) = (staff.emergency_contact, staff.emergency_tel)
        self.user = staff.user

    @property
    def name(self):
        return ' '.join([self.first_name, self.surname])

    @property
    def teams(self):
        query = (DBSession.query(Team.id, TeamMembers.team)
                 .join(Team, TeamMembers.team == Team.id)
                 .filter(TeamMembers.member == self.id))
        teams = [TeamData(team_id) for team_id, _ in query.all()]
        return teams

    @property
    def mailing_lists(self):
        query = (DBSession.query(MailingList.id, MailingListDirectory.email)
                 .join(MailingList, MailingListDirectory.email == MailingList.id)
                 .filter(MailingListDirectory.staff == self.id))
        email_addresses = [MailingListData(email_id) for email_id, _ in query.all()]
        return email_addresses

    @property
    def position(self):
        query = (DBSession.query(Position).filter(Position.staff == self.id))
        return query.first()

    @property
    def supervisor(self):
        if self.position.supervisor is not None:
            return StaffData(self.position.supervisor)
        return None

    def to_dict(self):
        return {'staff_id': self.id,
                'first_name': self.first_name,
                'surname': self.surname,
                'full_name': ' '.join([self.first_name, self.surname]),
                'teams': self.teams,
                'position': self.position,
                'supervisor': self.supervisor,
                'office': self.office,
                'office_tel': self.office_tel,
                'lab': self.lab,
                'lab_tel': self.lab_tel,
                'perso_tel': self.perso_tel,
                'email': self.email,
                'mailing_lists': self.mailing_lists,
                'emergency_contact': self.emergency_contact,
                'emergency_tel': self.emergency_tel,
                'user': self.user,
                }

    def save(self, params):
        staff = model.DBSession.query(Staff).filter(Staff.id == self.id).first()
        staff.email = params['email']
        staff.office = params['office']
        staff.office_tel = params['office_tel']
        staff.lab = params['lab']
        staff.lab_tel = params['lab_tel']
        staff.perso_tel = params['perso_tel']
        staff.emergency_contact = params['emergency_contact']
        staff.emergency_tel = params['emergency_tel']

        self.position.status = params['status']
        self.position.org = params['org']
        self.position.supervisor = params['supervisor']
        self.position.from_date = datetime.strptime(params['from'], '%Y-%m-%d').date()
        self.position.to_date = datetime.strptime(params['to'], '%Y-%m-%d').date()
        self.position.reference = params['ref']

        for email in params['mailing_list'].split(','):
            if MailingList.exists(email):
                if MailingListDirectory.is_not_staff_email(self.id, MailingList.get_id(email)):
                    self.associate_email(email)
            elif email:
                self.add_email(email)

        MailingListDirectory.clean(self.id, [MailingList.get_id(email) for email in params['mailing_list'].split(',')])

        params['teams'] = [params['teams']] if isinstance(params['teams'], str) else params['teams']
        for team in model.DBSession.query(Team).all():
            if team.name in params['teams']:
                if TeamMembers.is_not_team_member(self.id, team.id):
                    db_team_member = model.TeamMembers()
                    TeamMember = model.TeamMembers.namedtuple()
                    db_team_member.add(TeamMember(self.id, team.id))
                    model.DBSession.add(db_team_member)
                    model.DBSession.flush()
            else:
                for tm in model.DBSession.query(TeamMembers).filter(TeamMembers.member == self.id).filter(
                        TeamMembers.team == team.id).all():
                    model.DBSession.delete(tm)


class MailingListData():
    def __init__(self, email_id):
        self.id = email_id

    @property
    def address(self):
        query = DBSession.query(MailingList.address).filter(MailingList.id == self.id)
        return query.first()[0]

    @property
    def description(self):
        query = DBSession.query(MailingList.description).filter(MailingList.id == self.id)
        return query.first()[0]

    @property
    def people(self):
        query = (DBSession.query(Staff.id, MailingListDirectory.staff)
                 .join(Staff, MailingListDirectory.staff == Staff.id)
                 .filter(MailingListDirectory.email == self.id))
        people = [StaffData(staff_id) for staff_id, _ in query.all()]
        return people

    def to_dict(self):
        return {'email_id': self.id,
                'address': self.address,
                'description': self.description,
                'people': self.people,
                }

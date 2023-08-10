from collections import namedtuple

import pandas
import transaction
from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Text

from umrstaff.model import DeclarativeBase, metadata, DBSession
from umrstaff.model.team import Team
from umrstaff.model.staff import Staff
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
        query = (DBSession.query(Staff.id, Team, TeamLeaders)
                 .join(Team, TeamLeaders.team == Team.id)
                 .join(Staff, TeamLeaders.leader == Staff.id)).filter(Team.id == self.id)
        for staff_id, _, _ in query.all():
            leader.append(StaffData(staff_id))
        return leader

    @property
    def members(self):
        leader = []
        query = (DBSession.query(Staff.id, Team, TeamMembers)
                 .join(Team, TeamMembers.team == Team.id)
                 .join(Staff, TeamMembers.member == Staff.id)).filter(Team.id == self.id)
        for staff_id, _, _ in query.all():
            leader.append(StaffData(staff_id))
        return leader

    def to_dict(self):
        return {'team_id': self.id,
                'team_name': self.name,
                'team_leader': self.leader,
                'team_members': self.members,
                }


class StaffData():
    def __init__(self, staff_id):
        query = DBSession.query(Staff.first_name, Staff.surname, Staff.email).filter(Staff.id == staff_id)
        self.id = staff_id
        (self.first_name, self.surname, self.email) = query.first()

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
    def phone_numbers(self):
        query = (DBSession.query(PhoneNumber.id, PhoneDirectory.phone_number)
                 .join(PhoneNumber, PhoneDirectory.phone_number == PhoneNumber.id)
                 .filter(PhoneDirectory.staff == self.id))
        phone_numbers = [PhoneNumberData(phone_id) for phone_id, _ in query.all()]
        return phone_numbers

    @property
    def mailing_lists(self):
        query = (DBSession.query(MailingList.id, MailingListDirectory.email)
                 .join(MailingList, MailingListDirectory.email == MailingList.id)
                 .filter(MailingListDirectory.staff == self.id))
        email_addresses = [MailingListData(email_id) for email_id, _ in query.all()]
        return email_addresses

    def to_dict(self):
        return {'staff_id': self.id,
                'first_name': self.first_name,
                'surname': self.surname,
                'full_name': ' '.join([self.first_name, self.surname]),
                'teams': self.teams,
                'tel': self.phone_numbers,
                'email': self.email,
                'mailing_lists': self.mailing_lists
                }

    def save(self, params):
        staff = model.DBSession.query(Staff).filter(Staff.id==self.id).first()
        staff.email = params['email']

        for email in params['mailing_list'].split(','):
            if MailingList.exists(email):
                if MailingListDirectory.is_not_staff_email(self.id, MailingList.get_id(email)):
                    self.associate_email(email)
            elif email:
                self.add_email(email)

        MailingListDirectory.clean(self.id, [MailingList.get_id(email) for email in params['mailing_list'].split(',')])

        number_ids = []
        for location in ['office', 'lab', 'perso']:
            for number in params[f'tel_{location}'].split(','):
                if PhoneNumber.exists(number):
                    if PhoneDirectory.is_not_staff_phone(self.id, PhoneNumber.get_id(number)):
                        self.associate_phone_number(number)
                elif number:
                    print(f'add {number}')
                    self.add_phone_number(number, location)
                number_ids.append(PhoneNumber.get_id(number))

        PhoneDirectory.clean(self.id, number_ids)

        params['teams'] = [params['teams']] if isinstance(params['teams'], str) else params['teams']
        print(params['teams'])
        for team in model.DBSession.query(Team).all():
            if team.name in params['teams']:
                if TeamMembers.is_not_team_member(self.id, team.id):
                    db_team_member = model.TeamMembers()
                    TeamMember = model.TeamMembers.namedtuple()
                    db_team_member.add(TeamMember(self.id, team.id))
                    model.DBSession.add(db_team_member)
                    model.DBSession.flush()
                else:
                    print('Do nothing')
            else:
                for tm in model.DBSession.query(TeamMembers).filter(TeamMembers.member==self.id).filter(TeamMembers.team==team.id).all():
                    model.DBSession.delete(tm)

    def add_email(self, address, mailing_list=0):
        db_email = model.MailingList()
        EmailTuple = model.MailingList.namedtuple()
        db_email.add(EmailTuple(address, mailing_list))
        model.DBSession.add(db_email)
        model.DBSession.flush()
        self.associate_email(address)

    def associate_email(self, address):
        email_id = MailingList.get_id(address)
        db_email = model.MailingListDirectory()
        EmailDirTuple = model.MailingListDirectory.namedtuple()
        db_email.add(EmailDirTuple(email_id, self.id))
        model.DBSession.add(db_email)
        model.DBSession.flush()

    def add_phone_number(self, number, location):
        db_phone = model.PhoneNumber()
        PhoneNumberTuple = model.PhoneNumber.namedtuple()
        db_phone.add(PhoneNumberTuple(number, location))
        model.DBSession.add(db_phone)
        model.DBSession.flush()
        self.associate_phone_number(number)

    def associate_phone_number(self, number):
        phone_id = PhoneNumber.get_id(number)
        db_phone = model.PhoneDirectory()
        PhoneDirTuple = model.PhoneDirectory.namedtuple()
        db_phone.add(PhoneDirTuple(phone_id, self.id))
        model.DBSession.add(db_phone)
        model.DBSession.flush()


class PhoneNumberData():
    def __init__(self, phone_id):
        self.id = phone_id

    @property
    def number(self):
        query = DBSession.query(PhoneNumber.number).filter(PhoneNumber.id == self.id)
        return query.first()[0]

    @property
    def location(self):
        query = DBSession.query(PhoneNumber.location).filter(PhoneNumber.id == self.id)
        return query.first()[0]

    @property
    def people(self):
        query = (DBSession.query(Staff.id, PhoneDirectory.staff)
                 .join(Staff, PhoneDirectory.staff == Staff.id)
                 .filter(PhoneDirectory.phone_number == self.id))
        people = [StaffData(staff_id) for staff_id, _ in query.all()]
        return people

    def to_dict(self):
        return {'phone_id': self.id,
                'number': self.number,
                'people': self.people,
                'location': self.location,
                }


class MailingListData():
    def __init__(self, email_id):
        self.id = email_id

    @property
    def address(self):
        query = DBSession.query(MailingList.address).filter(MailingList.id == self.id)
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
                'people': self.people,
                }

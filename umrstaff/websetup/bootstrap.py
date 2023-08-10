# -*- coding: utf-8 -*-
"""Setup the UMRstaff application"""
from __future__ import print_function, unicode_literals
import transaction
from umrstaff import model
import pandas


def bootstrap(command, conf, vars):
    """Place any commands to setup umrstaff here"""

    # <websetup.bootstrap.before.auth
    from sqlalchemy.exc import IntegrityError
    try:
        admin_user = model.User()
        admin_user.user_name = 'admin'
        admin_user.display_name = 'Main administrator'
        admin_user.email_address = 'f.plewniak@unistra.fr'
        admin_user.password = 'adminpass'
        model.DBSession.add(admin_user)

        admin_group = model.Group()
        admin_group.group_name = 'managers'
        admin_group.display_name = "Administrators' Group"
        admin_group.users.append(admin_user)
        model.DBSession.add(admin_group)

        edit_group = model.Group()
        edit_group.group_name = 'editors'
        edit_group.display_name = "Editors' Group"
        edit_group.users.append(admin_user)
        model.DBSession.add(edit_group)

        admin = model.Permission()
        admin.permission_name = 'admin'
        admin.description = 'This permission gives an administrative right'
        admin.groups.append(admin_group)

        adduser = model.Permission()
        adduser.permission_name = 'adduser'
        adduser.description = 'This permission grants the right to create new users'
        adduser.groups.append(admin_group)

        edit = model.Permission()
        edit.permission_name = 'edit'
        edit.description = 'This permission grants the right to create new users'
        edit.groups.append(edit_group)

        model.DBSession.add(admin)

        #### Permanent staff members
        print('Staff members')
        staff_members = pandas.read_csv('initial_data/staff.csv')
        for staff in staff_members.itertuples():
            db_staff = model.Staff()
            db_staff.add(staff)
            model.DBSession.add(db_staff)

        #### Teams
        print('Teams')
        teams = pandas.read_csv('initial_data/teams.csv')
        for team in teams.itertuples():
            db_team = model.Team()
            db_team.add(team)
            model.DBSession.add(db_team)

        #### Team leader table (allowing more than one leader for one team)
        print('Team leaders')
        team_leaders = pandas.read_csv('initial_data/team_leaders.csv')
        for team_leader in team_leaders.itertuples():
            db_team_leader = model.TeamLeaders()
            db_team_leader.add(team_leader)
            model.DBSession.add(db_team_leader)

        #### Team leader table (allowing more than one leader for one team)
        print('Team members')
        team_members = pandas.read_csv('initial_data/team_members.csv')
        for team_member in team_members.itertuples():
            db_team_members = model.TeamMembers()
            db_team_members.add(team_member)
            model.DBSession.add(db_team_members)

        #### E-mail table
        print('E-mail addresses')
        emails = pandas.read_csv('initial_data/mailing_lists.csv')
        for email in emails.itertuples():
            db_email = model.MailingList()
            db_email.add(email)
            model.DBSession.add(db_email)

        #### E-mail directory table
        print('E-mail directory')
        email_directory = pandas.read_csv('initial_data/mailing_list_directory.csv')
        for email in email_directory.itertuples():
            db_email = model.MailingListDirectory()
            db_email.add(email)
            model.DBSession.add(db_email)

        #### Phone table
        print('Phone numbers')
        phone_numbers = pandas.read_csv('initial_data/phone_number.csv')
        for phone_number in phone_numbers.itertuples():
            db_phone_number = model.PhoneNumber()
            db_phone_number.add(phone_number)
            model.DBSession.add(db_phone_number)

        #### Phone directory table
        print('Phone directory')
        phone_directory = pandas.read_csv('initial_data/phone_directory.csv')
        for phone_number in phone_directory.itertuples():
            db_phone_number = model.PhoneDirectory()
            db_phone_number.add(phone_number)
            model.DBSession.add(db_phone_number)

        #### Category table
        print('Categories')
        categories = pandas.read_csv('initial_data/category.csv')
        for category in categories.itertuples():
            db_category = model.Category()
            db_category.add(category)
            model.DBSession.add(db_category)

        #### Staff/Category table
        print('Staff category')
        categories = pandas.read_csv('initial_data/staff_category.csv')
        for category in categories.itertuples():
            db_category = model.StaffCategory()
            db_category.add(category)
            model.DBSession.add(db_category)


        model.DBSession.flush()
        transaction.commit()
    except IntegrityError:
        print('Warning, there was a problem adding your auth data, '
              'it may have already been added:')
        import traceback
        print(traceback.format_exc())
        transaction.abort()
        print('Continuing with bootstrapping...')

    # <websetup.bootstrap.after.auth>

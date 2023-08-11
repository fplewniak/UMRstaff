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
        admin_group = model.Group()
        admin_group.group_name = 'managers'
        admin_group.display_name = "Administrators' Group"
        model.DBSession.add(admin_group)

        edit_group = model.Group()
        edit_group.group_name = 'editors'
        edit_group.display_name = "Editors' Group"
        model.DBSession.add(edit_group)

        admin = model.Permission()
        admin.permission_name = 'admin'
        admin.description = 'This permission gives an administrative right'
        admin.groups.append(admin_group)
        model.DBSession.add(admin)

        adduser = model.Permission()
        adduser.permission_name = 'adduser'
        adduser.description = 'This permission grants the right to create new users'
        adduser.groups.append(admin_group)
        model.DBSession.add(adduser)

        edit = model.Permission()
        edit.permission_name = 'edit'
        edit.description = 'This permission grants the right to create new users'
        edit.groups.append(admin_group)
        edit.groups.append(edit_group)
        model.DBSession.add(edit)

        ### Users
        print('Users')
        users = pandas.read_csv('initial_data/users.csv')
        for user in users.itertuples():
            db_user = model.User()
            db_user.user_name = user.user_name
            db_user.display_name = user.display_name
            db_user.email_address = user.email_address
            db_user.password = user.password
            for group in [admin_group, edit_group]:
                if group.group_name in user.groups.split(','):
                    group.users.append(db_user)
            model.DBSession.add(db_user)

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

        #### Team members
        print('Team members')
        team_members = pandas.read_csv('initial_data/team_members.csv')
        for team_member in team_members.itertuples():
            db_team_members = model.TeamMembers()
            db_team_members.add(team_member)
            model.DBSession.add(db_team_members)

        #### Mailing lists
        print('Mailing lists')
        mailing_lists = pandas.read_csv('initial_data/mailing_lists.csv')
        for mailing_list in mailing_lists.itertuples():
            db_mailing_list = model.MailingList()
            db_mailing_list.add(mailing_list)
            model.DBSession.add(db_mailing_list)

        mailing_lists_dir = pandas.read_csv('initial_data/mailing_list_directory.csv')
        for mailing_list in mailing_lists_dir.itertuples():
            db_mailing_list = model.MailingListDirectory()
            db_mailing_list.add(mailing_list)
            model.DBSession.add(db_mailing_list)

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

# -*- coding: utf-8 -*-
"""Main Controller"""
import tg
from tg import expose, flash, require, url, lurl
from tg import request, redirect, tmpl_context
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.exceptions import HTTPFound
from tg import predicates
from umrstaff import model
from umrstaff.controllers.secure import SecureController
from umrstaff.model import DBSession
from tgext.admin.tgadminconfig import BootstrapTGAdminConfig as TGAdminConfig
from tgext.admin.controller import AdminController

from umrstaff.lib.base import BaseController
from umrstaff.controllers.error import ErrorController
from umrstaff.model.data import TeamData, StaffData, PhoneNumberData, MailingListData

from umrstaff.model.team import Team
from umrstaff.model.staff import Staff
from umrstaff.model.team_leaders import TeamLeaders
import re
from docutils.core import publish_parts

__all__ = ['RootController']

from tw2.core import Widget


class TextArea(Widget):
    params = ['rows', 'cols']
    rows = 10
    cols = 30


# class CommentFields(WidgetsList):
#     """The WidgetsList defines the fields of the form."""
#
#     name = forms.TextField(validator=validators.NotEmpty())
#     email = forms.TextField(validator=validators.MailingList(not_empty=True),
#       attrs={'size':30})
#     comment = forms.TextArea(validator=validators.NotEmpty())
#     notify = forms.CheckBox(label="Notify me")

class RootController(BaseController):
    """
    The root controller for the UMRstaff application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """
    secc = SecureController()
    admin = AdminController(model, DBSession, config_type=TGAdminConfig)

    error = ErrorController()

    def _before(self, *args, **kw):
        tmpl_context.project_name = "umrstaff"

    def _default(self):
        return self.teams()

    @expose('umrstaff.templates.teams')
    def teams(self):
        query = DBSession.query(Team)
        teams = {team.id: TeamData(team.id) for team in query.all()}
        return dict(teams=teams)

    @expose('umrstaff.templates.teams2')
    def teams2(self):
        query = (DBSession.query(Team.name, Staff.first_name, Staff.surname, TeamLeaders)
                 .join(Team, TeamLeaders.team == Team.id)
                 .join(Staff, TeamLeaders.leader == Staff.id))
        teams = {}
        for team, first_name, surname, _ in query.order_by(Team.name):
            if team in teams:
                teams[team].append(' '.join([first_name, surname]))
            else:
                teams[team] = [' '.join([first_name, surname])]
        for team, leaders in teams.items():
            teams[team] = ', '.join(leaders)
        return dict(teams=teams)

    @expose('umrstaff.templates.team_list')
    def team_list(self):
        teams = {team_id: team_name for team_id, team_name, _ in DBSession.query(Team.name, Staff.surname, TeamLeaders)
        .join(Team, TeamLeaders.team == Team.id).join(Staff, TeamLeaders.leader == Staff.id).order_by(Team.name)}
        return dict(teams=teams)

    @expose('umrstaff.templates.team')
    def team(self, team_id=1):
        return TeamData(team_id).to_dict()

    def can_edit(self):
        return tg.request.identity and 'edit' in tg.request.identity['permissions']

    def save_data(self, staff_id, params):
        print("Saving data", params)
        return StaffData(staff_id).save(params)

    @expose('umrstaff.templates.staff')
    def staff(self):
        staff = [StaffData(staff.id) for staff in DBSession.query(Staff).all()]
        return dict(staff=staff)

    @expose('umrstaff.templates.people')
    def people(self, staff_id=1, action='display'):
        data = StaffData(staff_id).to_dict()
        # data['params'] = tg.request.args_params
        print(tg.request.args_params)
        if len(tg.request.args_params) > 1 and self.can_edit():
            StaffData(staff_id).save(tg.request.args_params)
            # self.save_data(staff_id, tg.request.args_params)
            data = StaffData(staff_id).to_dict()
        if self.can_edit():
            data['editable'] = '1'
        else:
            data['editable'] = '0'
        return data

    @expose('umrstaff.templates.people_edit')
    @require(predicates.has_permission('edit', msg=l_('Only for the editors')))
    def people_edit(self, staff_id=1):
        if len(tg.request.args_params) > 1:
            redirect(f'/people/{staff_id}', params=tg.request.args_params)
        data = StaffData(staff_id).to_dict()
        team_names = [team.name for team in data['teams']]
        data['team_list'] = {team.name: (team.id, team.name in team_names) for team in DBSession.query(Team).all()}
        return data

    @expose('umrstaff.templates.phone_number')
    def phone_number(self, phone_id=1):
        return PhoneNumberData(phone_id).to_dict()

    @expose('umrstaff.templates.mailing_list')
    def mailing_list(self, email_id=1):
        return MailingListData(email_id).to_dict()

    @expose('umrstaff.templates.index')
    def index(self):
        """Handle the front-page."""
        return dict(page='index')

    @expose('umrstaff.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')

    @expose('umrstaff.templates.environ')
    def environ(self):
        """This method showcases TG's access to the wsgi environment."""
        return dict(page='environ', environment=request.environ)

    @expose('umrstaff.templates.data')
    @expose('json')
    def data(self, **kw):
        """
        This method showcases how you can use the same controller
        for a data page and a display page.
        """
        return dict(page='data', params=kw)

    @expose('umrstaff.templates.manager_stuff')
    @require(predicates.has_permission('admin', msg=l_('Only for managers')))
    def manage_permission_only(self, **kw):
        """Illustrate how a page for managers only works."""
        return dict(page='managers stuff')

    @expose('umrstaff.templates.index')
    @require(predicates.is_user('editor', msg=l_('Only for the editor')))
    def editor_user_only(self, **kw):
        """Illustrate how a page exclusive for the editor works."""
        return dict(page='editor stuff')

    @expose('umrstaff.templates.login')
    def login(self, came_from=lurl('/'), failure=None, login=''):
        """Start the user login."""
        if failure is not None:
            if failure == 'user-not-found':
                flash(_('User not found'), 'error')
            elif failure == 'invalid-password':
                flash(_('Invalid Password'), 'error')

        login_counter = request.environ.get('repoze.who.logins', 0)
        if failure is None and login_counter > 0:
            flash(_('Wrong credentials'), 'warning')

        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from, login=login)

    @expose()
    def post_login(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ.get('repoze.who.logins', 0) + 1
            redirect('/login',
                     params=dict(came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)

        # Do not use tg.redirect with tg.url as it will add the mountpoint
        # of the application twice.
        return HTTPFound(location=came_from)

    @expose()
    def post_logout(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('We hope to see you soon!'))
        return HTTPFound(location=came_from)

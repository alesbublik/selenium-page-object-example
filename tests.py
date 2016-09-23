import logging
from urlparse import urlparse, urljoin

from django.conf import settings
from django.test import LiveServerTestCase
from django.test.utils import override_settings
from django.contrib.auth import get_user_model
User = get_user_model()

from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException,\
    TimeoutException

from pp.base.tests import TestData
from pp.base.models import BU, Product, Release
from pp.people.models import Function

from .page import (MainPage, SideMenu, LoginPage, OverviewTab,
        DocumentsTab, PeopleTab, CommsTab, FavouritesMenu, Bugzilla,
        ScheduleLink, StatusTab, AdminStatusSubjectsPage, SecurityPage)


logger = logging.getLogger(__name__)


def get_firefox_profile():
    fp = webdriver.FirefoxProfile()
#    try:
#        fp.add_extension(extension='firebug.xpi')
#        # Avoid startup screen
#        fp.set_preference("extensions.firebug.currentVersion", "2.0.9")
#        fp.set_preference("extensions.firebug.console.enableSites", "true")
#        fp.set_preference("extensions.firebug.net.enableSites", "true")
#        fp.set_preference("extensions.firebug.script.enableSites", "true")
#        fp.set_preference("extensions.firebug.allPagesActivation", "on")
#    except Exception as e:
#        logger.info('Unable to load Firebug:\n%s' % e)

    fp.update_preferences()
    return fp

def get_firefox_proxy(host, port):
    from selenium.webdriver.common.proxy import Proxy, ProxyType

    proxydef = "{host}:{port}".format(host=host, port=port)

    proxy = Proxy({
        'proxyType': ProxyType.MANUAL,
        'httpProxy': proxydef,
        'ftpProxy': proxydef,
        'sslProxy': proxydef,
        'noProxy': '' # set this value as desired
        })

    return proxy



class FirefoxWebDriver(WebDriver):
    pass


class SeleniumTestCase(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        logger.info('Setup Driver')

        fp = get_firefox_profile()
        proxy_spec = get_firefox_proxy('127.0.0.1', 8080)
        cls.wd = FirefoxWebDriver(firefox_profile=fp, proxy=proxy_spec)
        #cls.wd = webdriver.Chrome()
        cls.wd.implicitly_wait(5) # seconds

        # check window size to run tests properly
        window_size = cls.wd.get_window_size()
        if window_size['height'] < 1024 or window_size['width'] < 1000:
            logger.error('Indicated small window size. Needed resize to run tests properly')
            cls.wd.set_window_size(height=1024, width=1000)
        super(SeleniumTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.wd.quit()
        super(SeleniumTestCase, cls).tearDownClass()

    def login(self, username, password):
        self.open(settings.LOGIN_URL)
        main_page = MainPage(self.wd)
        #assert main_page.title_matches(), "link does not exist"
        #main_page.click_login_link()
        login_page = LoginPage(self.wd)
        assert login_page.path_matches(), "login page does not exist"
        login_page.send_user_password(username, password)
        login_page.click_submit_login()

    def with_login_get(self, username, password, path):
        self.login(username, password)
        self.open(path)

    def go_to(self, model_object, section=None):
        base_url = model_object.get_pp_url()
        section = section and section or 'overview'
        path = urljoin(urlparse(base_url).path, section)
        self.with_login_get('admin', 'admin', path)

    def go_to_model(self, model, shortname, section=None):
        if type(shortname) == int:
            model_obj = model.objects.get(pk=shortname)
        else:
            model_obj = model.objects.get(shortname=shortname)

        self.go_to(model_obj, section)

    def go_to_bu(self, shortname, section=None):
        self.go_to_model(BU, shortname, section)

    def go_to_product(self, shortname, section):
        self.go_to_model(Product, shortname, section)

    def go_to_release(self, shortname, section):
        self.go_to_model(Release, shortname, section)

    def logout(self):
        self.open(settings.LOGOUT_URL)

    def open(self, path):
        self.wd.get("{url}{path}".format(url=self.live_server_url, path=path))

    # obsolete
    def wait_for_spin(self):
        try:
            waiter = WebDriverWait(self.wd, 1).until(lambda driver : driver.find_element(by=By.CLASS_NAME, value='icon-spin'))
            while waiter.is_displayed():
                self.wd.implicitly_wait(1)
                waiter = WebDriverWait(self.wd, 1).until(lambda driver : driver.find_element(by=By.CLASS_NAME, value='icon-spin'))
        except:
            return False
        return False


    def is_element_present(self, by_obj, what):
        try:
            self.wd.find_element(by=by_obj, value=what)
        except NoSuchElementException:
            return False
        return True

    def is_element_present_until(self, by_obj, what, timeout=0):
        try:
            waiter = WebDriverWait(self.wd, timeout).until(lambda driver : driver.find_element(by=by_obj, value=what))
            return waiter.is_displayed()
        except TimeoutException:
            return False

    def is_alert_present(self):
        try:
            self.wd.switch_to_alert()
        except NoAlertPresentException:
            return False
        return True

    def close_alert_and_get_value(self):
        try:
            alert = self.wd.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True


@override_settings(PP_FE_URL='http://127.0.0.1/')
class ProductTest(SeleniumTestCase):
    def setUp(self):
        User.objects.create_superuser(username='admin',
                                      password='admin',
                                      email='pp@pp.xx')
        td = TestData()
        self.rg = td.create_releasegroup_cloud_spec()
        self.release = self.rg.releases.all()[0]
        self.product = self.release.product
        self.bu = self.product.bu
        self.pp_model = self.release.product
        self.model_name = self.pp_model._meta.model_name

        self.function = Function.objects.create(name='func', email='func@example.com')
        self.function2 = Function.objects.create(name='func2', email='func2@example.com')

    def test_overview(self):
        self.go_to(self.pp_model, 'overview')
        tab = OverviewTab(self.wd)
        side_menu = SideMenu(self.wd)
        favourites_menu = FavouritesMenu(self.wd)

        if self.model_name == 'release':
            self.assertEqual([], favourites_menu.favourite_elements())
            favourites_menu.add()

            self.assertEqual(self.pp_model.shortname,
                    favourites_menu.favourite_elements()[0].data_shortname)


        if self.model_name != 'bu':
            # cancel/revive
            is_canceled = tab.toggle_cancel()
            is_canceled2 = tab.toggle_cancel()
            self.assertEqual(is_canceled, not is_canceled2)

        is_project = tab.toggle_project()
        model = self.pp_model._meta.model
        self.assertEqual(model.objects.get(pk=self.pp_model.pk).is_project, is_project)

        is_project = tab.toggle_project()
        self.assertEqual(model.objects.get(pk=self.pp_model.pk).is_project, is_project)

        if self.model_name not in ('bu',):
            res = tab.add_distribution_method('test')
            self.assertEqual(model.objects.get(pk=self.pp_model.pk).get_dist_methods(), res)
            res = tab.remove_distribution_method()
            self.assertEqual(None, res)

            res = tab.add_distribution_method('test edited')
            self.assertEqual(model.objects.get(pk=self.pp_model.pk).get_dist_methods(), res)
        tab.add_description('test')
        self.assertEqual(model.objects.get(pk=self.pp_model.pk).get_description(), tab.get_description())

        # edit name
        foobarproduct_name = 'FooBarProduct'
        self.assertTrue(foobarproduct_name != tab.name)

        tab.name = foobarproduct_name
        self.assertEqual(foobarproduct_name, tab.name)
        if self.model_name == 'product':
            self.assertTrue(foobarproduct_name in side_menu.product_element(foobarproduct_name).text)

        # edit shortname
        foobarproduct_shortname = 'xyz'
        tab.shortname = foobarproduct_shortname
        product_elements = "".join([e.text for e in side_menu.product_elements()])

        self.assertTrue(model.objects.get(pk=self.pp_model.pk).shortname in product_elements)

        if self.model_name == 'release':
            favourite_elements = "".join([e.data_shortname for e in favourites_menu.favourite_elements()])
            self.assertTrue(model.objects.get(pk=self.pp_model.pk).shortname in favourite_elements)

        # publish/unpublish
        publish_state = tab.is_published()
        is_published = tab.toggle_publish()
        self.assertEqual(not publish_state, is_published)

        self.logout()


    def test_edit_documents_sections(self):
        self.go_to(self.pp_model, 'docs')
        tab = DocumentsTab(self.wd)

        # create sections
        data = {'section-name': 'new section'}
        res = tab.create_section(data)
        self.assertTrue('_error_msg' not in res)

        sec1_id = tab.section_elements()[0].data_id

        data_sub = {'section-name': 'subsection'}
        res = tab.create_section(data_sub, parent=sec1_id)
        self.assertTrue('_error_msg' not in res)

        subsec_id = tab.section_elements(parent=sec1_id)[0].data_id

        # create documents
        data_doc = {'doc-name': 'test1',
                    'url': 'www.python.org'}
        res = tab.create_document(data_doc, parent=sec1_id)
        self.assertTrue('_error_msg' not in res)

        doc1_id = tab.document_elements()[0].data_id

        data_doc = {'doc-name': 'test2',
                    'url': 'www.python.org'}
        res = tab.create_document(data_doc, parent=subsec_id)
        self.assertTrue('_error_msg' not in res)

        doc2_id = [d for d in tab.document_elements() if d.data_id != doc1_id][0].data_id

        # edit subdocument
        data_doc = {'url': 'eee.python.org'}
        res_new = tab.edit_document(doc2_id, data_doc)
        self.assertTrue('_error_msg' not in res_new)

        self.assertEqual(tab.document_element(doc2_id).parent_id, subsec_id)

        # edit subsection
        data_subsec = {'section-name': 'subsubsection'}
        res = tab.create_section(data_subsec, parent=subsec_id)
        self.assertTrue('_error_msg' not in res)

        data_subsec['section-name'] = 'subsubsection edited'
        subsubsection = [e for e in tab.section_elements(parent=subsec_id)][0].data_id
        res = tab.edit_section(subsubsection, data_subsec)
        self.assertTrue('_error_msg' not in res)

        data_doc = {'doc-name': 'test3',
                    'url': 'www.cccc.org'}
        res = tab.create_document(data_doc, parent=subsubsection)
        self.assertTrue('_error_msg' not in res)

        # remove subsubsection with document
        tab.remove_section(subsubsection)
        self.assertEqual(0, len(tab.section_elements(parent=subsec_id)))

        # remove document
        tab.remove_document(doc2_id)
        self.assertEqual(0, len(tab.document_elements(parent=subsec_id)))

        # remove section
        tab.remove_section(sec1_id)
        self.assertEqual(0, len(tab.section_elements()))
        self.logout()

    def test_edit_sections(self):
        self.go_to(self.pp_model, 'docs')
        # create
        tab = DocumentsTab(self.wd)
        data = {'section-name': 'new section'}
        res = tab.create_section(data)
        self.assertTrue('_error_msg' not in res)
        sec1_id = tab.section_elements()[0].data_id

        data['section-name'] = 'section2'
        res = tab.create_section(data)
        self.assertTrue('_error_msg' not in res)
        sec2_id = [e for e in tab.section_elements() if e.data_id != sec1_id][0].data_id

        # edit
        data = {'section-name': 'edit section'}
        res = tab.edit_section(sec1_id, data)
        self.assertTrue('_error_msg' not in res)

        # remove
        tab.remove_section(sec1_id)
        tab.remove_section(sec2_id)

        self.assertEqual([], tab.section_elements())
        self.logout()

    def test_edit_documents(self):
        self.go_to(self.pp_model, 'docs')

        # create
        data = {'doc-name': 'test1',
                'url': 'www.python.org'}
        tab = DocumentsTab(self.wd)
        res = tab.create_document(data)
        self.assertTrue('_error_msg' not in res)
        doc1 = tab.document_elements()[0].data_id

        data['doc-name'] = 'test2'
        res = tab.create_document(data)
        self.assertTrue('_error_msg' not in res)

        doc2 = [e for e in tab.document_elements() if e.data_id != doc1][0].data_id

        # edit
        data['doc-name'] = 'edit test2'
        data['url'] = 'www.edited.org'
        res = tab.edit_document(doc2, data)
        self.assertTrue('_error_msg' not in res)

        # remove
        tab.remove_document(doc1)
        tab.remove_document(doc2)

        self.assertEqual([], tab.document_elements())
        self.logout()


    def test_edit_people(self):
        self.go_to(self.pp_model, 'people')

        # create
        tab = PeopleTab(self.wd)
        data = {'function': self.function.name,
                'description': 'new description',
                'user': 'pslama'}
        res = tab.create_person(data)
        self.assertTrue('_error_msg' not in res)

        pers1 = tab.person_elements()[0].data_id

        data['description'] = 'new descr 2'
        data['function'] = self.function2.name
        res = tab.create_person(data)
        self.assertTrue('_error_msg' not in res)

        pers2 = [e for e in tab.person_elements() if e.data_id != pers1][0].data_id

        # edit
        data['description'] = 'edit'
        data['user'] = 'pslama'
        res = tab.edit_person(pers1, data)
        self.assertTrue('_error_msg' not in res)

        # id changed after edit operation
        pers1 = [e for e in tab.person_elements() if e.data_id != pers2][0].data_id

        # remove
        tab.remove_person(pers1)
        tab.remove_person(pers2)
        self.assertEqual([], tab.person_elements())

        self.logout()

    def test_edit_comms_meeting(self):
        self.go_to(self.pp_model, 'comms')

        tab = CommsTab(self.wd)
        # create
        data = {'meeting-title': 'test title', 'day': 'Monday',
                'time': '10:00 am PT', 'duration': '1 hour weekly',
                'confcode': '315-064-8792', 'minutes_url': 'http://example.com',
                'info_url': 'http://example.com',
                'comment': 'foo bar baz\nUS CANADA'}
        res = tab.create_meeting(data)
        self.assertTrue('_error_msg' not in res)
        meet1 = tab.meeting_elements()[0].data_id

        data['meeting-title'] = 'bang'
        res = tab.create_meeting(data)
        self.assertTrue('_error_msg' not in res)
        meet2 = [e for e in tab.meeting_elements() if e.data_id != meet1][0].data_id

        # edit
        data['day'] = 'Friday'
        data['time'] = '7:00 am PT'
        data['minutes_url'] = 'http://shadowman.com'
        data['comment'] = 'aaaa'
        res = tab.edit_meeting(meet1, data)
        self.assertTrue('_error_msg' not in res)

        # remove
        tab.remove_meeting(meet1)
        tab.remove_meeting(meet2)

        self.assertEqual([], tab.meeting_elements())

        self.logout()

    def test_edit_comms_irc(self):
        self.go_to(self.pp_model, 'comms')

        tab = CommsTab(self.wd)
        # create
        data = {'irc_server': 'http://www.dfasdf.com',
                'irc_channel': 'foo',
                'irc_desc': 'bar'}
        res = tab.create_irc(data)
        self.assertTrue('_error_msg' not in res)

        irc1 = tab.irc_elements()[0].data_id

        data['irc_server'] = 'http://www.dfsdfasdfsd.com'
        data['irc_channel'] = 'bla'
        res = tab.create_irc(data)
        self.assertTrue('_error_msg' not in res)

        irc2 = [e for e in tab.irc_elements() if e.data_id != irc1][0].data_id

        # edit
        data['irc_server'] = 'http://edited.com'
        res = tab.edit_irc(irc1, data)
        self.assertTrue('_error_msg' not in res)

        # remove
        tab.remove_irc(irc1)
        tab.remove_irc(irc2)

        self.assertEqual([], tab.irc_elements())

        self.logout()


    def test_edit_comms_maillists(self):
        self.go_to(self.pp_model, 'comms')

        tab = CommsTab(self.wd)
        # create
        data = {'email': 'shadow@example.com',
                'email_desc': 'test'}
        res = tab.create_ml(data)
        self.assertTrue('_error_msg' not in res)

        mail1 = tab.ml_elements()[0].data_id

        data['email'] = 'shadow2@example.com'
        data['email_desc'] = 'test2'
        res = tab.create_ml(data)
        self.assertTrue('_error_msg' not in res)

        mail2 = [e for e in tab.ml_elements() if e.data_id != mail1][0].data_id

        # edit
        data['email'] = 'testedited@example.com'
        res = tab.edit_ml(mail1, data)
        self.assertTrue('_error_msg' not in res)

        # remove
        tab.remove_ml(mail1)
        tab.remove_ml(mail2)

        self.assertEqual([], tab.ml_elements())
        self.logout()








@override_settings(PP_FE_URL='http://127.0.0.1/')
class BusinessUnitTest(ProductTest):
    def setUp(self):
        super(BusinessUnitTest, self).setUp()
        self.pp_model = self.bu
        self.model_name = self.pp_model._meta.model_name


@override_settings(PP_FE_URL='http://127.0.0.1/')
class ReleaseTest(ProductTest):
    def setUp(self):
        super(ReleaseTest, self).setUp()
        self.pp_model = self.release
        self.model_name = self.pp_model._meta.model_name

    def test_bugzilla(self):
        self.go_to(self.pp_model, 'overview')
        tab = Bugzilla(self.wd)
        tab.remove_bugzilla()

        data = {'product': 'product text', 'version': 'version', 'nvr': 'nvr'}
        tab.create_bugzilla(data)
        self.assertTrue(data['product'] in tab.bugzilla_value())
        data = {'product': 'editedtext'}
        tab.edit_bugzilla(data)
        self.assertTrue(data['product'] in tab.bugzilla_value())


    def test_favourites(self):
        self.go_to(self.pp_model, 'overview')

        favourites_menu = FavouritesMenu(self.wd)

        self.assertEqual([], favourites_menu.favourite_elements())
        favourites_menu.add()

        self.assertEqual(1, len(favourites_menu.favourite_elements()))
        self.assertEqual(1, len([e for e in favourites_menu.favourite_elements() \
                if e.data_shortname == self.pp_model.shortname]))


        favourites_menu.remove(self.pp_model.shortname)

        self.assertEqual([], favourites_menu.favourite_elements())

    def test_schedule_link(self):
        self.go_to(self.pp_model, 'overview')

        schedule_link = ScheduleLink(self.wd)

        path = ('idm', 'cs-8-0-0', 'cs-8-0-0.tjx')
        schedule_link.create_link(path)
        self.assertTrue(path[-1] in schedule_link.schedule())

        schedule_link.remove_link()

        self.assertTrue(path[-1] not in schedule_link.schedule())


    def test_status_issues_edit(self):
        self.go_to(self.pp_model, 'statusrep')
        tab = StatusTab(self.wd)

        # create
        data = {'issue-text': 'test text'}
        res = tab.create_issue(data)
        self.assertTrue('_error_msg' not in res)

        issue1 = tab.issue_elements()[0].data_id

        # edit
        data = {'issue-text': 'edited text'}
        res = tab.edit_issue(issue1, data)
        self.assertTrue('_error_msg' not in res)

        # remove
        tab.remove_issue(issue1)
        self.assertEqual([], tab.issue_elements())



    def test_status_edit(self):
        from pp.statuses.models import Subject, STATUSES, STATUS_GREEN, STATUS_HOLD

        subject_eng = Subject.objects.create(name='Engineering', shortname='ENG')
        subject_fld = Subject.objects.create(name='Field', shortname='FLD')

        self.go_to(self.pp_model, 'statusrep')
        tab = StatusTab(self.wd)
        statuses = dict(STATUSES)

        # go to tab and create status
        data = {'status-title': 'text', 'cke_fulltext': 'description', 'status':
                statuses[STATUS_HOLD]}
        res = tab.create_status(subject_eng, data)
        self.assertTrue('_error_msg' not in res)

        elements = tab.status_elements()
        st1 = elements[0].data_id

        # edit status
        data_edit = {'status': statuses[STATUS_GREEN]}
        res_edit = tab.edit_status(st1, data_edit)
        self.assertTrue('_error_msg' not in res_edit)

        # remove
        tab.remove_status(st1)
        self.assertEqual([], tab.status_elements())


    def test_status_overview(self):
        from pp.statuses.models import Subject, STATUSES, STATUS_GREEN, STATUS_HOLD

        subject_eng = Subject.objects.create(name='Engineering', shortname='ENG')
        subject_fld = Subject.objects.create(name='Field', shortname='FLD')
        tab = StatusTab(self.wd)
        statuses = dict(STATUSES)

        self.go_to(self.pp_model, 'statusrep')
        # we have created 2 subjects that are signed as 'Not used' by default
        self.assertEqual(2, len(tab.status_elements()))

        # go to tab and create status
        data = {'status-title': 'text', 'cke_fulltext': 'description', 'status':
                statuses[STATUS_HOLD]}
        res = tab.create_status(subject_eng, data)
        self.assertTrue('_error_msg' not in res)

        # create second status
        data = {'status-title': 'text', 'cke_fulltext': 'description', 'status':
                statuses[STATUS_GREEN]}
        res = tab.create_status(subject_fld, data)
        self.assertTrue('_error_msg' not in res)

        # overview
        tab.go_to_overview()
        elements = [e.text for e in tab.status_elements()]
        self.assertEqual(2, len(elements))
        self.assertTrue(statuses[STATUS_GREEN] in " ".join(elements))
        self.assertTrue(statuses[STATUS_HOLD] in " ".join(elements))


    def test_status_rename(self):
        from pp.statuses.models import Subject

        subjects_path = '/super/status-subjects'
        eng = 'Engineering'
        Subject.objects.create(name=eng, shortname='ENG')

        tab = AdminStatusSubjectsPage(self.wd)

        self.with_login_get('admin', 'admin', subjects_path)
        ss_id = tab.status_subjects_elements()[0].data_id
        data = {'item-name': 'edited name'}

        res = tab.edit_status_subject(ss_id, data)
        self.assertTrue('_error_msg' not in res)

        status_tab = StatusTab(self.wd)

        self.go_to(self.pp_model, 'statusrep')
        self.assertTrue(status_tab.status_elements()[0].text.startswith(data['item-name']))

    def test_security(self):
        self.go_to(self.pp_model, 'security')

        tab = SecurityPage(self.wd)

        # add text
        cpe_text = 'cpe text'
        xml_text = 'hello xml editor'
        tab.cpe_input = cpe_text
        tab.add_editor_text(xml_text)

        self.assertEqual(cpe_text, tab.cpe_input)
        self.assertEqual(xml_text, tab.get_editor_text())

        # edit text
        cpe_text = 'red house'
        tab.cpe_input = cpe_text

        xml_text = 'second'
        tab.add_editor_text(xml_text)

        self.assertEqual(cpe_text, tab.cpe_input)
        self.assertEqual(xml_text, tab.get_editor_text())

        # remove text
        tab.remove_security_data()

        self.assertEqual("", tab.cpe_input)
        self.assertEqual("", tab.get_editor_text())

    def test_copy_security_data_from(self):
        cpe_text = 'cpe'
        xml_text = 'xml'
        Release.objects.create(product=self.product,
                name='security_release',
                shortname='sec_release',
                published=True,
                schedule='',
                security_xml=xml_text,
                cpe=cpe_text)

        self.go_to(self.pp_model, 'security')
        tab = SecurityPage(self.wd)
        tab.copy_security_data_from('sec_release')

        self.assertEqual(cpe_text, tab.cpe_input)
        self.assertEqual(xml_text, tab.get_editor_text())

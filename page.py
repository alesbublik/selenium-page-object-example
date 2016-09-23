from .elements import (BasePageElement, ToggleElement, EditPopupElement,
        DescriptionEditorElement, XMLEditorElement, EditFormElement, DataWrapper,
        is_alert_present, is_element_present, is_element_present_until,
        ajax_timeout)
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class BasePage(object):
    def __init__(self, driver):
        self.driver = driver


class MainPage(BasePage):
    LOGIN_LINK = (By.ID, 'login')

    def title_matches(self):
        return "Admin" in self.driver.title

    def click_login_link(self):
        element = self.driver.find_element(*self.LOGIN_LINK)
        element.click()


class TopMenu(BasePage):
    def __init__(self, driver):
        super(TopMenu, self).__init__(driver)
        self.menu_locator = (By.ID, 'menu-tree')
        if not self.menu_exists():
            raise NoSuchElementException

    def menu_exists(self):
        if is_element_present(self.driver, *self.menu_locator):
            return True
        return False

    @property
    def menu_element(self):
        return self.driver.find_element(*self.menu_locator)

    def group_elements(self):
        return self.menu_element.find_elements_by_css_selector('div.group')

    def group_element(self, name):
        groups = [g for g in self.group_elements() if g.find_element_by_css_selector('span').text == name]
        if groups:
            return groups[0]
        else:
            raise NoSuchElementException

    def unit_elements(self, group_name=None):
        if group_name:
            group_elem = self.group_element(group_name)
            units = group_elem.find_elements_by_css_selector('li.dropdown')
        else:
            units = self.menu_element.find_elements_by_css_selector('ul.nav')
        return units


class SideMenu(BasePage):
    def __init__(self, driver):
        super(SideMenu, self).__init__(driver)
        self.menu_locator = (By.ID, 'side-panel')
        if not self.menu_exists():
            raise NoSuchElementException

    def menu_exists(self):
        if is_element_present(self.driver, *self.menu_locator):
            return True
        return False

    @property
    def menu_element(self):
        return self.driver.find_element(*self.menu_locator)

    def product_element(self, name):
        products = [p for p in self.product_elements() if p.find_element_by_css_selector('li > a').text == name]
        if products:
            return products[0]
        else:
            raise NoSuchElementException

    def product_elements(self):
        return self.menu_element.find_elements_by_css_selector('ul.sortable > li')

    def product_releases(self, name):
        product_element = self.product_element(name)
        releases = [e for e in product_element.find_elements_by_css_selector('ul.sublist > li')]
        return releases


class FavouritesMenu(BasePage):
    menu_locator = (By.ID, 'favourites')
    add_locator = (By.CSS_SELECTOR, '#favourite-add a')
    remove_locator = ()

    @property
    def menu_element(self):
        if not is_element_present_until(self.driver, self.menu_locator,
                timeout=1):
            return None
        return self.driver.find_element(*self.menu_locator)

    def favourite_elements(self):
        return [FavouriteElement(e) for e in self.menu_element.find_elements_by_css_selector('li') if e.get_attribute('data-shortname')]

    def add(self):
        if is_element_present(self.driver, self.add_locator[0], self.add_locator[1]):
            self.driver.find_element(*self.add_locator).click()
            ajax_timeout(self.driver)
        else:
            raise NoSuchElementException

    def remove(self, shortname):
        self.menu_element.find_element_by_css_selector("li[data-shortname='{0}'] a.favourite-remove".format(shortname)).click()
        ajax_timeout(self.driver)


class LoginUsername(BasePageElement):
    USERNAME_INPUT = (By.ID, 'id_username')

    locator = USERNAME_INPUT


class LoginPassword(BasePageElement):
    PASSWORD_INPUT = (By.ID, 'id_password')

    locator = PASSWORD_INPUT


class LoginPage(BasePage):
    LOGIN_BUTTON   = (By.ID, 'user-login')

    username_field = LoginUsername()
    password_field = LoginPassword()

    def path_matches(self):
        return 'login' in self.driver.current_url

    def send_user_password(self, username, password):
        self.username_field = username
        self.password_field = password

    def click_submit_login(self):
        element = self.driver.find_element(*self.LOGIN_BUTTON)
        element.click()


class ProjectToggleButton(ToggleElement):
    PROJECT_TOGGLE = (By.ID, 'btnEditProject')
    PROJECT_TOGGLE_VALUE = (By.CSS_SELECTOR, '#project')

    locator = PROJECT_TOGGLE

    def toggle(self, driver):
        super(ProjectToggleButton, self).toggle(driver)
        selector = self.PROJECT_TOGGLE_VALUE
        return driver.find_element(*selector).text.split('\n')[0].lower().endswith('yes')


class PublishToggleButton(ToggleElement):
    PUBLISH_TOGGLE = (By.ID, 'btnPublish')
    PUBLISH_TOGGLE_VALUE = (By.ID, 'btnPublish')

    locator = PUBLISH_TOGGLE

    def is_published(self, driver):
        selector = self.PUBLISH_TOGGLE_VALUE
        return driver.find_element(*selector).text == 'Unpublish'


    def toggle(self, driver):
        super(PublishToggleButton, self).toggle(driver)
        if is_alert_present(driver):
            alert = driver.switch_to.alert
            alert.accept()

        return self.is_published(driver)



class DistributionEditor(EditPopupElement):
    DIST_METHODS_POPUP_ADD       = (By.ID, 'btnAddDistributions')
    DIST_METHODS_POPUP_EDIT      = (By.ID, 'btnEditDistributions')
    DIST_METHODS_POPUP_EDIT_AREA = (By.ID, 'edit-distributions')
    DIST_METHODS_POPUP_REMOVE    = (By.ID, 'btnDeleteDistributions')
    DIST_METHODS_POPUP_SUBMIT    = (By.ID, 'formEditDistributionsSubmit')
    DIST_METHODS_VALUE           = (By.CSS_SELECTOR, '#distributions pre')

    add_locator = DIST_METHODS_POPUP_ADD
    edit_locator = DIST_METHODS_POPUP_EDIT
    remove_locator = DIST_METHODS_POPUP_REMOVE
    text_area_locator = DIST_METHODS_POPUP_EDIT_AREA
    submit_locator = DIST_METHODS_POPUP_SUBMIT
    locator = DIST_METHODS_VALUE


class EditName(EditPopupElement):
    EDIT_NAME_BUTTON = (By.ID, 'btnEditName')
    EDIT_NAME_INPUT = (By.ID, 'item-edit-name')
    EDIT_NAME_SUBMIT = (By.ID, 'formEditNameSubmit')
    EDIT_NAME_VALUE = (By.ID, 'base-name')

    add_locator = EDIT_NAME_BUTTON
    edit_locator = EDIT_NAME_BUTTON
    text_area_locator = EDIT_NAME_INPUT
    submit_locator = EDIT_NAME_SUBMIT
    locator = EDIT_NAME_VALUE


class EditShortName(EditPopupElement):
    EDIT_SHORTNAME_BUTTON = (By.ID, 'btnEditShortname')
    EDIT_SHORTNAME_INPUT = (By.ID, 'item-edit-shortname')
    EDIT_SHORTNAME_SUBMIT = (By.ID, 'formEditShortnameSubmit')
    EDIT_SHORTNAME_VALUE = (By.ID, 'base-name')

    add_locator = EDIT_SHORTNAME_BUTTON
    edit_locator = EDIT_SHORTNAME_BUTTON
    text_area_locator = EDIT_SHORTNAME_INPUT
    submit_locator = EDIT_SHORTNAME_SUBMIT
    locator = EDIT_SHORTNAME_VALUE


class CancelReviveButton(object):
    CANCEL = (By.ID, 'btnCancel')
    REVIVE = (By.ID, 'btnRevive')

    def toggle(self, driver):
        driver.find_element_by_id('tab-admin').click()
        driver.execute_script("$('#tab-admin').addClass('open');")
        if is_element_present(driver, self.CANCEL[0], self.CANCEL[1]):
            elem = driver.find_element(*self.CANCEL).click()
        else:
            elem = driver.find_element(*self.REVIVE).click()
        if is_alert_present(driver):
            alert = driver.switch_to.alert
            alert.accept()

        return self.is_canceled(driver)

    def is_canceled(self, driver):
        driver.find_element_by_id('tab-admin').click()
        driver.execute_script("$('#tab-admin').addClass('open');")

        if is_element_present(driver, self.CANCEL[0], self.CANCEL[1]):
            return False

        return True


class DescriptionEditor(DescriptionEditorElement):
    DESC_ADD      = (By.ID, 'btnAddDescription')
    DESC_REMOVE   = (By.ID, 'btnDeleteDescription')
    DESC_EDIT     = (By.ID, 'btnEditDescription')
    DESC_SUBMIT   = (By.ID, 'formEditDescriptionSubmit')
    DESC_VALUE    = (By.CSS_SELECTOR, '#description span')

    editor = 'edit-description'
    add_locator = DESC_ADD
    edit_locator = DESC_EDIT
    remove_locator = DESC_REMOVE
    submit_locator = DESC_SUBMIT
    locator = DESC_VALUE


class BugzillaProductForm(EditFormElement):
    NEW_BZP_FORM = (By.ID, 'btnAddBz')
    NEW_BZP_FORM_SUBMIT = (By.ID, 'formEditBzSubmit')
    EDIT_BZP = (By.ID, 'btnEditBz')
    REMOVE_BZP = (By.ID, 'btnDeleteBz')
    BZP_VALUE = (By.ID, 'bz')

    fields = ('product', 'version', 'nvr')
    form_link_locator = NEW_BZP_FORM
    submit_locator = NEW_BZP_FORM_SUBMIT


class Bugzilla(BasePage):
    bugzilla_product = BugzillaProductForm()

    def path_matches(self):
        return self.driver.current_url.endswith('overview')

    def create_bugzilla(self, data):
        self.bugzilla_product.open(self.driver)
        self.bugzilla_product.fill_in(self.driver, data)
        data = self.bugzilla_product.submit(self.driver)
        return data

    def edit_bugzilla(self, data):
        self.bugzilla_product.open(self.driver, locator=self.bugzilla_product.EDIT_BZP)
        self.bugzilla_product.fill_in(self.driver, data)
        data = self.bugzilla_product.submit(self.driver)
        return data

    def remove_bugzilla(self):
        self.driver.find_element(*self.bugzilla_product.REMOVE_BZP).click()
        if is_alert_present(self.driver):
            alert = self.driver.switch_to.alert
            alert.accept()
        ajax_timeout(self.driver)

    def bugzilla_value(self):
        return self.driver.find_element(*self.bugzilla_product.BZP_VALUE).text


class ScheduleLinkForm(EditFormElement):
    NEW_SL_FORM = (By.ID, 'btnAddSchedule')
    EDIT_SL_FORM = (By.ID, 'btnEditSchedule')
    REMOVE_SL_FORM = (By.ID, 'btnDeleteSchedule')
    NEW_SL_SUBMIT = (By.ID, 'formEditScheduleSubmit')
    SL_VALUE = (By.ID, 'schedule')

    fields = []
    form_link_locator = NEW_SL_FORM
    submit_locator = NEW_SL_SUBMIT


class ScheduleLink(BasePage):
    schedule_link = ScheduleLinkForm()

    def path_matches(self):
        return self.driver.current_url.endswith('overview')

    def create_link(self, path):
        self.schedule_link.open(self.driver)
        for item in path:
            self.driver.find_element_by_link_text(item).click()

        self.driver.find_element(*self.schedule_link.submit_locator).click()
        while self.driver.find_element(*self.schedule_link.submit_locator).is_displayed():
            self.driver.implicitly_wait(1)
        return None


    def edit_link(self, path):
        self.schedule_link.open(self.driver, locator=self.schedule_link.EDIT_SL_FORM)
        for item in path:
            self.driver.find_element_by_link_text(item).click()

        self.schedule_link.submit(self.driver)
        return None

    def remove_link(self):
        self.driver.find_element(*self.schedule_link.REMOVE_SL_FORM).click()
        alert = self.driver.switch_to.alert
        alert.accept()
        ajax_timeout(self.driver)
        return None


    def schedule(self):
        if is_element_present_until(self.driver, self.schedule_link.SL_VALUE, 3):
            return self.driver.find_element(*self.schedule_link.SL_VALUE).text
        else:
            raise NoSuchElementException



class OverviewTab(BasePage):
    project_toggle = ProjectToggleButton()
    publish_toggle = PublishToggleButton()
    cancel_toggle = CancelReviveButton()
    distribution = DistributionEditor()
    description = DescriptionEditor()
    name = EditName()
    shortname = EditShortName()

    def path_matches(self):
        return self.driver.current_url.endswith('overview')

    def toggle_cancel(self):
        return self.cancel_toggle.toggle(self.driver)

    def is_canceled(self):
        return self.cancel_toggle.is_canceled(self.driver)

    def is_published(self):
        return self.publish_toggle.is_published(self.driver)

    def toggle_publish(self):
        return self.publish_toggle.toggle(self.driver)

    def toggle_project(self):
        return self.project_toggle.toggle(self.driver)

    def add_distribution_method(self, text):
        self.distribution = text
        return self.distribution

    def remove_distribution_method(self):
        selector = DistributionEditor.DIST_METHODS_POPUP_REMOVE
        element = self.driver.find_element(*selector)
        element.click()
        if is_alert_present(self.driver):
            alert = self.driver.switch_to.alert
            alert.accept()
        ajax_timeout(self.driver)
        return self.distribution

    def add_description(self, text):
        self.description.send_keys(self.driver, text)
        #return self.description.data(self.driver)

    def remove_description(self):
        selector = DescriptionEditor.DESC_REMOVE
        self.driver.find_element(*selector).click()
        if is_alert_present(self.driver):
            alert = self.driver.switch_to.alert
            alert.accept()
        return None

    def get_description(self):
        return self.description.data(self.driver)


class StatusForm(EditFormElement):
    STATUS_ADD = (By.ID, 'btnAddNewRow')

    fields = ('status-title', 'status', 'cke_fulltext')
    editor = 'fulltext'
    add_locator = STATUS_ADD
    form_link_locator = STATUS_ADD
    submit_locator = (By.ID, 'formAddNewRowSubmit')

    def execute(self, driver, method, *args):
        if is_element_present_until(driver, self.add_locator, timeout=0.5):
            element = driver.find_element(*self.add_locator)
        else:
            element = driver.find_element(*self.edit_locator)

        element.click()

        if len(args) > 0:
            arguments = "'{0}'".format("', '".join(args))
        else:
            arguments = ''
        script = "return CKEDITOR.instances['{0}'].{1}({2});".format(self.editor, method, arguments)

        result = driver.execute_script(script.format(script))
        ajax_timeout(driver)
        return result

    def clear(self, driver):
        return self.execute(driver, 'setData', '')

    def send_text(self, driver, value):
        return self.execute(driver, 'setData', value)

    def data(self, driver):
        return self.execute(driver, 'getData')


class IssueForm(EditFormElement):
    NEW_ISSUE_FORM = (By.ID, 'btnAddNewIssue')
    NEW_ISSUE_FORM_SUBMIT = (By.ID, 'formAddNewIssueSubmit')

    fields = ('issue-text',)
    form_link_locator = NEW_ISSUE_FORM
    submit_locator = NEW_ISSUE_FORM_SUBMIT


class StatusTab(BasePage):
    status = StatusForm()
    issue_form = IssueForm()

    def path_matches(self):
        return self.driver.current_url.endswith('statusrep#overview')

    def go_to_overview(self):
        from collections import namedtuple

        fake_sub = namedtuple('Subject', ['shortname'])._make(['overview'])
        self.go_to_subject(subject=fake_sub)

    def go_to_issues_risks(self):
        from collections import namedtuple

        fake_sub = namedtuple('Subject', ['shortname'])._make(['issues-risks'])
        self.go_to_subject(subject=fake_sub)

    def go_to_subject(self, subject):
        script = """$('#subject-tabs [href="#{0}"]').click()""".format(subject.shortname)
        self.driver.execute_script(script)

    def create_issue(self, data):
        self.go_to_issues_risks()
        self.issue_form.open(self.driver)
        self.issue_form.fill_in(self.driver, data)
        data = self.issue_form.submit(self.driver)
        return data

    def edit_issue(self, row_element, data):
        if type(row_element) in (int, str, unicode):
            row_element = self.issue_element(str(row_element))

        selector = (By.CLASS_NAME, 'btn-edit')
        self.issue_form.open(row_element, locator=selector)
        self.issue_form.fill_in(self.driver, data)
        data = self.issue_form.submit(self.driver)
        return data

    def create_status(self, subject, data):
        self.go_to_subject(subject)
        if data['cke_fulltext']:
            self.status.send_text(self.driver, data['cke_fulltext'])
        self.status.open(self.driver)
        self.status.fill_in(self.driver, data)
        data = self.status.submit(self.driver)
        return data

    def edit_status(self, row_element, data):
        if type(row_element) in (int, str, unicode):
            row_element = self.status_element(str(row_element))

        selector = (By.CLASS_NAME, 'btn-edit')
        self.status.open(row_element, locator=selector)
        self.status.fill_in(self.driver, data)
        data = self.status.submit(self.driver)
        return data

    def remove_status(self, row_element):
        if type(row_element) in (int, str, unicode):
            row_element = self.status_element(str(row_element))

        selector = 'button.btn-remove'
        row_element.find_element_by_css_selector(selector).click()
        alert = self.driver.switch_to.alert
        alert.accept()

    def remove_issue(self, row_element):
        if type(row_element) in (int, str, unicode):
            row_element = self.issue_element(str(row_element))

        selector = 'button.btn-remove'
        row_element.find_element_by_css_selector(selector).click()
        alert = self.driver.switch_to.alert
        alert.accept()


    def status_element(self, data_id):
        data_id = str(data_id)
        element = [e for e in self.status_elements() if e.data_id == data_id]
        if element:
            return element[0]
        else:
            raise NoSuchElementException

    def status_elements(self):
        selector = "div#status-rep tbody.statuses"
        row_list = []
        if is_element_present(self.driver, By.CSS_SELECTOR, selector):
            elem = self.driver.find_element_by_css_selector(selector)
            row_list = elem.find_elements(By.TAG_NAME, 'tr')

        data = [DataWrapper(r) for r in row_list]
        return data

    def issue_element(self, data_id):
        data_id = str(data_id)
        element = [e for e in self.issue_elements() if e.data_id == data_id]
        if element:
            return element[0]
        else:
            raise NoSuchElementException

    def issue_elements(self):
        selector = "div#status-rep tbody.issues"
        row_list = []
        if is_element_present(self.driver, By.CSS_SELECTOR, selector):
            elem = self.driver.find_element_by_css_selector(selector)
            row_list = elem.find_elements(By.TAG_NAME, 'tr')

        data = [DataWrapper(r) for r in row_list]
        return data


class DocumentForm(EditFormElement):
    NEW_DOCUMENT_FORM = (By.ID, 'btnAddNewDoc')
    NEW_DOCUMENT_FORM_SUBMIT = (By.ID, 'formAddNewDocumentSubmit')

    fields = ('doc-parent', 'doc-name', 'url')
    form_link_locator = NEW_DOCUMENT_FORM
    submit_locator = NEW_DOCUMENT_FORM_SUBMIT


class FavouriteElement(DataWrapper):
    @property
    def data_shortname(self):
        return self.get_attribute('data-shortname')


class DocumentElement(DataWrapper):
    @property
    def parent_id(self):
        return self.get_attribute('data-parent')


class SectionForm(EditFormElement):
    NEW_SECTION_FORM = (By.ID, 'btnAddNewSection')
    NEW_SECTION_FORM_SUBMIT = (By.ID, 'formAddNewSectionSubmit')

    fields = ('section-parent', 'section-name')
    form_link_locator = NEW_SECTION_FORM
    submit_locator = NEW_SECTION_FORM_SUBMIT


class SectionElement(DataWrapper):
    @property
    def parent_id(self):
        return self.get_attribute('data-parent')


class DocumentsTab(BasePage):
    document_form = DocumentForm()
    section_form = SectionForm()

    def path_matches(self):
        return self.driver.current_url.endswith('docs')

    def create_document(self, data_dict, parent=None):
        if type(parent) in (int, str, unicode):
            parent = self.section_element(str(parent))

        if parent is None:
            self.driver.find_element(By.CSS_SELECTOR, '#docs .btn').click()
            self.document_form.open(self.driver)
        else:
            parent.find_element_by_css_selector('.btn').click()
            locator = (By.CSS_SELECTOR, 'li > a.btn-add-doc')
            self.document_form.open(parent, locator=locator)

        self.document_form.fill_in(self.driver, data_dict)
        data = self.document_form.submit(self.driver)
        return data

    def edit_document(self, row_element, data):
        if type(row_element) in (int, str, unicode):
            row_element = self.document_element(str(row_element))

        selector = (By.CLASS_NAME, 'btn-edit-doc')
        self.document_form.open(row_element, locator=selector)
        self.document_form.fill_in(self.driver, data)
        data = self.document_form.submit(self.driver)
        return data

    def remove_document(self, row_element):
        if type(row_element) in (int, str, unicode):
            row_element = self.document_element(str(row_element))

        selector = 'button.btn-remove-doc'
        row_element.find_element_by_css_selector(selector).click()
        alert = self.driver.switch_to.alert
        alert.accept()
        ajax_timeout(self.driver)

    def document_element(self, data_id):
        data_id = str(data_id)
        element = [e for e in self.document_elements() if e.data_id == data_id]
        if element:
            return element[0]
        else:
            raise NoSuchElementException

    def document_elements(self, parent=None):
        selector = "div#docs > ul#documents"
        row_list = []

        # for parent as a int or str type find his element
        if type(parent) in (int, str, unicode):
            #parent = self.document_element(str(parent))
            parent = self.section_element(str(parent))

        if is_element_present(self.driver, By.CSS_SELECTOR, selector):
            if parent is None:
                elem = self.driver.find_element_by_css_selector(selector)
            else:
                elem = parent

            row_list = elem.find_elements_by_css_selector('li.tree-leaf')
        return [DocumentElement(r) for r in row_list]

    def create_section(self, data, parent=None):
        if type(parent) in (int, str, unicode):
            parent = self.section_element(str(parent))

        if parent is None:
            self.driver.find_element(By.CSS_SELECTOR, '#docs .btn').click()
            self.section_form.open(self.driver)
        else:
            parent.find_element_by_css_selector('.btn').click()
            locator = (By.CSS_SELECTOR, 'li > a.btn-add-section')
            self.section_form.open(parent, locator=locator)

        self.section_form.fill_in(self.driver, data)
        data = self.section_form.submit(self.driver)
        return data

    def edit_section(self, row_element, data):
        if type(row_element) in (int, str, unicode):
            row_element = self.section_element(str(row_element))

        selector = (By.CLASS_NAME, 'btn-edit-section')
        self.section_form.open(row_element, locator=selector)
        self.section_form.fill_in(self.driver, data)
        data = self.section_form.submit(self.driver)
        return data

    def remove_section(self, row_element):
        if type(row_element) in (int, str, unicode):
            row_element = self.section_element(str(row_element))

        selector = 'button.btn-remove-section'
        row_element.find_element_by_css_selector(selector).click()
        alert = self.driver.switch_to.alert
        alert.accept()
        ajax_timeout(self.driver)

    def section_element(self, data_id):
        data_id = str(data_id)
        element = [e for e in self.section_elements() if e.data_id == data_id]
        if element:
            return element[0]
        else:
            raise NoSuchElementException

    def section_elements(self, parent=None):
        selector = "div#docs > ul#documents"
        row_list = []
        # for parent as a int or str type find his element
        if type(parent) in (int, str, unicode):
            parent = self.section_element(str(parent))

        if is_element_present(self.driver, By.CSS_SELECTOR, selector):
            if parent is None:
                elem = self.driver.find_element_by_css_selector(selector)
            else:
                elem = parent

            row_list = elem.find_elements_by_css_selector('li.tree-branch')
        return [SectionElement(r) for r in row_list]


class PersonForm(EditFormElement):
    NEW_PERSON_FORM = (By.ID, 'btnAddNewRow')
    NEW_PERSON_FORM_SUBMIT = (By.ID, 'formAddNewRowSubmit')

    fields = ('function', 'description', 'user')
    form_link_locator = NEW_PERSON_FORM
    submit_locator = NEW_PERSON_FORM_SUBMIT



class PeopleTab(BasePage):
    person_form = PersonForm()

    def path_matches(self):
        return self.driver.current_url.endswith('people')

    def create_person(self, data):
        self.person_form.open(self.driver)
        self.person_form.fill_in(self.driver, data)
        data = self.person_form.submit(self.driver)
        return data

    def edit_person(self, row_element, data):
        if type(row_element) in (int, str, unicode):
            row_element = self.person_element(str(row_element))

        selector = (By.CLASS_NAME, 'btn-edit')
        self.person_form.open(row_element, locator=selector)
        self.person_form.fill_in(self.driver, data)
        data = self.person_form.submit(self.driver)
        return data

    def remove_person(self, row_element):
        if type(row_element) in (int, str, unicode):
            row_element = self.person_element(str(row_element))

        selector = 'button.btn-remove'
        row_element.find_element_by_css_selector(selector).click()
        alert = self.driver.switch_to.alert
        alert.accept()
        ajax_timeout(self.driver)

    def person_element(self, data_id):
        element = [e for e in self.person_elements() if e.data_id == str(data_id)]
        if element:
            return element[0]
        else:
            raise NoSuchElementException

    def person_elements(self):
        selector = "div#people-tree table > tbody"
        row_list = []
        if is_element_present(self.driver, By.CSS_SELECTOR, selector):
            elem = self.driver.find_element_by_css_selector(selector)
            row_list = elem.find_elements(By.TAG_NAME, 'tr')

        return [DataWrapper(r) for r in row_list if r.get_attribute("data-id") != None]


class MeetingForm(EditFormElement):
    NEW_MEETING_FORM = [(By.CSS_SELECTOR, '#comms .btn'), (By.ID, 'btnAddMeeting')]
    NEW_MEETING_FORM_SUBMIT = (By.ID, 'formAddNewRowMtgSubmit')

    fields = ('meeting-title', 'day', 'time', 'duration', 'confcode',
              'minutes_url', 'info_url', 'comment')
    form_link_locator = NEW_MEETING_FORM
    submit_locator = NEW_MEETING_FORM_SUBMIT


class IRCForm(EditFormElement):
    NEW_IRC_FORM = [(By.CSS_SELECTOR, '#comms .btn'), (By.ID, 'btnAddIRC')]
    NEW_IRC_FORM_SUBMIT = (By.ID, 'formAddNewRowIRCSubmit')

    fields = ('irc_server', 'irc_channel', 'irc_desc')
    form_link_locator = NEW_IRC_FORM
    submit_locator = NEW_IRC_FORM_SUBMIT


class MailListForm(EditFormElement):
    NEW_MAILLIST_FORM = [(By.CSS_SELECTOR, '#comms .btn'), (By.ID, 'btnAddEmail')]
    NEW_MAILLIST_FORM_SUBMIT = (By.ID, 'formAddNewRowMLSubmit')

    fields = ('email', 'email_desc', 'archive', 'type')
    form_link_locator = NEW_MAILLIST_FORM
    submit_locator = NEW_MAILLIST_FORM_SUBMIT


class CommsTab(BasePage):
    meeting_form = MeetingForm()
    irc_form = IRCForm()
    maillist_form = MailListForm()

    def path_matches(self):
        return self.driver.current_url.endswith('comms')

    def create_meeting(self, data):
        self.meeting_form.open(self.driver)
        self.meeting_form.fill_in(self.driver, data)
        data = self.meeting_form.submit(self.driver)
        return data

    def edit_meeting(self, row_element, data):
        if type(row_element) in (int, str, unicode):
            row_element = self.meeting_element(str(row_element))

        selector = (By.CLASS_NAME, 'btn-edit')
        self.meeting_form.open(row_element, locator=selector)
        self.meeting_form.fill_in(self.driver, data)
        data = self.meeting_form.submit(self.driver)
        return data

    def remove_meeting(self, row_element):
        if type(row_element) in (int, str, unicode):
            row_element = self.meeting_element(str(row_element))

        selector = 'button.btn-delete'
        row_element.find_element_by_css_selector(selector).click()
        alert = self.driver.switch_to.alert
        alert.accept()
        ajax_timeout(self.driver)

    def meeting_element(self, data_id):
        element = [e for e in self.meeting_elements() if e.data_id == data_id]
        if element:
            return element[0]
        else:
            raise NoSuchElementException

    def meeting_elements(self):
        selector = "div#comms > ul#meetings"
        row_list = []
        if is_element_present(self.driver, By.CSS_SELECTOR, selector):
            elem = self.driver.find_element_by_css_selector(selector)
            row_list = elem.find_elements(By.TAG_NAME, 'li')

        return [DataWrapper(r) for r in row_list if r.get_attribute("data-id") != None]

    def create_irc(self, data):
        self.irc_form.open(self.driver)
        self.irc_form.fill_in(self.driver, data)
        data = self.irc_form.submit(self.driver)
        return data

    def edit_irc(self, row_element, data):
        if type(row_element) in (int, str, unicode):
            row_element = self.irc_element(str(row_element))

        selector = (By.CLASS_NAME, 'btn-edit')
        self.irc_form.open(row_element, locator=selector)
        self.irc_form.fill_in(self.driver, data)
        data = self.irc_form.submit(self.driver)
        return data

    def remove_irc(self, row_element):
        if type(row_element) in (int, str, unicode):
            row_element = self.irc_element(str(row_element))

        selector = 'button.btn-delete'
        row_element.find_element_by_css_selector(selector).click()
        alert = self.driver.switch_to.alert
        alert.accept()
        ajax_timeout(self.driver)


    def irc_element(self, data_id):
        element = [e for e in self.irc_elements() if e.data_id == data_id]
        if element:
            return element[0]
        else:
            raise NoSuchElementException

    def irc_elements(self):
        selector = "div#comms > ul#ircs"
        row_list = []
        if is_element_present(self.driver, By.CSS_SELECTOR, selector):
            elem = self.driver.find_element_by_css_selector(selector)
            row_list = elem.find_elements(By.TAG_NAME, 'li')

        return [DataWrapper(r) for r in row_list if r.get_attribute("data-id") != None]


    def create_ml(self, data):
        self.maillist_form.open(self.driver)
        self.maillist_form.fill_in(self.driver, data)
        data = self.maillist_form.submit(self.driver)
        return data

    def edit_ml(self, row_element, data):
        if type(row_element) in (int, str, unicode):
            row_element = self.ml_element(str(row_element))

        selector = (By.CLASS_NAME, 'btn-edit')
        self.maillist_form.open(row_element, locator=selector)
        self.maillist_form.fill_in(self.driver, data)
        data = self.maillist_form.submit(self.driver)
        return data

    def remove_ml(self, row_element):
        if type(row_element) in (int, str, unicode):
            row_element = self.ml_element(str(row_element))

        selector = 'button.btn-delete'
        row_element.find_element_by_css_selector(selector).click()
        alert = self.driver.switch_to.alert
        alert.accept()
        ajax_timeout(self.driver)

    def ml_element(self, data_id):
        element = [e for e in self.ml_elements() if e.data_id == data_id]
        if element:
            return element[0]
        else:
            raise NoSuchElementException

    def ml_elements(self):
        selector = "div#comms > ul#emails"
        row_list = []
        if is_element_present(self.driver, By.CSS_SELECTOR, selector):
            elem = self.driver.find_element_by_css_selector(selector)
            row_list = elem.find_elements(By.TAG_NAME, 'li')

        return [DataWrapper(r) for r in row_list if r.get_attribute("data-id") != None]


class BusinessGroupForm(EditFormElement):
    NEW_BG_FORM = (By.ID, 'btnAddNewGroup')
    NEW_BG_FORM_SUBMIT = (By.ID, 'formAddNewBUGrpSubmit')

    fields = ('bugrp-name', 'bugrp-shortname', 'bugrp-owner')
    form_link_locator = NEW_BG_FORM
    submit_locator = NEW_BG_FORM_SUBMIT


class BusinessUnitForm(EditFormElement):
    NEW_BU_FORM = (By.ID, 'btnAddNewBU')
    NEW_BU_FORM_SUBMIT = (By.ID, 'formAddNewBUSubmit')

    fields = ('item-bu-group', 'item-name', 'item-shortname', 'item-description')
    form_link_locator = NEW_BU_FORM
    submit_locator = NEW_BU_FORM_SUBMIT


class BusinessUnitElement(DataWrapper):
    @property
    def parent_id(self):
        return self.get_attribute('data-parent')


class AdminBUsPage(BasePage):
    business_group_form = BusinessGroupForm()
    business_unit_form = BusinessUnitForm()


    def get_element(self, element_id):
        if type(element_id) in (int, str, unicode):
            row_element = self.business_unit_element(str(element_id))
        else:
            row_element = element_id
        return row_element

    def path_matches(self):
        return self.driver.current_url.endswith('/manage-bus/')

    def create_business_unit(self, data_dict, parent=None):
        if type(parent) in (int, str, unicode):
            parent = self.business_group_element(str(parent))
        if parent is None:
            self.business_unit_form.open(self.driver)
        else:
            locator = (By.CSS_SELECTOR, 'span.admin-links button.btn-add-unit')
            self.business_unit_form.open(parent, locator=locator)

        self.business_unit_form.fill_in(self.driver, data_dict)
        data = self.business_unit_form.submit(self.driver)
        return data

    def edit_business_unit(self, element_id, data):
        row_element = self.get_element(element_id)
        selector = (By.CLASS_NAME, 'btn-edit-unit')
        self.business_unit_form.open(row_element, locator=selector)
        self.business_unit_form.fill_in(self.driver, data)
        data = self.business_unit_form.submit(self.driver)
        return data

    def business_unit_element(self, data_id):
        element = [e for e in self.business_unit_elements() if e.data_id == data_id]
        if element:
            return element[0]
        else:
            raise NoSuchElementException

    def business_unit_elements(self, parent=None):
        selector = "ul#bus-tree"
        row_list = []

        if type(parent) in (int, str, unicode):
            parent = self.business_group_element(str(parent))

        if is_element_present(self.driver, By.CSS_SELECTOR, selector):
            if parent is None:
                elem = self.driver.find_element_by_css_selector(selector)
            else:
                elem = parent

            row_list = elem.find_elements(By.CLASS_NAME, 'tree-leaf')

        return [BusinessUnitElement(r) for r in row_list if r.get_attribute('data-id') != None]

    def remove_business_unit(self, element_id):
        row_element = self.get_element(element_id)
        selector = 'button.btn-remove-unit'
        row_element.find_element_by_css_selector(selector).click()
        alert = self.driver.switch_to.alert
        alert.accept()
        ajax_timeout(self.driver)

    def create_business_group(self, data_dict):
        self.business_group_form.open(self.driver)
        self.business_group_form.fill_in(self.driver, data_dict)
        data = self.business_group_form.submit(self.driver)
        return data

    def edit_business_group(self, row_element, data):
        if type(row_element) in (int, str, unicode):
            row_element = self.business_group_element(str(row_element))

        selector = (By.CLASS_NAME, 'btn-edit-group')
        self.business_group_form.open(row_element, locator=selector)
        self.business_group_form.fill_in(self.driver, data)
        data =  self.business_group_form.submit(self.driver)
        return data

    def business_group_element(self, data_id):
        element = [e for e in self.business_group_elements() if e.data_id == data_id]
        if element:
            return element[0]
        else:
            raise NoSuchElementException

    def business_group_elements(self):
        selector = "ul#bus-tree"
        row_list = []
        if is_element_present(self.driver, By.CSS_SELECTOR, selector):
            elem = self.driver.find_element_by_css_selector(selector)
            row_list = elem.find_elements(By.CLASS_NAME, 'tree-branch')

        return [DataWrapper(r) for r in row_list if r.get_attribute('data-id') != None]

    def remove_business_group(self, row_element):
        if type(row_element) in (int, str, unicode):
            row_element = self.business_group_element(str(row_element))

        selector = 'button.btn-remove-group'
        row_element.find_element_by_css_selector(selector).click()
        alert = self.driver.switch_to.alert
        alert.accept()


class StatusSubjectForm(EditFormElement):
    NEW_SB_FORM = (By.ID, 'btnAddNewRow')
    NEW_SB_FORM_SUBMIT = (By.ID, 'formAddNewRowSubmit')

    fields = ('item-name', 'item-shortname')
    form_link_locator = NEW_SB_FORM
    submit_locator = NEW_SB_FORM_SUBMIT


class StatusSubjectToggleButton(ToggleElement):
    HIDE_SHOW_TOGGLE = (By.CSS_SELECTOR, 'button.btn-toggle')
    HIDE_SHOW_TOGGLE_VALUE = (By.CSS_SELECTOR, 'button.btn-toggle')

    locator = HIDE_SHOW_TOGGLE


class AdminStatusSubjectsPage(BasePage):
    status_toggle = StatusSubjectToggleButton()
    status_subjects_form = StatusSubjectForm()

    def path_matches(self):
        return self.driver.current_url.endswith('/status_subjects/')

    def get_element(self, element_id):
        if type(element_id) in (int, str, unicode):
            row_element = self.status_subjects_element(str(element_id))
        else:
            row_element = element_id
        return row_element

    def status_subjects_element(self, data_id):
        element = [e for e in self.status_subjects_elements() if e.data_id == data_id]
        if element:
            return element[0]
        else:
            raise NoSuchElementException

    def status_subjects_elements(self):
        selector = "div#items-tree"
        row_list = []
        if is_element_present(self.driver, By.CSS_SELECTOR, selector):
            elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            row_list = elem.find_elements(By.TAG_NAME, 'li')

        return [DataWrapper(r) for r in row_list if r.get_attribute('data-id') != None]

    def create_status_subject(self, data_dict):
        self.status_subjects_form.open(self.driver)
        self.status_subjects_form.fill_in(self.driver, data_dict)
        data = self.status_subjects_form.submit(self.driver)
        return data

    def edit_status_subject(self, row_element, data):
        row_element = self.get_element(row_element)
        selector = (By.CLASS_NAME, 'btn-edit')
        self.status_subjects_form.open(row_element, locator=selector)
        self.status_subjects_form.fill_in(self.driver, data)
        data = self.status_subjects_form.submit(self.driver)
        return data

    def remove_status_subject(self, row_element):
        selector = 'button.btn-delete'
        self.get_element(row_element).find_element_by_css_selector(selector).click()
        while not is_alert_present(self.driver):
            is_element_present_until(self.driver, (By.ID, 'fake_element'), 5)

        alert = self.driver.switch_to.alert
        alert.accept()
        is_element_present_until(self.driver, (By.ID, 'fake_element'), 5)

    def toggle_status_subject(self, element_id):
        """
        Hide or show status subject
        """
        row_element = self.get_element(element_id)
        self.status_toggle.toggle(row_element)
        selector = self.status_toggle.HIDE_SHOW_TOGGLE_VALUE
        # it takes more time so we will slower test
        is_element_present_until(self.driver, (By.ID, 'fake_element'), 5)
        return self.get_element(element_id).find_element(*selector).text.lower()


class AdminPersonForm(EditFormElement):
    NEW_PEOPLE_FORM = (By.ID, 'btnAddNewRow')
    NEW_PEOPLE_FORM_SUBMIT = (By.ID, 'formAddNewRowSubmit')

    fields = ('id_username', 'id_first_name', 'id_last_name', 'id_email', 'id_url', 'id_phone')
    form_link_locator = NEW_PEOPLE_FORM
    submit_locator = NEW_PEOPLE_FORM_SUBMIT


class AdminPeopleManagementPage(BasePage):
    person_form = AdminPersonForm()

    def path_matches(self):
        return self.driver.current_url.endswith('persons')

    def get_element(self, element_id):
        if type(element_id) in (int, str, unicode):
            row_element = self.admin_person_element(str(element_id))
        else:
            row_element = element_id
        return row_element

    def create_admin_person(self, data_dict):
        self.person_form.open(self.driver)
        self.person_form.fill_in(self.driver, data_dict)
        data = self.person_form.submit(self.driver)
        return data


    def admin_person_elements(self):
        selector = "div#items-tree > ul"
        row_list = []
        if is_element_present(self.driver, By.CSS_SELECTOR, selector):
            elem = self.driver.find_element_by_css_selector(selector)
            row_list = elem.find_elements(By.TAG_NAME, 'li')

        return [DataWrapper(r) for r in row_list if r.get_attribute('data-id') != None]

    def admin_person_element(self, data_id):
        element = [e for e in self.admin_person_elements() if e.data_id == data_id]
        if element:
            return element[0]
        else:
            raise NoSuchElementException

    def edit_admin_person(self, row_element, data):
        row_element = self.get_element(row_element)
        selector = (By.CLASS_NAME, 'btn-edit')
        self.person_form.open(row_element, locator=selector)
        self.person_form.fill_in(self.driver, data)
        data = self.person_form.submit(self.driver)
        return data

    def remove_admin_person(self, element_id):
        row_element = self.get_element(element_id)
        selector = 'button.btn-delete'
        row_element.find_element_by_css_selector(selector).click()
        alert = self.driver.switch_to.alert
        alert.accept()
        ajax_timeout(self.driver)


class AdminDescriptionForm(EditFormElement):
    NEW_DESCRIPTION_FORM = (By.ID, 'btnAddNewRow')
    NEW_DESCRIPTION_FORM_SUBMIT = (By.ID, 'formAddNewRowSubmit')

    fields = ('id_name',)
    form_link_locator = NEW_DESCRIPTION_FORM
    submit_locator = NEW_DESCRIPTION_FORM_SUBMIT


class AdminPeopleDescriptionManagementPage(BasePage):
    description_form = AdminDescriptionForm()

    def path_matches(self):
        return self.driver.current_url.endswith('descriptions')

    def get_element(self, element_id):
        if type(element_id) in (int, str, unicode):
            row_element = self.admin_description_element(str(element_id))
        else:
            row_element = element_id
        return row_element

    def create_admin_description(self, data_dict):
        self.description_form.open(self.driver)
        self.description_form.fill_in(self.driver, data_dict)
        data = self.description_form.submit(self.driver)
        return data

    def admin_description_elements(self):
        selector = "div#items-tree > ul"
        row_list = []
        if is_element_present(self.driver, By.CSS_SELECTOR, selector):
            elem = self.driver.find_element_by_css_selector(selector)
            row_list = elem.find_elements(By.TAG_NAME, 'li')

        return [DataWrapper(r) for r in row_list if r.get_attribute('data-id') != None]

    def admin_description_element(self, data_id):
        element = [e for e in self.admin_description_elements() if e.data_id == data_id]
        if element:
            return element[0]
        else:
            raise NoSuchElementException

    def edit_admin_description(self, row_element, data):
        row_element = self.get_element(row_element)
        selector = (By.CLASS_NAME, 'btn-edit')
        self.description_form.open(row_element, locator=selector)
        self.description_form.fill_in(self.driver, data)
        data = self.description_form.submit(self.driver)
        return data

    def remove_admin_description(self, element_id):
        row_element = self.get_element(element_id)
        selector = 'button.btn-delete'
        row_element.find_element_by_css_selector(selector).click()
        alert = self.driver.switch_to.alert
        alert.accept()
        ajax_timeout(self.driver)


class AdminFunctionForm(EditFormElement):
    NEW_FUNCTION_FORM = (By.ID, 'btnAddNewRow')
    NEW_FUNCTION_FORM_SUBMIT = (By.ID, 'formAddNewRowSubmit')

    fields = ('id_name', 'id_required')
    form_link_locator = NEW_FUNCTION_FORM
    submit_locator = NEW_FUNCTION_FORM_SUBMIT


class AdminPeopleFunctionManagementPage(BasePage):
    function_form = AdminFunctionForm()

    def path_matches(self):
        return self.driver.current_url.endswith('fuctions')

    def get_element(self, element_id):
        if type(element_id) in (int, str, unicode):
            row_element = self.admin_function_element(str(element_id))
        else:
            row_element = element_id
        return row_element

    def create_admin_function(self, data_dict):
        self.function_form.open(self.driver)
        self.function_form.fill_in(self.driver, data_dict)
        data = self.function_form.submit(self.driver)
        return data

    def admin_function_elements(self):
        selector = "div#items-tree > ul"
        row_list = []
        if is_element_present(self.driver, By.CSS_SELECTOR, selector):
            elem = self.driver.find_element_by_css_selector(selector)
            row_list = elem.find_elements(By.TAG_NAME, 'li')

        return [DataWrapper(r) for r in row_list if r.get_attribute('data-id') != None]

    def admin_function_element(self, data_id):
        element = [e for e in self.admin_function_elements() if e.data_id == data_id]
        if element:
            return element[0]
        else:
            raise NoSuchElementException

    def edit_admin_function(self, row_element, data):
        row_element = self.get_element(row_element)
        selector = (By.CLASS_NAME, 'btn-edit')
        self.function_form.open(row_element, locator=selector)
        self.function_form.fill_in(self.driver, data)
        data = self.function_form.submit(self.driver)
        return data

    def remove_admin_function(self, element_id):
        row_element = self.get_element(element_id)
        selector = 'button.btn-delete'
        row_element.find_element_by_css_selector(selector).click()
        alert = self.driver.switch_to.alert
        alert.accept()
        ajax_timeout(self.driver)


class CPEInput(BasePageElement):
    CPE_INPUT = (By.ID, 'cpe')

    locator = CPE_INPUT


class XMLEditor(XMLEditorElement):
    EDITOR_INPUT = (By.CSS_SELECTOR, '#xml-editor div.ace_content')
    REMOVE_BTN = (By.ID, 'btnRemove')
    EDITOR_VALUE = EDITOR_INPUT
    UPDATE_BTN = (By.ID, 'btnUpdate')

    locator = EDITOR_INPUT

    edit_locator = EDITOR_INPUT
    remove_locator = REMOVE_BTN
    submit_locator = UPDATE_BTN
    locator = EDITOR_INPUT


class CopySecurityForm(EditFormElement):
    COPY_SECURITY_FORM = (By.ID, 'btnCopy')
    SUBMIT_BTN = (By.ID, 'formCopySecuritySubmit')

    fields = ('copy-object',)
    form_link_locator = COPY_SECURITY_FORM
    submit_locator = SUBMIT_BTN


class SecurityPage(BasePage):
    UPDATE_BUTTON = (By.ID, 'btnUpdate')
    REMOVE_BUTTON = (By.ID, 'btnRemove')

    copy_security_form = CopySecurityForm()
    xml_editor = XMLEditor()
    cpe_input = CPEInput()

    def path_matches(self):
        return 'security' in self.driver.current_url

    def add_editor_text(self, text):
        self.xml_editor.send_keys(self.driver, text)

    def clear_editor(self):
        self.xml_editor.clear(self.driver)

    def get_editor_text(self):
        return self.xml_editor.data(self.driver)

    def click_update_data(self):
        element = self.driver.find_element(*self.UPDATE_BUTTON)
        element.click()
        ajax_timeout(self.driver)

    def remove_security_data(self):
        self.driver.find_element(*self.REMOVE_BUTTON).click()
        if is_alert_present(self.driver):
            alert = self.driver.switch_to.alert
            alert.accept()
        ajax_timeout(self.driver)

    def copy_security_data_from(self, copy_object):
        self.copy_security_form.open(self.driver)
        data = {'copy-object': copy_object}
        self.copy_security_form.fill_in(self.driver, data)
        data = self.copy_security_form.submit(self.driver)
        ajax_timeout(self.driver, timeout=5)
        return data


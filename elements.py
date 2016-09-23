import logging

from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.common.exceptions import NoAlertPresentException, NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)


def is_element_present(driver, by_obj, what):
    try:
        driver.find_element(by=by_obj, value=what)
    except NoSuchElementException:
        return False
    return True

def ajax_complete(driver):
    try:
        return 0 == driver.execute_script("return jQuery.active")
    except WebDriverException:
        pass


def ajax_timeout(driver, timeout=1):
    #wait for ajax items to load
    WebDriverWait(driver, timeout).until(
             ajax_complete,  "Timeout waiting for page to load")


def is_element_present_until(driver, locator, timeout=0):
    try:
        WebDriverWait(driver, timeout).until(lambda dr: dr.find_element(by=locator[0], value=locator[1]))
    except TimeoutException:
        return False

    return True

def is_alert_present(driver):
    try:
        driver.switch_to.alert
    except NoAlertPresentException:
        return False
    return True


class BasePageElement(object):
    def __set__(self, obj, value):
        driver = obj.driver
        if not is_element_present_until(driver, self.locator, timeout=1):
            raise NoSuchElementException

        driver.find_element(*self.locator).clear()
        driver.find_element(*self.locator).send_keys(value)

    def __get__(self, obj, owner):
        driver = obj.driver
        if not is_element_present_until(driver, self.locator, timeout=1):
            raise NoSuchElementException

        element = driver.find_element(*self.locator)
        return element.get_attribute("value")


class ToggleElement(object):
    def toggle(self, driver):
        if not isinstance(self.locator, list):
            locators = [self.locator]
        else:
            locators = self.locator

        for loc in locators:
            if is_element_present_until(driver, loc, timeout=3):
                element = driver.find_element(*loc)
            else:
                raise NoSuchElementException
            element.click()


class EditPopupElement(object):
    def __set__(self, obj, value):
        driver = obj.driver
        if is_element_present_until(driver, self.add_locator, timeout=0.5):
            element = driver.find_element(*self.add_locator)
        else:
            element = driver.find_element(*self.edit_locator)
        element.click()
        driver.find_element(*self.text_area_locator).clear()
        driver.find_element(*self.text_area_locator).send_keys(value)
        driver.find_element(*self.submit_locator).click()
        ajax_timeout(driver)

    def __get__(self, obj, owner):
        driver = obj.driver
        if is_element_present_until(driver, self.locator, timeout=1):
            return driver.find_element(*self.locator).text
        return None


class DescriptionEditorElement(object):
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
        driver.find_element(*self.submit_locator).click()
        ajax_timeout(driver)
        return result

    def clear(self, driver):
        return self.execute(driver, 'setData', '')

    def send_keys(self, driver, value):
        return self.execute(driver, 'setData', value)

    def data(self, driver):
        return self.execute(driver, 'getData')


class XMLEditorElement(object):
    def execute(self, driver, method, *args):
        if is_element_present_until(driver, self.edit_locator, timeout=0.5):
            element = driver.find_element(*self.edit_locator)

        element.click()

        if len(args) > 0:
            arguments = "'{0}'".format("', '".join(args))
        else:
            arguments = ''
        script = "return window.xml_editor.{0}({1})".format(method, arguments)

        result = driver.execute_script(script)
        if method in ('setValue',):
            driver.find_element(*self.submit_locator).click()
            ajax_timeout(driver)
        return result

    def clear(self, driver):
        return self.execute(driver, 'setValue', '')

    def send_keys(self, driver, text):
        return self.execute(driver, 'setValue', text)

    def data(self, driver):
        return self.execute(driver, 'getValue')


class EditFormElement(object):
    """
    In inherited class define these attributes:
        fields = (,)
        form_link_locator = (By.ID, 'locator')
        submit_locator = (By.ID, 'locator')
    """

    def open(self, driver, locator=None):
        self.data = None
        locator = locator and locator or self.form_link_locator
        if not isinstance(locator, list):
            locators = [locator]
        else:
            locators = locator

        for loc in locators:
            if is_element_present_until(driver, loc, timeout=0.5):
                element = driver.find_element(*loc)
            else:
                raise NoSuchElementException
            element.click()

    def fill_in(self, driver, values):
        fields_to_fill = set(self.fields).intersection(set(values.keys()))
        if not fields_to_fill:
            logger.error(fields_to_fill)
            raise NoSuchElementException

        for field in fields_to_fill:
            field_element = driver.find_element(By.ID, field)
            try:
                field_element.clear()
            except WebDriverException as e:
                logger.warning(e.msg)
            if field_element.tag_name in ('input', 'textarea'):
                if field_element.get_attribute('type') == 'checkbox':
                    if field_element.is_selected() != values[field]:
                        field_element.click()
                else:
                    field_element.click()
                    field_element.send_keys(values[field])
            elif field_element.tag_name == 'select':
                self.select_field(field_element, values[field])


    def select_field(self, element, value):
        select = Select(element)
        options = [o for o in select.options if o.text == value]
        if not options:
            raise NoSuchElementException

        select.select_by_visible_text(value)

    def form_values(self, driver):
        form_values = {}
        for field in self.fields:
            field_element = driver.find_element(By.ID, field)
            form_values[field] = field_element.get_attribute("value")
        return form_values

    def submit(self, driver):
        error_element = (By.CSS_SELECTOR, '.input-error')
        submit_btn = driver.find_element(*self.submit_locator)
        self.data = self.form_values(driver)
        submit_btn.click()
        ajax_timeout(driver)
        if is_element_present_until(driver, error_element):
            error_msg = []
            element = driver.find_element(*error_element)
            element_id = element.get_attribute('id')
            element_msg = driver.find_element(By.CSS_SELECTOR, '.tooltip-inner').text
            element_value = element.get_attribute('value')
            error_msg.append({element_id: {element_msg: element_value}})
            return {'_error_msg': error_msg}
        return self.data


class DataWrapper(object):
    def __init__(self, obj):
        self._obj = obj

    def __getattr__(self, attr):
        func = getattr(self.__dict__['_obj'], attr)
        if callable(func):
            def wrapper_func(*args, **kwargs):
                ret = func(*args, **kwargs)
                return ret
            return wrapper_func
        else:
            return func

    @property
    def data_id(self):
        return self.get_attribute('data-id')



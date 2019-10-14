from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile


class SeleniumWrapper:

    def __init__(self, driver_config):
        options = Options()
        options.headless = driver_config['driver_headless']
        profile = FirefoxProfile(driver_config['fire_fox_profile_path'])
        self.__driver = webdriver.Firefox(
            executable_path=driver_config['fire_fox_driver_path'], firefox_profile=profile, options=options)

    def open_website(self, url):
        self.__driver.get(url=url)

    def get_element_with_wait(self, locator, wait=10):
        return WebDriverWait(self.__driver, wait).until(
            expected_conditions.presence_of_element_located(locator=locator))

    def wait_till_clickable(self, locator, wait=10):
        return WebDriverWait(self.__driver, wait).until(expected_conditions.element_to_be_clickable(locator=locator))

    def get_element(self, locator):
        (identifier, value) = locator
        return self.__driver.find_element(by=identifier, value=value)

    def switch_to_active_element(self):
        return self.__driver.switch_to.active_element

    def execute_script(self, script, element):
        self.__driver.execute_script(script, element)

    def get_driver_instance(self):
        return self.__driver

    def close_connection(self):
        self.__driver.quit()

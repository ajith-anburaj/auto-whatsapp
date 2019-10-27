from time import sleep

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import whatsapp.Constants as Constants
import whatsapp.config as config
from common.helper import is_valid_phone_number
from .SeleniumWrapper import SeleniumWrapper
from common.logger import logger


class WhatsApp:
    def __init__(self, driver_config):
        self.selenium = SeleniumWrapper(driver_config)

    def open_whats_app_web(self):
        self.selenium.open_website(config.WEB_WHATS_APP_URL)

    def is_logged_in(self):
        identifiers = ['//img[@alt="Scan me!"]', '//input[@name="rememberMe"]']
        self.open_whats_app_web()
        for identifier in identifiers:
            try:
                self.selenium.get_element_with_wait((By.XPATH, identifier))
            except TimeoutException:
                return True
        else:
            return False

    def __get_message_page_element(self):
        chat_icon = self.selenium.wait_till_clickable((By.XPATH, '//div[@title="New chat"]'))
        ActionChains(self.selenium.get_driver_instance()).move_to_element(chat_icon).click().perform()
        return self.selenium.get_element((By.XPATH, '//input[@title="Search contacts"]'))

    def __traverse_contacts_list(self):
        contacts = []
        is_contacts_available = True
        while is_contacts_available:
            contact_element = self.selenium.switch_to_active_element()
            contacts.append(contact_element.text.split("\n")[0])
            contact_element.send_keys(Keys.ARROW_DOWN)
            if contact_element == self.selenium.switch_to_active_element():
                is_contacts_available = False
        return contacts

    def __saved_contacts(self):
        search_contacts_div = self.__get_message_page_element()
        search_contacts_div.click()
        search_contacts_div.send_keys(Keys.ARROW_DOWN)
        return self.__traverse_contacts_list()

    def __chat_contacts(self):
        body = self.selenium.get_element_with_wait(
            (By.XPATH, '//input[@title="Search or start new chat"]')
        )
        body.send_keys(Keys.ARROW_DOWN)
        return self.__traverse_contacts_list()

    def contacts(self):
        saved_contacts = self.__saved_contacts()
        chat_contacts = set(self.__chat_contacts())
        groups = []
        for contact in list(chat_contacts):
            if contact not in saved_contacts:
                if not is_valid_phone_number(contact.replace(" ", "")):
                    chat_contacts.remove(contact)
                    groups.append(contact)
            else:
                chat_contacts.remove(contact)
        return {
            "saved_contacts": sorted(saved_contacts),
            "unsaved_contacts": sorted(chat_contacts),
            "possible_groups": sorted(groups),
        }

    def __select_contact(self, contact):
        search_contacts_div = self.__get_message_page_element()
        search_contacts_div.clear()
        search_contacts_div.send_keys(contact)
        sleep(1)
        search_contacts_div.send_keys(Keys.ARROW_DOWN)
        while True:
            contact_element = self.selenium.switch_to_active_element()
            contact_name = contact_element.text.split("\n")[0]
            if contact_name == contact:
                contact_element.send_keys(Keys.ENTER)
                return True
            contact_element.send_keys(Keys.ARROW_DOWN)
            if contact_element == self.selenium.switch_to_active_element():
                return False

    def __select_file_upload(self):
        attachment_element = self.selenium.get_element((By.XPATH, '//span[@data-icon="clip"]'))
        attachment_element.click()

    def __handle_text_message(self, message):
        message_input_element = self.selenium.get_element(
            (By.XPATH, '//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')
        )
        message_input_element.send_keys(message + Keys.ENTER)

    def __handle_media_message(self, message):
        self.__select_file_upload()
        message = "\n".join(message)
        media_attachment = self.selenium.get_element(
            (By.XPATH, "//header[1]//ul/li[1]//input")
        )
        media_attachment.send_keys(message)
        self.selenium.get_element_with_wait(
            (By.XPATH, '//span[@data-icon="send-light"]')
        ).click()

    def __handle_file_messages(self, message):
        self.__select_file_upload()
        message = "\n".join(message)
        file_attachment = self.selenium.get_element(
            (By.XPATH, "//header[1]//ul/li[3]//input")
        )
        file_attachment.send_keys(message)
        self.selenium.get_element_with_wait(
            (By.XPATH, '//span[@data-icon="send-light"]')
        ).click()

    def __go_to_main_window(self):
        try:
            back_button_element = self.selenium.get_element(
                (By.XPATH, '//span[@data-icon="back-light"]')
            )
            self.selenium.get_driver_instance().execute_script(
                "arguments[0].click();", back_button_element
            )
        except NoSuchElementException:
            logger.debug("Already in main window")

    def send_message(self, contact, message, message_type):
        self.__go_to_main_window()
        message_to_handler = {
            Constants.TEXT: self.__handle_text_message,
            Constants.MEDIA: self.__handle_media_message,
            Constants.FILE: self.__handle_file_messages,
        }
        if self.__select_contact(contact):
            if message_type in message_to_handler:
                message_to_handler[message_type](message)
                return True
            else:
                logger.error("Invalid message type")
                return False
        else:
            logger.error("Contact not found")
            return False

    def close_whats_app(self):
        self.selenium.close_connection()

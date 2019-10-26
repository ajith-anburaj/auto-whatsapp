from time import sleep

from whatsapp.WhatsApp import WhatsApp
import whatsapp.Constants as Constants
import config

driver_config = {
    'binary_location': config.binary_location,
    'fire_fox_driver_path': config.fire_fox_driver_path,
    'driver_headless': config.driver_headless,
    'fire_fox_profile_path': config.fire_fox_profile_path
}


def log_in():
    driver_config_head = driver_config
    driver_config['driver_headless'] = False
    client_login = WhatsApp(driver_config=driver_config_head)
    client_login.open_whats_app_web()
    sleep(5)
    if client_login.is_logged_in():
        print('Login Successful')
        client_login.close_whats_app()
        return True
    else:
        print('Login unsuccessful')
        client_login.close_whats_app()
        return False


def interact_with_whats_app():
    client_headless = WhatsApp(driver_config)
    client_headless.open_whats_app_web()
    print(client_headless.send_message('Veera Mani', 'Testing ignore', Constants.TEXT))
    client_headless.close_whats_app()


if __name__ == '__main__':
    client = WhatsApp(driver_config)
    is_logged_in = client.is_logged_in()
    client.close_whats_app()
    if is_logged_in:
        interact_with_whats_app()
    else:
        interact_with_whats_app() if log_in() else print('Please try again later')

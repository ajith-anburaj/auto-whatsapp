# auto-whatsapp
Programmatically send WhatsApp messages

Prerequisites:
1. Python
2. Mozila Firefox

To Get started, clone the repo and do the following steps.

In config.py file,
1. Point the binary_location to your local firefox.exe.
2. Point the fire_fox_driver_path to geckodriver.exe if you are on windows & geckodriver if you are on mac.
3. Point the fire_fox_profile_path to profiles folder in firefox 
(To get the profiles folder, open firefox and type about:support). Troubleshooting information page will get opened. In that page, there will be the path of profiles folder.

After changing these steps, run pip3 install -r requirements.txt

once all the dependencies are successfully downloaded,

add contact name and message in interact_with_whats_app(), client_headless.send_message('CONTACT NAME','MESSAGE',CONSTANTS.TEXT)

now run python main.py to see the result.

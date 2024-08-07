import os
import logging

# Check if folder exists and create one if not.
def check_folder(folder_name):
    logging.debug(f'Checking if {folder_name} directory exists')
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
        logging.info(f'Creating {folder_name} directory')


### Break and send error signal then exit when error happened to help quick debug.
def break_and_signal(error_message):
    logging.error(error_message)
    exit(1)


def get_base_path():
    return os.path.dirname(os.path.abspath(__file__))


def get_file_path(file_name):
    return os.path.join(get_base_path(), file_name)


def get_present_path():
    return os.getcwd()

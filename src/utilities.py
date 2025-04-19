import os
import logging
import glob

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


def delete_files_in_directory(directory: str):
    """Delete all files in the specified directory."""
    try:
        files = glob.glob(os.path.join(directory, '*'))
        for f in files:
            os.remove(f)
        logging.info(f"All files in {directory} have been deleted.")
    except Exception as e:
        logging.error(f"Error deleting files in {directory}: {e}")

# Remove the highest and lowest values from a list and return the average of the remaining values.
def remove_high_low_average(values):
    if len(values) <= 2:
        raise ValueError("List must contain more than two elements to remove high and low values.")
    
    sorted_values = sorted(values)
    trimmed_values = sorted_values[1:-1]  # Remove the first and last elements
    average = sum(trimmed_values) / len(trimmed_values)
    
    return average
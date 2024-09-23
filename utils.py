# check if file already exist before writing to csv and xlsx
import os

def check_file_exists(file_path):
    return os.path.isfile(file_path)
# Add your utilities or helper functions to this file.

import os
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

def load_env():  
    """
    Loads environment variables from a .env file into the environment.
    This function searches for a .env file in the current and parent directories.
    If found, it loads the environment variables defined in the file into the process environment.
    Raises a FileNotFoundError if no .env file is found.
    Raises:
        FileNotFoundError: If the .env file cannot be located.
    """
    env_path = find_dotenv()
    if not env_path:
        raise FileNotFoundError("Could not find .env file")
    
    load_dotenv(dotenv_path=env_path)

def get_env_var(env_variable):
    """
    Retrieve the value of an environment variable, strip leading/trailing whitespace, and remove any trailing commas.

    :param env_variable (str): The name of the environment variable to retrieve.

    :returns:
        str or None: The processed value of the environment variable, or None if the variable is not set.
    """
    value = os.getenv(env_variable)
    if value is None:
        return None
    return value.strip().rstrip(',')

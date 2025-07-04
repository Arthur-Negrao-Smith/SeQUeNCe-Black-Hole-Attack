from .network_data import Network_Data

import json as js
from typing import Any
import logging

log: logging.Logger = logging.getLogger(__name__)

class Data_Manager:
    """
    Class to manage network's data
    """
    def __init__(self) -> None:
        """
        Constructor for Data_Manager
        """
        self._data: Network_Data = Network_Data()
        self._json: dict = dict()

    def __str__(self) -> str:
        """
        String to see the data

        Returns:
            str: Data in string format
        """
        return f"{self._json}"

    def __len__(self) -> int:
        """
        Get data's number of items

        Returns:
            int: Number of itens
        """
        return len(self._json)

    def update_data(self, data: Network_Data) -> None:
        """
        Updates the data to use in json

        Args:
            data (Network_Data): Data to add in json
        """
        self._data = data

    def get_data(self) -> Network_Data:
        """
        Get all data used to use in json

        Returns:
            Network_Data: Dict to add in json
        """
        return self._data

    def update_json(self, json: dict) -> None:
        """
        Updates the json

        Args:
            json (dict): Dict in json format to change json
        """
        self._json = json

    def get_json(self) -> dict:
        """
        Get the jason

        Returns:
            dict: Dict in json format
        """
        return self._json

    def load_json(self, filename: str, create_file_if_not_exist: bool = False) -> None:
        """
        Load the json data

        Args:
            filename (str): Json's filename to read
            create_file_if_not_exist (bool): Create a file if it doesn't exists
        """
        if create_file_if_not_exist and not self._exist_filename(filename):
            self._create_file(filename)
        elif not self._exist_filename(filename):
            return

        with open(file=filename, mode='r', encoding='utf-8') as file:
            self._data = js.load(file)
            log.debug(f"The data in {filename} was loaded")
            return

    def write_json(self, filename: str) -> None:
        """
        Write the json data

        Args:
            filename (str): Json's filename to write
        """
        self._create_file(filename)

        with open(file=filename, mode='w', encoding='utf-8') as file:
            js.dump(self._json, file, indent=2, ensure_ascii=False)

    def insert_data_in_json(self, element_key: Any, keys: list) -> None:
        """
        Insert data in jason with selected keys

        Args:
            element_key (Any): Any element's key to access in json 
            keys (list): List with json's keys in order
        """
        # if key doens't exist, then create key
        try:
            tmp_element: dict = self._json[keys[0]]
        except:
            self._json[keys[0]] = dict()
            tmp_element: dict = self._json[keys[0]]
        keys.pop(0)

        for key in keys:
            # if key doens't exist, then create key
            try:
                tmp_element = tmp_element[key]
            except:
                tmp_element[key] = dict()
                tmp_element = tmp_element[key]

        tmp_element[element_key] = self.get_data().get_all_data()

    def sum_jsons(self, json1: dict, json2: dict) -> dict:
        result: dict = json1.copy()

        for key, value in json2.items():
            if key in result:
                if isinstance(result[key], set) and isinstance(value, set):
                    result[key] = result[key].union(value)
                elif isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self.sum_jsons(result[key], value)
                else:
                    result[key] = value  # overwrite the data with equal key
            else:
                result[key] = value
        return result

    def print_data_manager(self) -> None:
        """
        To see the data and json
        """
        print(self)

    def _create_file(self, filename: str) -> None:
        """
        Create or clear a file

        Args:
            filename (str): Json's filename to create
        """
        with open(file=filename, mode='w') as file:
            log.debug(f"The file '{filename}' was created")
            file.close()

    def _exist_filename(self, filename: str) -> bool:
        """
        Check the filename's existence

        Returns:
            bool: True if filename is valid, else returns False
        """
        try:
            with open(file=filename, mode='r', encoding='utf-8') as file:
                log.debug(f"The file '{filename}' exists")
                file.close()
            return True

        except FileNotFoundError:
            log.warning(f"The data wasn't loaded. The filename {filename} doesn't finded")
            return False

        except:
            log.warning(f"The data wasn't loaded. An unknown error occurred")
            return False

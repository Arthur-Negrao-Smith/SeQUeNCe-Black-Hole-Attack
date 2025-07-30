from .network_data import Network_Data

import pandas as pd
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
        self._csv_dict: dict[str, list] = dict()

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

    def update_csv_dict(self, csv: dict[str, list]) -> None:
        """
        Updates the CSV dict

        Args:
            csv (dict): Dict to storage the data
        """
        self._csv_dict = csv

    def get_csv_dict(self) -> dict[str, list]:
        """
        Get all network's data in CSV dict

        Returns:
            dict[int, dict]: CSV dict with all network's data storged
        """
        return self._csv_dict

    def load_csv(self, filename: str) -> bool:
        """
        Load the csv dict from any csv file

        Args:
            filename (str): Csv's filename to read

        Returns:
            bool: Returns True if file exists, else returns False
        """
        if not self._exist_filename(filename):
            return False

        with open(file=filename, mode='r', encoding='utf-8') as file:
            data: pd.DataFrame = pd.read_csv(file, sep=',', encoding='utf-8', index_col=False)
            self._csv_dict = data.to_dict(orient='list')
            return True

    def write_csv(self, filename: str, preserve_old_csv: bool = False) -> None:
        """
        Write the entire csv dict in a csv file

        Args:
            filename (str): CSV's filename to write
            preserve_old_csv (bool): If it is False, then overwrite the old csv. Default is False
        """
        data: pd.DataFrame = pd.DataFrame(self._csv_dict)

        # if file doesn't exist and isn't to preserve old csv
        if not self._exist_filename(filename) or not preserve_old_csv:
            with open(file=filename, mode='w', encoding='utf-8') as file:
                data.to_csv(file, sep=',', encoding='utf-8', header=True, index=False)
            log.debug(f"The {filename} was created and was writed the data")
            return

        with open(file=filename, mode='a', encoding='utf-8') as file:
            data.to_csv(file, sep=',', encoding='utf-8', header=False, index=False)
            log.debug(f"The {filename} appended the data")

    def append_data_in_csv_dict(self) -> None:
        """
        Append data in csv dict
        """
        if self._csv_dict == dict():
            for key, value in self.get_data().get_all_data().items():
                self._csv_dict[key] = value
            return

        for key, value in self.get_data().get_all_data().items():
            self._csv_dict[key].append(value[0])

    def append_data_in_csv_file(self, filename: str, append_in_csv_dict: bool = False) -> None:
        """
        Append in a csv file

        Args:
            filename (str): CSV's filename to write
            append_in_csv_dict (bool): If it is True append data in csv dict
        """
        data: pd.DataFrame = pd.DataFrame(self.get_data().get_all_data())

        if append_in_csv_dict:
            self.append_data_in_csv_dict()

        # add header if file not exists
        header: bool = not self._exist_filename(filename)

        with open(file=filename, mode='a', encoding='utf-8') as file:
            data.to_csv(file, sep=',', encoding='utf-8', header=header, index=False)
            log.debug(f"The {filename} appended the data")

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

    def load_json(self, filename: str, create_file_if_not_exist: bool = False) -> bool:
        """
        Load the json data

        Args:
            filename (str): Json's filename to read
            create_file_if_not_exist (bool): Create a file if it doesn't exists

        Returns:
            bool: Returns True if file exists, else returns False
        """
        if create_file_if_not_exist and not self._exist_filename(filename):
            self._create_file(filename)
        elif not self._exist_filename(filename):
            return False

        with open(file=filename, mode='r', encoding='utf-8') as file:
            self._json = js.load(file)
            log.debug(f"The data in {filename} was loaded")
            return True

    def write_json(self, filename: str) -> None:
        """
        Write the json data

        Args:
            filename (str): Json's filename to write
        """
        with open(file=filename, mode='w', encoding='utf-8') as file:
            js.dump(self._json, file, indent=2, ensure_ascii=False)
        log.debug(f"It was writed the data in {filename}")

    def insert_data_in_json(self, element_key: Any, keys: list) -> None:
        """
        Insert data in jason with selected keys and clean data

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
        keys = keys[1:] # don't copy the first element

        for key in keys:
            # if key doens't exist, then create key
            try:
                tmp_element = tmp_element[key]
            except:
                tmp_element[key] = dict()
                tmp_element = tmp_element[key]

        data_with_out_array: dict = self._convert_data_without_lists(self.get_data())
        tmp_element[element_key] = data_with_out_array

    def _convert_data_without_lists(self, data: Network_Data) -> dict:
        """
        Convert network data to remove lists
        """
        temp_data: dict = dict()
        for key, value in data.get_all_data().items():
            temp_data[key] = value[0]
        return temp_data

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

def sum_jsons(json1: dict, json2: dict) -> dict:
    result: dict = json1.copy()

    for key, value in json2.items():
        if key in result:
            if isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = sum_jsons(result[key], value)
            else:
                result[key] = value  # overwrite the data with equal key
        else:
            result[key] = value
    return result

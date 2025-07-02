import json as js
from typing import Any
import logging

log: logging.Logger = logging.getLogger(__name__)

class Data_Manager:
    """
    Class to manage network's data
    """
    from .network import Network
    def __init__(self) -> None:
        """
        Constructor for Data_Manager

        Args:
            network (Network): Network to manage data
        """
        #self.network: Network = network # type: ignore
        self._data: dict = dict()
        self._json: dict = dict()

    def __str__(self) -> str:
        """
        String to see the data

        Returns:
            str: Data in string format
        """
        return f"{self._data}"

    def __getitem__(self, key: Any) -> Any:
        """
        Get data's items

        Args:
            key (Any): Key to access data
        
        Returns:
            Any: Data accessed
        """
        return self._data[key]
    
    def __setitem__(self, key: Any, data: Any) -> None:
        """
        Get data's items

        Args:
            key (Any): Key to access data
            data (Anny): Any data to add
        """
        self._data[key] = data

    def __len__(self) -> int:
        """
        Get data's number of items
        
        Returns:
            int: Number of itens
        """
        return len(self._data)

    def update_data(self, data: dict) -> None:
        """
        Updates the data

        Args:
            data (dict): Dict to add in json
        """
        self._data = data

    def get_data(self) -> dict:
        """
        Get all data

        Returns:
            dict: Dict to add in json
        """
        return self._data
    
    def update_json(self, json: dict) -> None:
        """
        Updates the json

        Args:
            json (dict): Dict in json format to change json
        """
        self._data = json

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
            js.dump(self._data, file, indent=2, ensure_ascii=False)
        
    def _create_file(self, filename: str) -> None:
        """
        Create or clear a file

        Args:
            filename (str): Json's filename to create
        """
        with open(file=filename, mode='w+') as file:
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
            return True
            
        except FileNotFoundError:
            log.warning(f"The data wasn't loaded. The filename {filename} doesn't finded")
            return False
        
        except:
            log.warning(f"The data wasn't loaded. An unknown error occurred")
            return False

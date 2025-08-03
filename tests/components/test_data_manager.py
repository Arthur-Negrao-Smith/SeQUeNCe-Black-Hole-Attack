from components.data_manager import Data_Manager, sum_jsons
from components.network_data import Network_Data
import components.network_data as nd

import pytest as pt
import pandas as pd
import os


TEST_CONSUMED_EPRS: int = -1


def remove_test_file(filename: str) -> None:
    try:
        os.remove(filename)
    except:
        return


@pt.fixture
def network_data() -> Network_Data:
    data: Network_Data = Network_Data()
    data.change_number(nd.CONSUMED_EPRS, TEST_CONSUMED_EPRS)
    return data


@pt.fixture
def data_manager() -> Data_Manager:
    return Data_Manager()


@pt.fixture
def csv_dict_1() -> dict[str, list]:
    csv: dict[str, list] = {"a": [1], "b": [1]}
    return csv


@pt.fixture
def csv_dict_2() -> dict[str, list]:
    csv: dict[str, list] = {"a": [2], "b": [2]}
    return csv


@pt.fixture
def json_1() -> dict:
    json: dict = {"a": {"a.a": 1}, "b": {"b.a": 1}}
    return json


@pt.fixture
def json_2() -> dict:
    json: dict = {"a": {"a.b": 2}, "b": {"b.b": 2}}
    return json


@pt.fixture
def json_sumed() -> dict:
    json: dict = {"a": {"a.a": 1, "a.b": 2}, "b": {"b.a": 1, "b.b": 2}}
    return json


class Test_Data_Manager:
    test_path: str = "tests/components/test-path"
    test_path_csv = f"{test_path}.csv.test"
    test_path_json = f"{test_path}.json.test"

    def test_update_and_get_data(
        self, data_manager: Data_Manager, network_data: Network_Data
    ) -> None:

        data_manager.update_data(network_data)
        assert data_manager.get_data().get_item(nd.CONSUMED_EPRS) == TEST_CONSUMED_EPRS

    def test_update_and_get_csv_dict(
        self, data_manager: Data_Manager, csv_dict_1: dict[str, list]
    ) -> None:

        data_manager.update_csv_dict(csv_dict_1)
        assert data_manager.get_csv_dict() == csv_dict_1

    def test_update_and_get_json(
        self, data_manager: Data_Manager, json_1: dict
    ) -> None:

        data_manager.update_json(json_1)
        assert data_manager.get_json() == json_1

    def test_load_and_write_csv(
        self, data_manager: Data_Manager, csv_dict_1: dict[str, list]
    ) -> None:

        assert data_manager.load_csv(self.test_path_csv) == False

        data_manager.update_csv_dict(csv_dict_1)
        data_manager.write_csv(self.test_path_csv)

        assert data_manager.load_csv(self.test_path_csv) == True
        remove_test_file(self.test_path_csv)
        assert data_manager.get_csv_dict() == csv_dict_1

    def test_load_and_write_json(
        self, data_manager: Data_Manager, json_1: dict[str, list]
    ) -> None:

        assert data_manager.load_json(self.test_path_json) == False

        data_manager.update_json(json_1)
        data_manager.write_json(self.test_path_json)

        assert data_manager.load_json(self.test_path_json) == True
        remove_test_file(self.test_path_json)
        assert data_manager.get_json() == json_1

    def test_append_data_in_csv_dict(
        self, data_manager: Data_Manager, network_data: Network_Data
    ) -> None:

        other_network_data_consumed_eprs: int = -2
        other_network_data: Network_Data = Network_Data()
        other_network_data.change_number(
            nd.CONSUMED_EPRS, other_network_data_consumed_eprs
        )

        data_manager.update_data(network_data)
        data_manager.append_data_in_csv_dict()
        data_manager.write_csv(self.test_path_csv)

        other_data_manager: Data_Manager = Data_Manager()
        other_data_manager.load_csv(filename=self.test_path_csv)
        remove_test_file(filename=self.test_path_csv)

        assert data_manager.get_csv_dict() == other_data_manager.get_csv_dict()

    def test_append_data_in_csv_file(
        self, data_manager: Data_Manager, network_data: Network_Data
    ) -> None:

        # garantee the file doesn't exists
        remove_test_file(filename=self.test_path_csv)
        data_manager.update_data(network_data)
        data_manager.append_data_in_csv_file(
            filename=self.test_path_csv, append_in_csv_dict=True
        )

        assert data_manager._exist_filename(filename=self.test_path_csv) == True

        other_data_manager: Data_Manager = Data_Manager()
        other_data_manager.load_csv(filename=self.test_path_csv)

        assert other_data_manager.get_csv_dict() == data_manager.get_csv_dict()

        other_network_data_consumed_eprs: int = -2
        other_network_data: Network_Data = Network_Data()
        other_network_data.change_number(
            nd.CONSUMED_EPRS, other_network_data_consumed_eprs
        )

        data_manager.update_data(other_network_data)
        data_manager.append_data_in_csv_file(
            self.test_path_csv, append_in_csv_dict=True
        )

        assert data_manager.get_csv_dict().get(nd.CONSUMED_EPRS) == [
            TEST_CONSUMED_EPRS,
            other_network_data_consumed_eprs,
        ]

        data_manager.load_csv(self.test_path_csv)
        remove_test_file(filename=self.test_path_csv)

        assert data_manager.get_csv_dict().get(nd.CONSUMED_EPRS) == [
            TEST_CONSUMED_EPRS,
            other_network_data_consumed_eprs,
        ]

    def test_insert_data_in_json(
        self, data_manager: Data_Manager, network_data: Network_Data
    ) -> None:

        test_keys: list[str] = ["a", "b"]
        final_key: str = "c"

        data_manager.update_data(network_data)
        data_manager.insert_data_in_json(element_key=final_key, keys=test_keys)
        test_keys.append(final_key)

        tmp_json: dict = data_manager.get_json()
        for key in test_keys:
            tmp_json = tmp_json[key]

        assert tmp_json == data_manager._convert_data_without_lists(network_data)

    def test_csv_to_dataframe(
        self, data_manager: Data_Manager, network_data: Network_Data
    ) -> None:

        assert isinstance(data_manager.csv_to_dataframe(), pd.DataFrame)

        assert data_manager.csv_to_dataframe().to_dict() == {}

        data_manager.update_data(network_data)
        data_manager.append_data_in_csv_dict()

        assert (
            data_manager.csv_to_dataframe().to_dict()
            == pd.DataFrame(network_data.get_all_data()).to_dict()
        )


def test_sum_jsons(json_1: dict, json_2: dict, json_sumed: dict) -> None:

    assert sum_jsons(json_1, json_2) == json_sumed

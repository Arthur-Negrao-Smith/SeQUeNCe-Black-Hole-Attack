import components.network_data as nd
from components.network_data import Network_Data

class TestNetwork_Data:
    data: Network_Data = Network_Data()


    def test_increment(self) -> None:

        self.data.change_number(nd.CONSUMED_EPRS, 0)
        self.data.increment(nd.CONSUMED_EPRS, 2)
        assert self.data.get_item(nd.CONSUMED_EPRS) == 2

        self.data.change_number(nd.CONSUMED_EPRS, 0)
        self.data.increment(nd.CONSUMED_EPRS)
        assert self.data.get_item(nd.CONSUMED_EPRS) == 1


    def test_get_item(self) -> None:

        self.data.change_number(nd.CONSUMED_EPRS, 0)
        assert self.data.get_item(nd.CONSUMED_EPRS) == 0


    def test_clear(self) -> None:

        self.data.clear()
        assert self.data.get_all_data() == {}

import unittest
from unittest.mock import patch, Mock

from certbot import errors
from certbot_dns_ionos.ionos import _IONOSClient


test_domain = "test_domain.de"
test_record_name = "_acme-challenge.test_domain.de"
test_record_content = "123456789"


class TestIONOSClient(unittest.TestCase):
    def setUp(self):
        self.client = _IONOSClient("test_token")
        self.mock_response = Mock()

    def test_add_txt_record_with_non_ok_result_raises_exception(self):
        self.mock_response.status_code = 401

        with patch("requests.get", return_value=self.mock_response) as mock_get:
            with self.assertRaises(errors.PluginError) as context:
                self.client.add_txt_record(test_domain, test_record_name, test_record_content)
            self.assertEqual(str(context.exception), "Received non OK status from IONOS API 401")
            mock_get.assert_called_once()
            

    def test_add_txt_record_find_zone_id_with_no_result_raises_exception(self):
        self.mock_response.json.return_value = {"items": []}
        self.mock_response.status_code = 200

        with patch("requests.get", return_value=self.mock_response) as mock_get:
            with self.assertRaises(errors.PluginError) as context:
                self.client.add_txt_record(test_domain, test_record_name, test_record_content)
            self.assertEqual(str(context.exception), "Domain not known")
            mock_get.assert_called_once()

    def test_add_txt_record_find_zone_id_with_unkown_zone_raises_exception(self):
        self.mock_response.json.return_value = {"items": [{"id": "any", "properties":{"zoneName": "any"}}]}
        self.mock_response.status_code = 200

        with patch("requests.get", return_value=self.mock_response) as mock_get:
            with self.assertRaises(errors.PluginError) as context:
                self.client.add_txt_record(test_domain, test_record_name, test_record_content)
            self.assertEqual(str(context.exception), "Domain not known")
            mock_get.assert_called_once()

    def test_find_zone_id_success(self):
        #zone_id = "test"
        #self.mock_response.json.return_value = {"items": [{"id": zone_id, "properties":{"zoneName": test_domain}}]}
        #self.mock_response.status_code = 200
        #self.mock_response.
        #with patch("requests.get", return_value=self.mock_response) as mock_get:
        #    zone_id = self.client._find_zone_id(test_domain)
        #    self.assertEqual(zone_id, zone_id)
        #    mock_get.assert_called_once()
        pass


if __name__ == "__main__":
    unittest.main()
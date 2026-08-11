import unittest
from unittest.mock import patch, Mock, call

from certbot import errors
from certbot_dns_ionos_cloud.ionos import _IONOSClient
from certbot_dns_ionos_cloud.ionos import dns_api_base_url


test_domain = "test_domain.de"
test_record_name = "_acme-challenge"
test_record_name_full = "_acme-challenge.test_domain.de"
test_record_content = "123456789"
zone_id = "test"
record_id = "12356"
token = "test_token"
auth_header={"Authorization":"Bearer " + token}


class TestIONOSClient(unittest.TestCase):
    def setUp(self):
        self.client = _IONOSClient("test_token", "", "")
        self.mock_response = Mock()

    def test_add_txt_record_with_non_ok_result_raises_exception(self):
        self.mock_response.status_code = 401

        with patch("requests.get", return_value=self.mock_response) as mock_get:
            with self.assertRaises(errors.PluginError) as context:
                self.client.add_txt_record(
                    test_domain, test_record_name_full, test_record_content
                )
            self.assertEqual(
                str(context.exception), "Received non OK status from IONOS API 401"
            )
            mock_get.assert_called_once_with(f"{dns_api_base_url}/zones",
                                        params={"filter.zoneName": test_domain}, headers=auth_header)

    def test_add_txt_record_find_zone_id_with_no_result_raises_exception(self):
        self.mock_response.json.return_value = {"items": []}
        self.mock_response.status_code = 200

        with patch("requests.get", return_value=self.mock_response) as mock_get:
            with self.assertRaises(errors.PluginError) as context:
                self.client.add_txt_record(
                    test_domain, test_record_name_full, test_record_content
                )
            self.assertEqual(str(context.exception), "Domain not known")
            mock_get.assert_called_once_with(f"{dns_api_base_url}/zones",
                                        params={"filter.zoneName": test_domain}, headers=auth_header)

    def test_add_txt_record_find_zone_id_with_unkown_zone_raises_exception(self):
        self.mock_response.json.return_value = {
            "items": [{"id": "any", "properties": {"zoneName": "any"}}]
        }
        self.mock_response.status_code = 200

        with patch("requests.get", return_value=self.mock_response) as mock_get:
            with self.assertRaises(errors.PluginError) as context:
                self.client.add_txt_record(
                    test_domain, test_record_name_full, test_record_content
                )
            self.assertEqual(str(context.exception), "Domain not known")
            mock_get.assert_called_once_with(f"{dns_api_base_url}/zones",
                                        params={"filter.zoneName": test_domain}, headers=auth_header)

    def test_add_txt_record_with_not_found_record_creates_record(self):
        get_zones_response = Mock()
        get_zones_response.status_code = 200
        get_zones_response.json.return_value = {
            "items": [{"id": zone_id, "properties": {"zoneName": test_domain}}]
        }

        get_records_response = Mock()
        get_records_response.status_code = 202
        get_records_response.json.return_value = {"items": []}

        responses = [get_zones_response, get_records_response]

        insert_response = Mock()
        insert_response.status_code = 202

        with patch("requests.get", side_effect=responses) as mock_get:
            with patch("requests.post", return_value=insert_response) as mock_post:
                self.client.add_txt_record(
                    test_domain, test_record_name_full, test_record_content
                )
                assert len(mock_get.mock_calls) == 2
                call1 = call(f"{dns_api_base_url}/zones",
                                        params={"filter.zoneName": test_domain}, headers=auth_header)
                call2 = call(f"{dns_api_base_url}/records",
                                        params={"filter.zoneId": zone_id, "filter.name":test_record_name}, headers=auth_header)
                mock_get.assert_has_calls([call1, call2])
                mock_post.assert_called_once_with(f"{dns_api_base_url}/zones/{zone_id}/records", json={
                                "properties": {
                                    "name": test_record_name,
                                    "type": "TXT",
                                    "content": test_record_content,
                                }
                            },
                            headers=auth_header)

    def test_add_txt_record_with_exisiting_record_same_content_does_nothing(self):
        get_zones_response = Mock()
        get_zones_response.status_code = 200
        get_zones_response.json.return_value = {
            "items": [{"id": zone_id, "properties": {"zoneName": test_domain}}]
        }

        get_records_response = Mock()
        get_records_response.status_code = 202
        get_records_response.json.return_value = {
            "items": [
                {
                    "id": record_id,
                    "properties": {
                        "name": test_record_name,
                        "content": test_record_content,
                    },
                }
            ]
        }
        responses = [get_zones_response, get_records_response]

        with patch("requests.get", side_effect=responses) as mock_get:
            self.client.add_txt_record(test_domain, test_record_name_full, test_record_content)
            assert len(mock_get.mock_calls) == 2
            call1 = call(f"{dns_api_base_url}/zones",
                                    params={"filter.zoneName": test_domain}, headers=auth_header)
            call2 = call(f"{dns_api_base_url}/records",
                                    params={"filter.zoneId": zone_id, "filter.name":test_record_name}, headers=auth_header)
            mock_get.assert_has_calls([call1, call2])

    def test_add_txt_record_with_exisiting_record_different_updates_record(self):
        get_zones_response = Mock()
        get_zones_response.status_code = 200
        get_zones_response.json.return_value = {
            "items": [{"id": zone_id, "properties": {"zoneName": test_domain}}]
        }

        get_records_response = Mock()
        get_records_response.status_code = 202
        get_records_response.json.return_value = {
            "items": [
                {
                    "id": record_id,
                    "properties": {
                        "name": test_record_name,
                        "content": "old content",
                    },
                }
            ]
        }

        responses = [get_zones_response, get_records_response]

        update_response = Mock()
        update_response.status_code = 202

        with patch("requests.get", side_effect=responses) as mock_get:
            with patch("requests.put", return_value=update_response) as mock_put:
                self.client.add_txt_record(
                    test_domain, test_record_name_full, test_record_content
                )
                assert mock_get.call_count == 2
                mock_put.assert_called()
                call1 = call(f"{dns_api_base_url}/zones",
                                        params={"filter.zoneName": test_domain}, headers=auth_header)
                call2 = call(f"{dns_api_base_url}/records",
                                        params={"filter.zoneId": zone_id, "filter.name":test_record_name}, headers=auth_header)
                mock_get.assert_has_calls([call1, call2])
                mock_put.assert_called_once_with(f"{dns_api_base_url}/zones/{zone_id}/records/{record_id}",
                                json={"id": record_id, "properties": {
                                                        "name": test_record_name,
                                                        "content": test_record_content,
                                                    }},
                                headers=auth_header)

    def test_delete_txt_record_find_zone_id_with_no_result_raises_exception(self):
        self.mock_response.json.return_value = {"items": []}
        self.mock_response.status_code = 200

        with patch("requests.get", return_value=self.mock_response) as mock_get:
            with self.assertRaises(errors.PluginError) as context:
                self.client.del_txt_record(
                    test_domain, test_record_name_full, test_record_content
                )
            self.assertEqual(str(context.exception), "Domain not known")
            mock_get.assert_called_once_with(f"{dns_api_base_url}/zones",
                                        params={"filter.zoneName": test_domain}, headers=auth_header)

    def test_delete_record_find_zone_id_with_unkown_zone_raises_exception(self):
        self.mock_response.json.return_value = {
            "items": [{"id": "any", "properties": {"zoneName": "any"}}]
        }
        self.mock_response.status_code = 200

        with patch("requests.get", return_value=self.mock_response) as mock_get:
            with self.assertRaises(errors.PluginError) as context:
                self.client.del_txt_record(
                    test_domain, test_record_name_full, test_record_content
                )
            self.assertEqual(str(context.exception), "Domain not known")
            mock_get.assert_called_once_with(f"{dns_api_base_url}/zones",
                                        params={"filter.zoneName": test_domain}, headers=auth_header)

    def test_delete_txt_record_with_not_found_record_does_nothing(self):
        get_zones_response = Mock()
        get_zones_response.status_code = 200
        get_zones_response.json.return_value = {
            "items": [{"id": zone_id, "properties": {"zoneName": test_domain}}]
        }

        get_records_response = Mock()
        get_records_response.status_code = 202
        get_records_response.json.return_value = {"items": []}

        responses = [get_zones_response, get_records_response]

        with patch("requests.get", side_effect=responses) as mock_get:
            with patch("requests.delete", return_value={}) as mock_delete:
                self.client.del_txt_record(
                    test_domain, test_record_name_full, test_record_content
                )
                mock_delete.assert_not_called()
                call1 = call(f"{dns_api_base_url}/zones",
                                        params={"filter.zoneName": test_domain}, headers=auth_header)
                call2 = call(f"{dns_api_base_url}/records",
                                        params={"filter.zoneId": zone_id, "filter.name":test_record_name}, headers=auth_header)
                mock_get.assert_has_calls([call1, call2])

    def test_delete_txt_record_with_existing_record_and_different_content_does_nothing(
        self,
    ):
        get_zones_response = Mock()
        get_zones_response.status_code = 200
        get_zones_response.json.return_value = {
            "items": [{"id": zone_id, "properties": {"zoneName": test_domain}}]
        }

        get_records_response = Mock()
        get_records_response.status_code = 202
        get_records_response.json.return_value = {
            "items": [
                {
                    "id": record_id,
                    "properties": {
                        "name": test_record_name,
                        "content": "unmatching requested content",
                    },
                }
            ]
        }

        responses = [get_zones_response, get_records_response]

        with patch("requests.get", side_effect=responses) as mock_get:
            with patch("requests.delete", return_value={}) as mock_delete:
                self.client.del_txt_record(
                    test_domain, test_record_name_full, test_record_content
                )
                mock_delete.assert_not_called()
                assert mock_get.call_count == 2
                call1 = call(f"{dns_api_base_url}/zones",
                                        params={"filter.zoneName": test_domain}, headers=auth_header)
                call2 = call(f"{dns_api_base_url}/records",
                                        params={"filter.zoneId": zone_id, "filter.name":test_record_name}, headers=auth_header)
                mock_get.assert_has_calls([call1, call2])

    def test_delete_txt_record_with_existing_record_and_same_content_succeeds(self):
        get_zones_response = Mock()
        get_zones_response.status_code = 200
        get_zones_response.json.return_value = {
            "items": [{"id": zone_id, "properties": {"zoneName": test_domain}}]
        }

        get_records_response = Mock()
        get_records_response.status_code = 202
        get_records_response.json.return_value = {
            "items": [
                {
                    "id": record_id,
                    "properties": {
                        "name": test_record_name,
                        "content": test_record_content,
                    },
                }
            ]
        }

        responses = [get_zones_response, get_records_response]

        delete_response = Mock()
        delete_response.status_code = 202

        with patch("requests.get", side_effect=responses) as mock_get:
            with patch("requests.delete", return_value=delete_response) as mock_delete:
                self.client.del_txt_record(
                    test_domain, test_record_name_full, test_record_content
                )
                call1 = call(f"{dns_api_base_url}/zones",
                                        params={"filter.zoneName": test_domain}, headers=auth_header)
                call2 = call(f"{dns_api_base_url}/records",
                                        params={"filter.zoneId": zone_id, "filter.name":test_record_name}, headers=auth_header)
                mock_get.assert_has_calls([call1, call2])
                assert mock_delete.call_count == 1
                mock_delete.assert_called_once_with(f"{dns_api_base_url}/zones/{zone_id}/records/{record_id}",
                                        headers=auth_header)


if __name__ == "__main__":
    unittest.main()

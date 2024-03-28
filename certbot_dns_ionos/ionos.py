"""DNS Authenticator for IONOS."""
import json
import logging

import requests

from certbot import errors
from certbot.plugins import dns_common

logger = logging.getLogger(__name__)

dns_api_base_url = "https://dns.de-fra.ionos.com"


class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for IONOS

    This Authenticator uses the IONOS API to fulfill a dns-01 challenge.
    """
    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(
            add, default_propagation_seconds=120
        )
        add("credentials", help="credentials INI file.")

    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return (
            "This plugin configures a DNS TXT record to respond to a dns-01 challenge using "
            + "the IONOS REST API."
        )

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            "credentials",
            "IONOS API credentials INI file. Only Bearer token authentication is supported",
            {"token":"access token for the IONOS API"},
        )

    def _perform(self, domain, validation_name, validation):
        self._get_ionos_client().add_txt_record(
            domain, validation_name, validation
        )

    def _cleanup(self, domain, validation_name, validation):
        self._get_ionos_client().del_txt_record(
            domain, validation_name, validation
        )

    def _get_ionos_client(self):
        return _IONOSClient(
            self.credentials.conf("token")
        )


class _IONOSClient(object):
    """
    Encapsulates all communication with the IONOS Cloud DNS API.
    """

    def __init__(self, token:str):
        logger.debug("creating IONOS Client")
        self.headers = {"Authorization": "Bearer " + token}

        
    def _handle_response(self, resp: requests.Response):
     if resp.status_code != 200 and resp.status_code != 202:
         raise errors.PluginError(
             "Received non OK status from IONOS API {0}".format(resp.status_code)
         )
     try:
         return resp.json()
     except json.decoder.JSONDecodeError:
         raise errors.PluginError(
             "API response with non JSON: {0}".format(resp.text)
         )

    def add_txt_record(self, domain, record_name:str, record_content):
        """
        Add a TXT record using the supplied information.

        :param str domain: The domain to use to look up the managed zone.
        :param str record_name: The record name (typically beginning with '_acme-challenge.').
        :param str record_content: The record content (typically the challenge validation).
        :raises certbot.errors.PluginError: if an error occurs communicating with the IONOS API
        """
        # because the domain is appended by the API, we remove it from it from the record name
        record_name_without_domain = record_name.replace("."+domain, "")
        zone_id = self._find_zone_id(domain)
        if zone_id is None:
            raise errors.PluginError("Domain not known")
        logger.debug("domain found: %s with id: %s", domain, zone_id)
        record = self.get_existing_txt_acme_record(zone_id, record_name_without_domain)
        if record is not None:
            record_properties = record["properties"]
            if record_properties["content"] == record_content:
                logger.info("already there, id {0}".format(record["id"]))
                return
            else:
                logger.info("update {0}".format(record["id"]))
                record_properties["content"] = record_content
                self._update_txt_record(
                    zone_id, record
                )
        else:
            logger.info("insert new txt record")
            self._insert_txt_record(zone_id, record_name_without_domain, record_content)

    def del_txt_record(self, domain, record_name:str, record_content:str):
        """
        Delete a TXT record using the supplied information.

        :param str domain: The domain to use to look up the managed zone.
        :param str record_name: The record name (typically beginning with '_acme-challenge.').
        :param str record_content: The record content (typically the challenge validation).
        :raises certbot.errors.PluginError: if an error occurs communicating with the IONOS API
        """
        zone_id = self._find_zone_id(domain)
        if zone_id is None:
            raise errors.PluginError("Domain not known")
        logger.debug("domain found: %s with id: %s", domain, zone_id)
        record = self.get_existing_txt_acme_record(zone_id, record_name.replace("."+domain, ""))
        if record is not None:
            record_properties = record["properties"]
            if record_properties["content"] == record_content:
                logger.debug("delete TXT record: %s", record["id"])
                self._handle_response(
            requests.delete(dns_api_base_url + "/zones/" + zone_id +"/records/"+record["id"], headers=self.headers))
                


    def _insert_txt_record(self, zone_id, record_name, record_content):
        new_record = {"properties":{
                "name":record_name, "type":"TXT", "content":record_content}}
        
        self._handle_response(
            requests.post(dns_api_base_url + "/zones/" + zone_id +"/records", json=new_record, headers=self.headers))
        logger.debug("create with payload: %s", new_record)

    def _update_txt_record(
        self, zone_id, record
    ):
        self._handle_response(
            requests.put(dns_api_base_url + "/zones/" + zone_id +"/records/"+record["id"], json=record, headers=self.headers))
        logger.debug("update with payload: %s", record)


    def _find_zone_id(self, domain):
        """
        Find the zone for a given domain.

        :param str domain: The domain for which to find the zone.
        :returns: The ID of the zone, if found.
        :rtype: str
        :raises certbot.errors.PluginError: if the zone cannot be found.
        """

        zones_response = self._handle_response(
            requests.get(dns_api_base_url + "/zones", params={"filter.zoneName":domain}, headers=self.headers))
        
        for zone_item in zones_response["items"]:
            zone_item_properties = zone_item["properties"]
            if zone_item_properties and zone_item_properties["zoneName"] == domain:
                return zone_item["id"]
            
        return None

    def get_existing_txt_acme_record(self, zone_id, record_name):
        """
        Get existing TXT records for the record name.

        :param str zone_id: The ID of the zone.
        :param str record_name: The record name (typically beginning with '_acme-challenge.').

        :returns: TXT record value or None
        :rtype: `object` or `None`

        """
        records_response = self._handle_response(
            requests.get(dns_api_base_url + "/records", 
                         params={"filter.zoneId": zone_id, 
                                 "filter.name": record_name}, headers=self.headers))
        
        for record_item in records_response["items"]:
            record_item_properties = record_item["properties"]
            if record_item_properties and record_item_properties.get("name") == record_name:
                return record_item
            
        return None

#! /usr/bin/env python

import requests

class Settings():

    """vManage Settings API
    Responsible for DELETE, GET, POST, PUT methods against vManage
    Settings.
    """

    def __init__(self, header, host, port=443):

        """Initialize vManage Settings object with session parameters.
        Args:
            session (obj): Requests Session object
            host (str): hostname or IP address of vManage
            port (int): default HTTPS 443
        """

        self.headers = header
        self.host = host
        self.port = port
        self.base_url = f'https://{self.host}:{self.port}/dataservice/settings/configuration'

    def get_vmanage_org(self):
        """Get vManage organization
        Args:
        Returns:
            org (str): The vManage organization.
        """

        url = f"{self.base_url}/organization"
        response = requests.get(url=url, headers=self.headers, verify=False)
        if response.status_code == 200:
            items = response.json()
            for item in items['data']:
                org = item['org']
            return (org)
        else:
            return None

    def get_vbond(self):
        """Get vBond IP or name
        Args:
        Returns:
            vbond: vbond ip or name
        """

        url = f"{self.base_url}/device"
        response = requests.get(url=url, headers=self.headers, verify=False)
        if response.status_code == 200:
            items = response.json()
            for item in items['data']:
                vbond = item['domainIp']
            return (vbond)
        else:
            return None

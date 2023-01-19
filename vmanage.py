#! /usr/bin/env python

import requests

class Authentication:

    def __init__(self, host, port, user, password, validate_certs=False, timeout=10):

        """Initialize Authentication object with session parameters.
        Args:
            host (str): hostname or IP address of vManage
            user (str): username for authentication
            password (str): password for authentication
            port (int): default HTTPS port 443
            validate_certs (bool): turn certificate validation
                on or off.
            timeout (int): how long Reqeusts will wait for a
                response from the server, default 10 seconds
        """

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.timeout = timeout
        self.base_url = f'https://{self.host}:{self.port}'
        #self.base_url = "https://%s:%s" % (self.host, self.port)
        self.session = requests.Session()
        self.session.verify = validate_certs

    def login(self):
        api = "/j_security_check"
        url = self.base_url + api
        payload = {'j_username': self.user, 'j_password': self.password}
        response = requests.post(url=url, data=payload, verify=False)
        try:
            cookies = response.headers["Set-Cookie"]
            jsessionid_full = cookies.split(";")
            self.jsessionid = jsessionid_full[0]
            return (self.jsessionid)
        except:
            if logger is not None:
                logger.error("No valid JSESSION ID returned\n")
            exit()

    def get_token(self):
        headers = {'Cookie': self.jsessionid}
        api = "/dataservice/client/token"
        url = self.base_url + api
        response = requests.get(url=url, headers=headers, verify=False)
        if response.status_code == 200:
            return (response.text)
        else:
            return None




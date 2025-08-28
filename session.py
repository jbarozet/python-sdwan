#! /usr/bin/env python

# Session-based Authentication for Cisco SD-WAN Manager
#
# Log in with a username and password to establish a session.
# Get a cross-site request forgery prevention token, necessary for most POST operations
#
# More information [here](https://developer.cisco.com/docs/sdwan/authentication/#session-based-authentication)

import logging
import os
import sys

import requests
import urllib3

logger = logging.getLogger(__name__)

# Disable insecure request warnings globally
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ----------------------------------------------------------
class Authentication:
    """
    Handles session-based authentication for SD-WAN Manager.
    """

    def __init__(self, host, port, user, password, validate_certs=False, timeout=10):
        """
        Initialize Authentication object with session parameters.
        Args:
            host (str): hostname or IP address of SD-WAN Manager
            user (str): username for authentication
            password (str): password for authentication
            port (int): default HTTPS port 443
            validate_certs (bool): turn certificate validation on or off.
            timeout (int): how long Requests will wait for a response from the server, default 10 seconds
        """

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.timeout = timeout
        self.base_url = f"https://{self.host}:{self.port}"
        self.session = requests.Session()
        self.session.verify = validate_certs  # Set session-wide verification
        self.jsessionid = None
        self.token = None
        self.header = None
        self.dataservice_base_url = None

    def login(self):
        """
        Performs the initial login to get the JSESSIONID.
        """

        api = "/j_security_check"
        url = self.base_url + api
        payload = {"j_username": self.user, "j_password": self.password}

        response = None
        try:
            response = self.session.post(url=url, data=payload, timeout=self.timeout)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

            cookies = response.headers.get("Set-Cookie")
            if not cookies:
                raise ValueError("No 'Set-Cookie' header found in login response.")

            jsessionid_full = cookies.split(";")
            self.jsessionid = jsessionid_full[0]
            return self.jsessionid

        except requests.exceptions.RequestException as e:
            logger.error(
                f"Login failed: {e}. Response: {response.text if response is not None else 'No response'}\n"
            )
            sys.exit(1)

        except ValueError as e:
            logger.error(f"Login failed: {e}\n")
            sys.exit(1)

    def get_token(self):
        """
        Retrieves the X-XSRF-TOKEN.
        """

        if not self.jsessionid:
            logger.warning("JSESSIONID not set, attempting login before getting token.")
            self.login()  # Ensure jsessionid is present

        headers = {
            "Cookie": self.jsessionid
        }  # This cookie is also managed by self.session
        api = "/dataservice/client/token"
        url = self.base_url + api

        response = None

        try:
            response = self.session.get(url=url, headers=headers, timeout=self.timeout)
            response.raise_for_status()  # Raise an exception for HTTP errors
            self.token = response.text
            return self.token

        except requests.exceptions.RequestException as e:
            logger.error(
                f"Failed to get X-XSRF-TOKEN: {e}. Status: {response.status_code if response is not None else 'N/A'}, Response: {response.text if response is not None else 'No response'}\n"
            )
            return None

    def establish_session(self):
        """
        Performs login and token retrieval, then constructs header and base_url.
        """

        self.jsessionid = self.login()
        self.token = self.get_token()

        if self.token:
            self.header = {
                "Content-Type": "application/json",
                "Cookie": self.jsessionid,
                "X-XSRF-TOKEN": self.token,
            }
        else:
            # Fallback if token is not obtained, though it might indicate an issue
            self.header = {
                "Content-Type": "application/json",
                "Cookie": self.jsessionid,
            }
            logger.warning(
                "X-XSRF-TOKEN was not obtained. API calls might fail if it's required."
            )

        self.dataservice_base_url = f"https://{self.host}:{self.port}/dataservice"
        return self.dataservice_base_url, self.header


# ----------------------------------------------------------
def get_manager_credentials_from_env():
    """
    Retrieves manager credentials from environment variables.
    Exits if any required variable is missing.
    """

    manager_host = os.environ.get("manager_host")
    manager_port = os.environ.get("manager_port")
    manager_username = os.environ.get("manager_username")
    manager_password = os.environ.get("manager_password")

    # Check for None values first
    if not all([manager_host, manager_port, manager_username, manager_password]):
        print(
            "Manager details must be set via environment variables using below commands:\n"
            "For Windows Workstation:\n"
            "  set manager_host=198.18.1.10\n"
            "  set manager_port=8443\n"
            "  set manager_username=admin\n"
            "  set manager_password=admin\n"
            "For MAC OSX / Linux Workstation:\n"
            "  export manager_host=198.18.1.10\n"
            "  export manager_port=8443\n"
            "  export manager_username=admin\n"
            "  export manager_password=admin"
        )
        sys.exit(1)

    return manager_host, manager_port, manager_username, manager_password


# ----------------------------------------------------------
def get_authenticated_session_details():
    """
    Orchestrates the retrieval of credentials, authentication,
    and returns the base URL and header for API calls.
    """
    host, port, user, password = get_manager_credentials_from_env()
    auth_manager = Authentication(host, port, user, password)
    base_url, header = auth_manager.establish_session()
    return base_url, header

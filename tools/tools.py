#!/usr/bin/env python3

from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib3
import requests
import os
import click
import cmd
import sys
import tabulate

requests.packages.urllib3.disable_warnings()


vmanage_host = os.environ.get("vmanage_host")
vmanage_port = os.environ.get("vmanage_port")
vmanage_username = os.environ.get("vmanage_username")
vmanage_password = os.environ.get("vmanage_password")

if vmanage_host is None or vmanage_port is None or vmanage_username is None or vmanage_password is None:
    print("For Windows Workstation, vManage details must be set via environment variables using below commands")
    print("set vmanage_host=198.18.1.10")
    print("set vmanage_port=8443")
    print("set vmanage_username=admin")
    print("set vmanage_password=admin")
    print("For MAC OSX Workstation, vManage details must be set via environment variables using below commands")
    print("export vmanage_host=198.18.1.10")
    print("export vmanage_port=8443")
    print("export vmanage_username=admin")
    print("export vmanage_password=admin")
    exit()


# ----------------------------------------------------------------------------------------------------
# Authentication Class
# ----------------------------------------------------------------------------------------------------

class Authentication:

    @staticmethod
    def get_jsessionid(vmanage_host, vmanage_port, username, password):
        api = "/j_security_check"
        base_url = "https://%s:%s" % (vmanage_host, vmanage_port)
        url = base_url + api
        payload = {'j_username': username, 'j_password': password}

        response = requests.post(url=url, data=payload, verify=False)
        try:
            cookies = response.headers["Set-Cookie"]
            jsessionid = cookies.split(";")
            return (jsessionid[0])
        except:
            if logger is not None:
                logger.error("No valid JSESSION ID returned\n")
            exit()

    @staticmethod
    def get_token(vmanage_host, vmanage_port, jsessionid):
        headers = {'Cookie': jsessionid}
        base_url = "https://%s:%s" % (vmanage_host, vmanage_port)
        api = "/dataservice/client/token"
        url = base_url + api
        response = requests.get(url=url, headers=headers, verify=False)
        if response.status_code == 200:
            return (response.text)
        else:
            return None

# ----------------------------------------------------------------------------------------------------
# Authenticate to vManage
# ----------------------------------------------------------------------------------------------------

Auth = Authentication()
jsessionid = Auth.get_jsessionid(
    vmanage_host, vmanage_port, vmanage_username, vmanage_password)
token = Auth.get_token(vmanage_host, vmanage_port, jsessionid)

if token is not None:
    header = {'Content-Type': "application/json",
              'Cookie': jsessionid, 'X-XSRF-TOKEN': token}
else:
    header = {'Content-Type': "application/json", 'Cookie': jsessionid}

base_url = "https://%s:%s/dataservice" % (vmanage_host, vmanage_port)


# ----------------------------------------------------------------------------------------------------
# Commands
# ----------------------------------------------------------------------------------------------------

@click.group()
def cli():
    """Command line tool for vManage APIs).
    """
    pass


#----------------------------------------------------------------------------------------------------
# approute-fields
#----------------------------------------------------------------------------------------------------

@click.command()
def approute_fields():
    """ Retrieve App route Aggregation API Query fields.                                  
        \nExample command: ./monitor-app-route-stats.py approute-fields
    """

    try:
        api_url = "/statistics/approute/fields"

        url = base_url + api_url

        response = requests.get(url=url, headers=header, verify=False)

        if response.status_code == 200:
            items = response.json()
        else:
            click.echo("Failed to get list of App route Query fields " + str(response.text))
            exit()

        tags = list()
        cli = cmd.Cmd()

        for item in items:
            tags.append(item['property'] + "(" + item['dataType'] + ")" )

        click.echo(cli.columnize(tags,displaywidth=120))

    except Exception as e:
        print('Exception line number: {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

#----------------------------------------------------------------------------------------------------
# NBAR Apps
#----------------------------------------------------------------------------------------------------

@click.command()
def nbar_apps():
    """ Get NBAR Applications.                                  
        \nExample command: ./tools.py nbar-apps
    """

    try:
        api_url = "/device/dpi/application-mapping"

        url = base_url + api_url

        response = requests.get(url=url, headers=header, verify=False)

        if response.status_code == 200:
            items = response.json()["data"]
        else:
            click.echo("Failed to get list of App " + str(response.text))
            exit()

        app_headers = ["name", "longname", "family"]
        table = list()

        for item in items:
            tr = [item['name'], item['longname'], item['family']]
            table.append(tr)
        
        table.sort()
        
        try:
            click.echo(tabulate.tabulate(table, app_headers, tablefmt="fancy_grid"))
        except UnicodeEncodeError:
                click.echo(tabulate.tabulate(table, app_headers, tablefmt="grid"))

    except Exception as e:
        print('Exception line number: {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


# ----------------------------------------------------------------------------------------------------
# Build Command Menu
# ----------------------------------------------------------------------------------------------------

cli.add_command(approute_fields)
cli.add_command(nbar_apps)


if __name__ == "__main__":
    cli()

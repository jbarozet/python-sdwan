#! /usr/bin/env python

import requests
import os
import cmd
import tabulate
import click

requests.packages.urllib3.disable_warnings()


# ----------------------------------------------------------------------------------------------------
# vManage Authentication
# ----------------------------------------------------------------------------------------------------

def get_jsessionid(host,port,username,password):
    api = "/j_security_check"
    base_url = "https://%s:%s" % (host, port)
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

def get_token(host, port, jsessionid):
    headers = {'Cookie': jsessionid}
    base_url = "https://%s:%s" % (host, port)
    api = "/dataservice/client/token"
    url = base_url + api
    response = requests.get(url=url, headers=headers, verify=False)
    if response.status_code == 200:
        return (response.text)
    else:
        return None


# ----------------------------------------------------------------------------------------------------
# Click CLI
# ----------------------------------------------------------------------------------------------------

@click.group()
def cli():
    """Command line tool for to collect application names).
    """
    pass


# ----------------------------------------------------------------------------------------------------
# app-list
# ----------------------------------------------------------------------------------------------------

@click.command()
def app_list():
    """ Retrieve the list of Applications.                                  
        \nExample command: ./app.py app-list
    """
    print("app-list")

    api_url = "/device/dpi/application-mapping"
    url = base_url + api_url

    response = requests.get(url=url, headers=header, verify=False)
    if response.status_code == 200:
        items = response.json()
        app_headers = ["App name", "Family", "ID"]
    else:
        click.echo(
            "Failed to get list of Apps " + str(response.text))
        exit()
    
    table = list()
    cli = cmd.Cmd()

    for item in items['data']:
        tr = [item['name'], item['family'], item['appId']]
        table.append(tr)

    click.echo(tabulate.tabulate(table, app_headers, tablefmt="fancy_grid"))


# ----------------------------------------------------------------------------------------------------
# app-list-2
# Display app-name and family in multi-column view
# ----------------------------------------------------------------------------------------------------

@click.command()
def app_list_2():
    """ Retrieve the list of Applications.                                  
        \nExample command: ./app.py app-list-2
    """
    print("app-list-2")

    api_url = "/device/dpi/application-mapping"
    url = base_url + api_url

    response = requests.get(url=url, headers=header, verify=False)
    
    if response.status_code == 200:
        items = response.json()    
    else:
        click.echo("Failed to get list of Apps " + str(response.text))
        exit()
    
    table = list()
    cli = cmd.Cmd()

    for item in items['data']:
        #print(item['name'])
        table.append(item['name'] + "(" + item['family'] + ")")

    click.echo(cli.columnize(table, displaywidth=120))


# ----------------------------------------------------------------------------------------------------
# qosmos-list
# ----------------------------------------------------------------------------------------------------

@click.command()
def qosmos_list():
    """ Retrieve the list of Qosmos Applications.                                  
        \nExample command: ./app.py qosmos-list
    """
    print("qosmos-list")

    api_url = "/device/dpi/qosmos-static/applications"
    url = base_url + api_url

    response = requests.get(url=url, headers=header, verify=False)
    if response.status_code == 200:
        items = response.json()
        app_headers = ["App name", "Family", "ID"]
    else:
        click.echo(
            "Failed to get list of Apps " + str(response.text))
        exit()
    
    table = list()
    cli = cmd.Cmd()

    for item in items['data']:
        tr = [item['name'], item['family'], item['appId']]
        table.append(tr)

    click.echo(tabulate.tabulate(table, app_headers, tablefmt="fancy_grid"))



# ----------------------------------------------------------------------------------------------------
# Authenticate with vManage
# ----------------------------------------------------------------------------------------------------

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

jsessionid = get_jsessionid(vmanage_host, vmanage_port, vmanage_username, vmanage_password)
token = get_token(vmanage_host, vmanage_port, jsessionid)

if token is not None:
    header = {'Content-Type': "application/json",
              'Cookie': jsessionid, 'X-XSRF-TOKEN': token}
else:
    header = {'Content-Type': "application/json", 'Cookie': jsessionid}

base_url = "https://%s:%s/dataservice" % (vmanage_host, vmanage_port)


# ----------------------------------------------------------------------------------------------------
# Run commands
# ----------------------------------------------------------------------------------------------------

cli.add_command(app_list)
cli.add_command(app_list_2)
cli.add_command(qosmos_list)

if __name__ == "__main__":
    cli()

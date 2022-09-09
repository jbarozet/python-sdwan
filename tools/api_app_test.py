#!/usr/bin/env python3

import urllib3
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

vmanage_url = 'https://44.196.44.132'


def status(r):
    if r.status_code == 200:
        print(
            f"{r.request.path_url}; token:{'X-XSRF-TOKEN' in r.request.headers}; items:{len(r.json()['data'])}")
    else:
        print(
            f"{r.request.path_url}; token:{'X-XSRF-TOKEN' in r.request.headers}; code {r.status_code}")


def version():
    r = requests.get(vmanage_url + '/dataservice/client/about',
                     cookies=jar, headers=headers, verify=False)
    about_json = r.json()
    if 'data' in about_json:
        if "version" in about_json['data']:
            print('Version {}'.format(about_json['data']['version']))
        if "applicationVersion" in about_json['data']:
            print('LongVersion {}'.format(
                about_json['data']['applicationVersion']))
        if "applicationServer" in about_json['data']:
            print('Server {}\n'.format(
                about_json['data']['applicationServer']))


print("Login... ", end='')
r = requests.post(vmanage_url + '/dataservice/j_security_check', verify=False,
                  data={'j_username': "admin", 'j_password': "Fun_Nfvis1"})

if r.status_code == 200:
    print(r.status_code, end='')
    if r._content == b'':
        jar = r.cookies
        print(' OK')
        r = requests.get(vmanage_url + '/dataservice/client/token',
                         cookies=jar, verify=False)
        if r.status_code == 200:
            #            print("Token: ", end='')
            #            print(r._content)
            headers = {'X-XSRF-TOKEN': r._content}
            version()

            r = requests.get(vmanage_url + '/dataservice/device/dpi/qosmos/applications',
                             cookies=jar, verify=False)
            status(r)
            r = requests.get(vmanage_url + '/dataservice/device/dpi/qosmos/applications',
                             cookies=jar, headers=headers, verify=False)
            status(r)

            r = requests.get(vmanage_url + '/dataservice/device/dpi/supported-applications',
                             cookies=jar, verify=False)
            status(r)
            r = requests.get(vmanage_url + '/dataservice/device/dpi/supported-applications',
                             cookies=jar, headers=headers, verify=False)
            status(r)

            r = requests.get(vmanage_url + '/dataservice/device/dpi/qosmos-static/applications',
                             cookies=jar, verify=False)
            status(r)
            r = requests.get(vmanage_url + '/dataservice/device/dpi/qosmos-static/applications',
                             cookies=jar, headers=headers, verify=False)
            status(r)

            r = requests.get(vmanage_url + '/dataservice/device/dpi/common/applications',
                             cookies=jar, verify=False)
            status(r)
            r = requests.get(vmanage_url + '/dataservice/device/dpi/common/applications',
                             cookies=jar, headers=headers, verify=False)
            status(r)

            r = requests.get(vmanage_url + '/dataservice/device/dpi/application-mapping',
                             cookies=jar, verify=False)
            status(r)
            r = requests.get(vmanage_url + '/dataservice/device/dpi/application-mapping',
                             cookies=jar, headers=headers, verify=False)
            status(r)

            r = requests.get(vmanage_url + '/dataservice/device/dpi/nbar/applications',
                             cookies=jar, verify=False)
            status(r)
            r = requests.get(vmanage_url + '/dataservice/device/dpi/nbar/applications',
                             cookies=jar, headers=headers, verify=False)
            status(r)

        r = requests.get(vmanage_url + '/logout', cookies=jar,
                         verify=False)
        print('Logout')

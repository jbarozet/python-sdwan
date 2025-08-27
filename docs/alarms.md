# Alarms APIs

[Cisco IOS XE Catalyst SD-WAN Alarms Guide](https://www.cisco.com/c/en/us/td/docs/routers/sdwan/alarms-reference-guide/cisco-ios-xe-catalyst-sd-wan-alarms-guide/sd-wan-alarms-guide.html)

## Notes

With our current (Viptela) API monitoring solution, we are currently using both **rulename** and **component** fields to specifically group and correlate events for our ITOM platform to reduce ticket noise, my concern is that since there are a number of new alarms then there could also be new variables to consider.

We have been able to find the component variables list using /event/component/keyvalue API, but having trouble finding an equivalent variables list for "rulename".

Would you have a list of all the variables that can be returned in the "rulename" field? (highlighted in the sample JSON response below).

The closest I've been able to find is using the /event/types/keyvalue endpoint, are they the same values? if so we can use those.

## TL/DR

Get alarms: `GET https://{{vmanage}}:{{port}}/dataservice/alarms`

Find the component variables: `GET https://<>/dataservice/event/component/keyvalue`

Find the event names (rulenames): `GET https://<>/dataservice/event/types/keyvalue`

Get all possible values for alarms, and severity mapping: `GET https://{{vmanage}}:{{port}}/dataservice/alarms/severitymappings`

## Get Alarms

`GET https://{{vmanage}}:{{port}}/dataservice/alarms` endpoint:

Example:

```json
    "data": [
        {
            "suppressed": false,
            "devices": [
                {
                    "system-ip": "10.10.1.15"
                }
            ],
            "eventname": "memory-usage",
            "type": "memory-usage",
            "rulename": "memory-usage",
            "component": "System",
            "entry_time": 1752550188330,
            "statcycletime": 1752549967210,
            "message": "System memory usage is above 93%",
            "severity": "Critical",
            "severity_number": 1,
            "uuid": "36055fd8-b802-495e-88f8-de80f00bf6fd",
            "values": [
                {
                    "system-ip": "10.10.1.15",
                    "host-name": "site2-cedge01",
                    "memory-status": "usage-critical"
                }
            ],
            "rule_name_display": "Memory_Usage",
            "receive_time": 1752550188329,
            "values_short_display": [
                {
                    "host-name": "site2-cedge01",
                    "system-ip": "10.10.1.15",
                    "memory-status": "usage-critical"
                }
            ],
            "system_ip": "10.10.1.15",
            "acknowledged": false,
            "active": true,
            "tenant": "default",
            "id": "AZgMIaUvQA2v7zEucE-M"
        },
 ```

Bulk API to collect alarms:

`GET https://{{vmanage}}:{{port}}/dataservice/data/device/statistics/alarm?startDate={{startDate}}&endDate={{endDate}}&timeZone={{timeZone}}&count={{count}}"

## Components

Find the component variables (Policy, NAT, BFD, APP-Route, System, Control...)

The following endoint returns components:

`GET https://<>/dataservice/event/component/keyvalue`

Example of response (20.18):

```json
{
  "header": {
    "generatedOn": 1756284947995
  },
  "data": [
    {
      "key": "Policy",
      "value": "Policy"
    },
    {
      "key": "Nat",
      "value": "Nat"
    },
    {
      "key": "CRYPTO",
      "value": "CRYPTO"
    },
    {
      "key": "BFD",
      "value": "BFD"
    },
    {
      "key": "App-Route",
      "value": "App-Route"
    },
    {
      "key": "Nwpi",
      "value": "Nwpi"
    },
    {
      "key": "Configuration-db",
      "value": "Configuration-db"
    },
    {
      "key": "Security",
      "value": "Security"
    },
    {
      "key": "System",
      "value": "System"
    },
    {
      "key": "Control",
      "value": "Control"
    },
    {
      "key": "security",
      "value": "security"
    },
    {
      "key": "VPN",
      "value": "VPN"
    },
    {
      "key": "Hardware",
      "value": "Hardware"
    },
    {
      "key": "CloudExpress",
      "value": "CloudExpress"
    },
    {
      "key": "cloudDock",
      "value": "cloudDock"
    },
    {
      "key": "Firmware",
      "value": "Firmware"
    },
    {
      "key": "NHRP",
      "value": "NHRP"
    },
    {
      "key": "Device",
      "value": "Device"
    },
    {
      "key": "Statistics",
      "value": "Statistics"
    },
    {
      "key": "OMP",
      "value": "OMP"
    },
    {
      "key": "PIM",
      "value": "PIM"
    },
    {
      "key": "compliance",
      "value": "compliance"
    },
    {
      "key": "Software",
      "value": "Software"
    },
    {
      "key": "Bridge",
      "value": "Bridge"
    },
    {
      "key": "OSPF",
      "value": "OSPF"
    }
  ]
}
```

## Types (event names, rulenames)

“rulename” possible values, I believe we can get the list using:

https://{{vmanage}}:{{port}}/dataservice/event/types/keyvalue

double check <https://sdwan-git.cisco.com/sdwan/nms/blob/next/server/src/main/java/com/viptela/vmanage/server/event/event_config_category.json>
This is the event definition that API returns.

```json
{
  "header": {
    "generatedOn": 1756285032643
  },
  "data": [
    {
      "key": "system-software-install-change",
      "value": "system-software-install-change"
    },
    {
      "key": "system-software-install-status",
      "value": "system-software-install-status"
    },
    {
      "key": "system-firmware-install-status",
      "value": "system-firmware-install-status"
    },
    {
      "key": "im-event",
      "value": "im-event"
    },
    {
      "key": "utd-notification",
      "value": "utd-notification"
    },
    {
      "key": "utd-update",
      "value": "utd-update"
    },
    {
      "key": "utd-ips-alert",
      "value": "utd-ips-alert"
    },

    [cut for brevity]

  ]
}

```

## Severity Mappings

Get all possible values for alarms, and the corresponding severity mapping:

`GET https://{{vmanage}}:{{port}}/dataservice/alarms/severitymappings`

Example of response (20.18) - Extract:

```json
{
  "header": {
    "generatedOn": 1756285196961
  },
  "data": [
    {
      "key": "Major",
      "value": "Major",
      "associatedAlarms": [
        {
          "key": "WANI_Recommendation",
          "value": "WANI Recommendation"
        },
        {
          "key": "ISE",
          "value": "ISE"
        },
        {
          "key": "SD-AVC Cloud Connector Credentials Error",
          "value": "SD-AVC Cloud Connector Credentials Error"
        },
        {
          "key": "Create PxGrid Account failed",
          "value": "Create PxGrid Account failed"
        },
        {
          "key": "Tracker_State_Change",
          "value": "Tracker State Change"
        },
        {
          "key": "Multicloud",
          "value": "Multicloud"
        },

        [cut for brevity]

        {
          "key": "Disk_Usage",
          "value": "Disk Usage"
        },
        {
          "key": "Memory_Usage",
          "value": "Memory Usage"
        },

        [cut for brevity]

```
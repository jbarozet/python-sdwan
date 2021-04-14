# Monitor App Route Stats


## INSTALLATION

### Requirements
To use this application you will need:
- Python 3.7+
- Cisco SD-WAN 18.3+

### Install and Setup
Clone the code to local machine.

```
git clone https://github.com/suchandanreddy/sdwan-apis.git
cd sdwan-apis/code_samples
```

### Setup Python Virtual Environment (requires Python 3.7+)

```bash
python3.7 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

### Setup local environment variables to provide vManage instance details.

Examples:
```
export vmanage_host=<vmanage-ip>
export vmanage_port=<vmanage-port>
export vmanage_username=<username>
export vmanage_password=<password>
```


## USAGE

### Aggregation API Query Payload
Aggregation API query is created using below constructs
- Query Conditions
- Aggregation components:
    - Field
    - Histogram
    - Metrics

For example, we need to first define Query Conditions(rules) Based on these rules the data records are extracted from vManage. Some of the common supported rules are to select based on stats entry_time to get statistics in specific intervals of time, then use various query fields like local system-ip, local color, remote color to retrieve the records for specific vEdge routers transport circuits in that time interval.

Once the query conditions are determined, you then provide the fields, histogram and metrics, which determine how data is aggregated.


### Commands available

```
# python monitor-app-route-stats.py
Usage: monitor-app-route-stats.py [OPTIONS] COMMAND [ARGS]...

  Command line tool for monitoring Application Aware Routing
  Statistics(Latency/Loss/Jitter/vQoE Score).

Options:
  --help  Show this message and exit.

Commands:
  approute-fields  Retrieve App route Aggregation API Query fields.
  approute-report  Create Average Approute statistics report.
  approute-stats   Create Average Approute statistics for all tunnels...

#
```

### Query fields

Example
```
# python monitor-app-route-stats.py approute-fields
vdevice_name(string)  local_system_ip(string)   src_ip(string)    loss_percentage(number)  name(string)
host_name(string)     remote_system_ip(string)  dst_ip(string)    jitter(number)           loss(number)
device_model(string)  local_color(string)       src_port(number)  tx_pkts(number)
statcycletime(date)   remote_color(string)      dst_port(number)  rx_pkts(number)
entry_time(date)      proto(string)             total(number)     tx_octets(number)
vip_idx(number)       window(number)            latency(number)   rx_octets(number)

#
```


### Example-1 - approute-stats

The following example query retrieves average latency/loss/jitter and vqoe score for the last hour for all tunnels between routers with provided local and remote system-ip.

Code snippet:
```
{
  "query": {
    "condition": "AND",
    "rules": [
      {
        "value": [
          "1"
        ],
        "field": "entry_time",
        "type": "date",
        "operator": "last_n_hours"
      },
      {
        "value": [
          "<Router-1 System-IP>"
        ],
        "field": "local_system_ip",
        "type": "string",
        "operator": "in"
      },
      {
        "value": [
          "<Router-2 System-IP>"
        ],
        "field": "remote_system_ip",
        "type": "string",
        "operator": "in"
      }
    ]
  },
  "aggregation": {
    "field": [
      {
        "property": "name",
        "sequence": 1,
        "size": 6000
      }
    ],
    "metrics": [
      {
        "property": "loss_percentage",
        "type": "avg"
      },
      {
        "property": "vqoe_score",
        "type": "avg"
      },
      {
        "property": "latency",
        "type": "avg"
      },
      {
        "property": "jitter",
        "type": "avg"
      }
    ]
  }
}
```

Sample response:
```
# monitor-app-route-stats python monitor-app-route-stats.py approute-stats
Enter Router-1 System IP address : 10.0.0.108
Enter Router-2 System IP address : 10.0.0.101

Average App route statistics between 10.0.0.108 and 10.0.0.101 for last 1 hour

╒═══════════════════════════════════════════════════════╤══════════════╤═══════════╤═══════════════════╤══════════╕
│ Tunnel name                                           │   vQoE score │   Latency │   Loss percentage │   Jitter │
╞═══════════════════════════════════════════════════════╪══════════════╪═══════════╪═══════════════════╪══════════╡
│ 10.0.0.108:public-internet-10.0.0.101:public-internet │            8 │     27.25 │           0.18825 │        0 │
╘═══════════════════════════════════════════════════════╧══════════════╧═══════════╧═══════════════════╧══════════╛

Average App route statistics between 10.0.0.101 and 10.0.0.108 for last 1 hour

╒═══════════════════════════════════════════════════════╤══════════════╤═══════════╤═══════════════════╤══════════╕
│ Tunnel name                                           │   vQoE score │   Latency │   Loss percentage │   Jitter │
╞═══════════════════════════════════════════════════════╪══════════════╪═══════════╪═══════════════════╪══════════╡
│ 10.0.0.101:public-internet-10.0.0.108:public-internet │           10 │        27 │                 0 │        0 │
╘═══════════════════════════════════════════════════════╧══════════════╧═══════════╧═══════════════════╧══════════╛
#
```





### Example-2 - approute-report

The following query retrieves the application route statistics between the start date and end date as query conditions so you get the average latency/loss/jitter between those two intervals.
(Note that only the UTC timezone is supported in query conditions so you need to convert the user input to UTC timezone if needed)

Here, the statistics are aggregated in 24 hour intervals so with that you can get a report of statistics for provided start and end dates with the average of statistics for 24 hour interval.

Code snippet:
```
{
      "query": {
          "condition": "AND",
          "rules": [
          {
              "value": [
                        start_date+"T00:00:00 UTC",
                        end_date+"T23:59:59 UTC"
                       ],
              "field": "entry_time",
              "type": "date",
              "operator": "between"
          },
          {
              "value": [
                      hub["system_ip"]
                      ],
              "field": "local_system_ip",
              "type": "string",
              "operator": "in"
          }
          ]
      },
      "aggregation": {
          "field": [
          {
              "property": "name",
              "size": 6000,
              "sequence": 1
          },
          {
              "property": "proto",
              "sequence": 2
          },
          {
              "property": "local_system_ip",
              "sequence": 3
          },
          {
              "property": "remote_system_ip",
              "sequence": 4
          }
          ],
          "histogram": {
          "property": "entry_time",
          "type": "hour",
          "interval": 24,
          "order": "asc"
          },
          "metrics": [
          {
              "property": "latency",
              "type": "avg"
          },
          {
              "property": "jitter",
              "type": "avg"
          },
          {
              "property": "loss_percentage",
              "type": "avg"
          },
          {
              "property": "vqoe_score",
              "type": "avg"
          }
          ]
      }
      }
      ```
# USAGE

## Aggregation API Query Payload

Aggregation API query is created using below constructs

- Query Conditions
- Aggregation components:
  - Field
  - Histogram
  - Metrics

For example, we need to first define Query Conditions(rules) Based on these rules the data records are extracted from vManage. Some of the common supported rules are to select based on stats entry_time to get statistics in specific intervals of time, then use various query fields like local system-ip, local color, remote color to retrieve the records for specific vEdge routers transport circuits in that time interval.

Once the query conditions are determined, you then provide the fields, histogram and metrics, which determine how data is aggregated.

## Commands available

```bash
# python monitor-app-route-stats.py
Usage: app.py [OPTIONS] COMMAND [ARGS]...

  Command line tool to monitor Applications

Options:
  --help  Show this message and exit.

Commands:
  app-list Retrieve NBAR application list
  qosmos-list Retrieve Qosmos application list
  approute-fields  Retrieve App route Aggregation API Query fields.
  approute-stats   Create Average Approute statistics for all tunnels...

#
```

## Example-1 - Query fields

Example

```bash
# python monitor-app-route-stats.py approute-fields
vdevice_name(string)  local_system_ip(string)   src_ip(string)    loss_percentage(number)  name(string)
host_name(string)     remote_system_ip(string)  dst_ip(string)    jitter(number)           loss(number)
device_model(string)  local_color(string)       src_port(number)  tx_pkts(number)
statcycletime(date)   remote_color(string)      dst_port(number)  rx_pkts(number)
entry_time(date)      proto(string)             total(number)     tx_octets(number)
vip_idx(number)       window(number)            latency(number)   rx_octets(number)

#
```

## Example-2 - approute-stats

The following example query retrieves average latency/loss/jitter and vqoe score for the last hour for all tunnels between routers with provided local and remote system-ip.

Code snippet:

```json
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

```bash
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

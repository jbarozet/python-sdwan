# SD-WAN Manager API Examples

## Install and Setup

Clone the code to local machine.

```shell
git clone https://github.com/jbarozet/python-sdwan.git
```

## Setup Python Virtual Environment

```bash
uv sync
source venv/bin/activate
```

## Setup local environment variables to provide vManage instance details.

Example for MacOSX:

```bash
export vmanage_host=<vmanage-ip>
export vmanage_port=<vmanage-port>
export vmanage_username=<username>
export vmanage_password=<password>
```

Example for Windows

```shell
set vmanage_host=<vmanage-ip>
set vmanage_port=<vmanage-port>
set vmanage_username=<username>
set vmanage_password=<password>
```

## Documentation

Refer to:

- [Getting Started](./01-Getting-Started.md)
- [Authentication](./02-Authentication.md)
- [Usage](./03-Usage.md)

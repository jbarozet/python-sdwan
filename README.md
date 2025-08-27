# SD-WAN Manager API Examples

This section provides practical Python examples demonstrating authentication to SD-WAN Manager and subsequent API interactions.
Please note these examples are for demonstration purposes only and not production-ready.

## Install and Setup

Clone the code to local machine.

```shell
git clone https://github.com/jbarozet/python-sdwan.git
```

## Setup Python Virtual Environment

Install uv by running the following command in Terminal:

`curl -LsSf https://astral.sh/uv/install.sh | sh`

Initialize and install dependancies:

```bash
cd python-sdwan
uv venv .venv
source .venv/bin/activate
uv pip install .
```

## Setup local environment variables to provide manager instance details

You need to define the SD-WAN Manager parameters to authenticate.

Example for MacOSX:

```bash
export manager_host=10.0.0.100
export manager_port=443
export manager_username=sdwan
export manager_password=mysuperpassword
```

Example for Windows

```shell
set manager_host=10.0.0.100
set manager_port=443
set manager_username=sdwan
set manager_password=mysuperpassword
```

The easiest way to run the tool is to provide all the lab variables in a init file and source that file.
The example file below contains all the variables required to run all the tasks.

```shell
% cat init.sh
export manager_host=10.0.0.100
export manager_port=443
export manager_username=sdwan
export manager_password=mysuperpassword
% source init.sh
```

## Documentation

Refer to:

- [Getting Started](./docs/01-Getting-Started.md)
- [Authentication](./docs/02-Authentication.md)
- [Usage](./docs/monitoring.md)

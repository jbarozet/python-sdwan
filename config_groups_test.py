#! /usr/bin/env python
# =========================================================================
# Python Script for SD-WAN Manager APIs
#
# SD-WAN/SD-Routing UX 2.0 Configuration
# Config Groups, Feature Profiles, Policy Groups
#
# =========================================================================

import logging
import os
from datetime import datetime

# Import the new unified Manager class and the credentials function
from config_groups import ConfigGroupTable, SDRoutingProfileTable, SDWANProfileTable

# Import the new unified Manager class and the credentials function
from manager import Manager, get_manager_credentials_from_env
from prompt import Prompt


# -----------------------------------------------------------------------------
def help():
    print("Define vManage parameters in .env file")
    exit(1)


# -----------------------------------------------------------------------------
def list_groups():
    config_group_table.display()


# -----------------------------------------------------------------------------
def save_groups():
    config_group_table.save_to_file()


# -----------------------------------------------------------------------------
def access_groups():
    config_group_table.access_data()


# -----------------------------------------------------------------------------
def list_sdwan_profiles():
    sdwan_profiles_table.list()


# -----------------------------------------------------------------------------
def save_sdwan_profiles():
    sdwan_profiles_table.save_profiles()


# -----------------------------------------------------------------------------
def list_sdrouting_profiles():
    sdrouting_profiles_table.list()


# -----------------------------------------------------------------------------
def save_sdrouting_profiles():
    sdrouting_profiles_table.save_profiles()


# -----------------------------------------------------------------------------
def list_sdwan_profile_categories():
    sdwan_profiles_table.list_categories()


# -----------------------------------------------------------------------------
def list_sdrouting_profile_categories():
    sdrouting_profiles_table.list_categories()


# -----------------------------------------------------------------------------
def quit():
    print("Quitting ...")
    # manager.close()
    raise SystemExit


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)s (%(asctime)s): %(message)s (Line: %(lineno)d [%(filename)s])",
        datefmt="%d/%m/%Y %I:%M:%S %p",
        level=logging.INFO,
    )

    print("\n--- Authenticating to SD-WAN Manager ---")
    host, port, user, password = get_manager_credentials_from_env()
    manager = Manager(host, port, user, password)

    # Collecting Config Groups and Feature Profiles from SD-WAN Manager
    config_group_table = ConfigGroupTable(manager)
    sdwan_profiles_table = SDWANProfileTable(manager)
    sdrouting_profiles_table = SDRoutingProfileTable(manager)

    # Menu
    options = {
        "List Configuration Groups": list_groups,
        "List SD-WAN Feature Profiles": list_sdwan_profiles,
        "List SD-Routing Feature Profiles": list_sdrouting_profiles,
        "List SD-WAN Feature Profiles per category": list_sdwan_profile_categories,
        "List SD-Routing Feature Profiles per category": list_sdrouting_profile_categories,
        "Save Configuration Groups to files": save_groups,
        "Save SD-WAN Feature Profiles to files": save_sdwan_profiles,
        "Save SD-Routing Feature Profiles to files": save_sdrouting_profiles,
        "Example: Accessing data from the first ConfigGroup object": access_groups,
        "Quit": quit,
    }

    while True:
        print("")
        Prompt.dict_menu(options)

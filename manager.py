# =========================================================================
# Catalyst WAN Python scripts examples
#
# SD-WAN/SD-Routing UX 2.0 Device Config
# Using Config Group and Feature Profiles
#
# Description:
#   Get config-groups and feature profiles
#   Get devices associated with config-group
#   Get deployment values
#   Save everything under output folder
#
# Output folder hierarchy:
#   config_groups
#       associated
#       groups
#       values
#
#   feature_profiles
#       cli
#       system
#       transport
#       service
#       policy-object
#
# =========================================================================

import json
import os
from datetime import datetime
from typing import Optional

import requests

# Import the new function from session.py
from session import get_authenticated_session_details


# -----------------------------------------------------------------------------
def save_json(
    payload: dict, filename: str = "payload", directory: str = "./output/payloads/"
):
    """Save json response payload to a file

    Args:
        payload: JSON response payload
        filename: filename for saved files (default: "payload")
    """

    filename = "".join([directory, f"{filename}.json"])

    if not os.path.exists(directory):
        print(f"Creating folder {directory}")
        os.makedirs(directory)  # Create the directory if it doesn't exist

    # Dump entire payload to file
    with open(filename, "w") as file:
        json.dump(payload, file, indent=4)


# -----------------------------------------------------------------------------
class MyManager:
    def __init__(self):
        self.status = False
        self.profile_id_table = []
        self.config_group_table = []

        # Get the authenticated session object and base URL
        self.session, self.base_url = get_authenticated_session_details()

        print(f"Base URL: {self.base_url}")
        print(f"Session headers: {self.session.headers}")  # Show configured headers

        self.status = True

    def _api_get(self, path: str, params: Optional[dict] = None):
        """
        Helper method to make a GET request to the SD-WAN Manager API.
        Handles URL construction, uses the authenticated session, and checks for HTTP errors.

        Args:
            path (str): The API endpoint path (e.g., "/v1/config-group/").
            params (dict, optional): Dictionary of query parameters. Defaults to None.

        Returns:
            dict: The JSON response from the API.

        Raises:
            requests.exceptions.RequestException: If the API call fails.
        """
        url = self.base_url + path
        # print(f"Making GET request to: {url}") # Uncomment for verbose debugging
        response = self.session.get(url=url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        return response.json()

    # def close(self): # No longer strictly necessary as session handles its own closing on program exit
    #     self.session.close()


# -----------------------------------------------------------------------------
class SDRoutingFeatureProfile:
    """
    Helper class to fetch detailed payload for a single SD-Routing feature profile.
    """

    payload = None

    def __init__(
        self, manager, id, name, solution, type, createdby, lastupdatedby, lastupdatedon
    ):
        self.manager = manager
        self.id = id
        self.name = name
        self.solution = solution
        self.type = type
        self.createdby = createdby
        self.lastupdatedby = lastupdatedby
        self.lastupdatedon = lastupdatedon

        url_base = "/v1/feature-profile/sd-routing/"

        match self.type:
            case "system":
                urlp = url_base + "system/"
            case "transport":
                urlp = url_base + "transport/"
            case "service":
                urlp = url_base + "service/"
            case "cli":
                urlp = url_base + "cli/"
            # case "policy-object": # This case was commented out in original, keeping it that way
            #     urlp = url_base + "policy-object/"
            case _:
                print(f"{self.type} type not supported for SD-Routing feature profile")
                return

        # Get profile_id payload
        # NOTE: details option has been added in 20.12
        path = urlp + self.id
        params = {"details": "true"}
        print(f"Fetching details for profile ID {self.id} from {path}")
        try:
            self.payload = self.manager._api_get(path, params=params)
            self.profile_name = self.payload["profileName"]
            self.profile_type = self.payload["profileType"]
            self.solution = self.payload["solution"]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching details for profile ID {self.id}: {e}")
            self.payload = None  # Indicate failure to fetch


# -----------------------------------------------------------------------------
class SDRoutingProfileTable:
    def __init__(self, manager: MyManager):
        self.manager = manager
        self.profiles_table = []  # This will store generic Profile objects

        api_path_summary = "/v1/feature-profile/sd-routing/"

        # Get list of profiles (summary)
        try:
            summary_data = self.manager._api_get(api_path_summary)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching SD-Routing profile summary: {e}")
            return  # Exit if summary data cannot be fetched

        # For each summary item, fetch full details and create a Profile object
        for item in summary_data:
            profile_id = item["profileId"]
            profile_name = item["profileName"]
            profile_solution = item["solution"]
            profile_type = item["profileType"]
            profile_createdby = item["createdBy"]
            profile_lastupdated = item["lastUpdatedBy"]
            profile_lastUpdatedOn = item["lastUpdatedOn"]

            # Use SDRoutingFeatureProfile to fetch the detailed payload
            sdrouting_feature_profile_fetcher = SDRoutingFeatureProfile(
                self.manager,
                profile_id,
                profile_name,
                profile_solution,
                profile_type,
                profile_createdby,
                profile_lastupdated,
                profile_lastUpdatedOn,
            )

            if not sdrouting_feature_profile_fetcher.payload:
                print(
                    f"Skipping profile ID {profile_id} due to unsupported type or fetch error."
                )
                continue

            full_profile_payload = sdrouting_feature_profile_fetcher.payload

            # Now, use the full_profile_payload to create a generic Profile object
            profile = Profile(
                id=full_profile_payload.get("profileId"),
                name=full_profile_payload.get("profileName"),
                solution=full_profile_payload.get("solution"),
                type=full_profile_payload.get("profileType"),
                description=full_profile_payload.get("description"),
                lastUpdatedBy=full_profile_payload.get("lastUpdatedBy"),
                lastUpdatedOn=full_profile_payload.get("lastUpdatedOn"),
                createdBy=full_profile_payload.get("createdBy"),
                createdOn=full_profile_payload.get("createdOn"),
                profileParcelCount=full_profile_payload.get("profileParcelCount"),
                origin=full_profile_payload.get("origin"),
            )
            self.profiles_table.append(profile)

    def list(self):
        print("\n--- SD-Routing Feature Profiles\n")
        for profile in self.profiles_table:
            profile.display()  # Use the display method of the generic Profile object

    def list_categories(self):
        print("\n--- SD-Routing Feature Profiles per category\n")

        categories = [
            "system",
            "transport",
            "service",
            "cli",
            "policy-object",
        ]

        for category_item in categories:
            print(f"\n--- Category: {category_item.upper()} ---")
            found_in_category = False
            for profile in self.profiles_table:
                if profile.type == category_item:
                    profile.display()
                    found_in_category = True
            if not found_in_category:
                print(f"    No profiles found for category '{category_item}'.")

    def save_profiles(self, directory="output/feature_profiles/sdrouting"):
        print(f"\n--- Saving SD-Routing Feature Profiles in {directory}\n")

        for profile in self.profiles_table:
            profile.save_to_file(
                directory
            )  # Use the save_to_file method of the generic Profile object


# -----------------------------------------------------------------------------
class SDWANFeatureProfile:
    """
    Helper class to fetch detailed payload for a single SD-WAN feature profile.
    """

    payload = None

    def __init__(
        self, manager, id, name, solution, type, createdby, lastupdatedby, lastupdatedon
    ):
        self.manager = manager
        self.id = id
        self.name = name
        self.solution = solution
        self.type = type
        self.createdby = createdby
        self.lastupdatedby = lastupdatedby
        self.lastupdatedon = lastupdatedon

        print(f"Fetching details for profile {self.name} ({self.id})")

        api_url = "/v1/feature-profile/sdwan/"

        match self.type:
            case "system":
                urlp = api_url + "system/"
            case "transport":
                urlp = api_url + "transport/"
            case "service":
                urlp = api_url + "service/"
            case "cli":
                urlp = api_url + "cli/"
            # case "policy-object": # This case was commented out in original, keeping it that way
            #     urlp = api_url + "policy-object/"
            case _:
                print(f"{self.type} type not supported for SD-WAN feature profile")
                return

        # Get profile_id payload
        # NOTE: details option has been added in 20.12
        path = urlp + self.id
        params = {"details": "true"}
        try:
            self.payload = self.manager._api_get(path, params=params)
            self.profile_name = self.payload.get("profileName")
            self.profile_type = self.payload.get("profileType")
            self.solution = self.payload.get("solution")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching details for profile {self.name} ({self.id}): {e}")
            self.payload = None  # Indicate failure to fetch


# -----------------------------------------------------------------------------
class SDWANProfileTable:
    def __init__(self, manager: MyManager):
        self.manager = manager
        self.profiles_table = []  # This will now store generic Profile objects

        api_path_summary = "/v1/feature-profile/sdwan/"

        print("\n--- Collecting Feature Profiles ---")

        # Get list of profiles (summary)
        try:
            summary_data = self.manager._api_get(api_path_summary)
            save_json(summary_data, "2_profile_table")  # save payload response
        except requests.exceptions.RequestException as e:
            print(f"Error fetching SD-WAN profile summary: {e}")
            return  # Exit if summary data cannot be fetched

        # For each summary item, fetch full details and create a Profile object
        for item in summary_data:
            profile_id = item["profileId"]
            profile_name = item["profileName"]
            profile_solution = item["solution"]
            profile_type = item["profileType"]
            profile_createdby = item["createdBy"]
            profile_lastupdated = item["lastUpdatedBy"]
            profile_lastUpdatedOn = item["lastUpdatedOn"]

            # Use SDWANFeatureProfile to fetch the detailed payload
            # This class makes the API call for details of a single profile
            sdwan_feature_profile_fetcher = SDWANFeatureProfile(
                self.manager,
                profile_id,
                profile_name,
                profile_solution,
                profile_type,
                profile_createdby,
                profile_lastupdated,
                profile_lastUpdatedOn,
            )
            if not sdwan_feature_profile_fetcher.payload:
                print(
                    f"Skipping profile {profile_name} ({profile_id}) due to unsupported type or fetch error."
                )
                continue
            full_profile_payload = sdwan_feature_profile_fetcher.payload
            save_json(full_profile_payload, profile_name)

            # Now, use the full_profile_payload to create a generic Profile object
            # Using .get() for robustness in case a key is missing in the payload
            profile = Profile(
                id=full_profile_payload.get("profileId"),
                name=full_profile_payload.get("profileName"),
                solution=full_profile_payload.get("solution"),
                type=full_profile_payload.get("profileType"),
                description=full_profile_payload.get("description"),
                lastUpdatedBy=full_profile_payload.get("lastUpdatedBy"),
                lastUpdatedOn=full_profile_payload.get("lastUpdatedOn"),
                createdBy=full_profile_payload.get("createdBy"),
                createdOn=full_profile_payload.get("createdOn"),
                profileParcelCount=full_profile_payload.get("profileParcelCount"),
                origin=full_profile_payload.get("origin"),
            )
            self.profiles_table.append(profile)

    def list(self):
        print("\n--- SD-WAN Feature Profiles\n")
        for profile in self.profiles_table:
            profile.display()  # Use the display method of the generic Profile object

    def list_categories(self):
        print("\n--- SD-WAN Feature Profiles per category\n")

        categories = [
            "system",
            "transport",
            "service",
            "cli",
            "policy-object",
        ]

        for category_item in categories:
            print(f"\n--- Category: {category_item.upper()} ---")
            found_in_category = False
            for profile in self.profiles_table:
                if profile.type == category_item:
                    profile.display()
                    found_in_category = True
            if not found_in_category:
                print(f"    No profiles found for category '{category_item}'.")

    def save_profiles(self, directory="output/feature_profiles/sdwan"):
        print(f"\n--- Saving SD-WAN Feature Profiles in {directory}\n")

        for profile in self.profiles_table:
            profile.save_to_file(directory)


# -----------------------------------------------------------------------------
class Profile:
    def __init__(
        self,
        id,
        name,
        solution,
        type,
        description,
        lastUpdatedBy,
        lastUpdatedOn,
        createdBy,
        createdOn,
        profileParcelCount,
        origin,
    ):
        self.id = id
        self.name = name
        self.solution = solution
        self.type = type
        self.description = description
        self.lastUpdatedBy = lastUpdatedBy
        self.lastUpdatedOn = self._convert_timestamp_to_datetime(lastUpdatedOn)
        self.createdBy = createdBy
        self.createdOn = self._convert_timestamp_to_datetime(createdOn)
        self.profileParcelCount = profileParcelCount
        self.origin = origin

    def _convert_timestamp_to_datetime(self, timestamp):
        """Converts a Unix timestamp (milliseconds) to a datetime object."""
        if timestamp is not None:
            return datetime.fromtimestamp(timestamp / 1000)  # Convert ms to seconds
        return None

    def _convert_datetime_to_timestamp(self, dt_obj):
        """Converts a datetime object to a Unix timestamp (milliseconds)."""
        if dt_obj is not None:
            return int(dt_obj.timestamp() * 1000)
        return None

    def to_dict(self):
        """Converts the Profile object to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "solution": self.solution,
            "type": self.type,
            "description": self.description,
            "lastUpdatedBy": self.lastUpdatedBy,
            "lastUpdatedOn": self._convert_datetime_to_timestamp(self.lastUpdatedOn),
            "createdBy": self.createdBy,
            "createdOn": self._convert_datetime_to_timestamp(self.createdOn),
            "profileParcelCount": self.profileParcelCount,
            "origin": self.origin,
        }

    def save_to_file(self, directory="output/feature_profiles"):
        """
        Saves the Profile object's data to a JSON file.

        Args:
            directory (str): The directory where the file will be saved.
            Defaults to 'output/feature_profiles'.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)  # Create the directory if it doesn't exist

        # Sanitize the name to create a valid filename
        # Replace non-alphanumeric characters (except spaces, dots, underscores) with nothing
        # Then replace spaces with underscores for better filename compatibility
        sanitized_name = "".join(
            c for c in self.name if c.isalnum() or c in (" ", ".", "_", "-")
        ).strip()
        sanitized_name = sanitized_name.replace(" ", "_")

        # Fallback if name becomes empty or invalid after sanitization
        if not sanitized_name:
            filename = f"profile_{self.id}.json"
        else:
            filename = f"{sanitized_name}.json"

        filepath = os.path.join(directory, filename)

        try:
            with open(filepath, "w") as f:
                json.dump(
                    self.to_dict(), f, indent=4
                )  # Use indent=4 for pretty-printing JSON
            print(f"Successfully saved Profile '{self.name}' to '{filepath}'")
        except Exception as e:
            print(f"Error saving Profile '{self.name}' to '{filepath}': {e}")

    def __repr__(self):
        return f"Profile(name='{self.name}', id='{self.id}', type='{self.type}')"

    def display(self):
        """Prints the details of the profile."""
        print(f"> Profile Name ❯ {self.name}")
        print(f"      ID: {self.id}")
        print(f"      Type: {self.type}")
        print(f"      Solution: {self.solution}")
        print(f"      Last Updated On: {self.lastUpdatedOn}")
        print(f"      Created On: {self.createdOn}")
        print(f"      Parcel Count: {self.profileParcelCount}")
        # print("-" * 40)  # Separator for readability


# -----------------------------------------------------------------------------
class ConfigGroup:
    def __init__(
        self,
        id,
        name,
        description,
        source,
        solution,
        lastUpdatedBy,
        lastUpdatedOn,
        createdBy,
        createdOn,
        profiles_data,
        version,
        state,
        devices,
        numberOfDevices,
        numberOfDevicesUpToDate,
        origin,
        copyInfo,
        originInfo,
        topology,
        fullConfigCli,
        iosConfigCli,
        versionIncrementReason,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.source = source
        self.solution = solution
        self.lastUpdatedBy = lastUpdatedBy
        self.lastUpdatedOn = self._convert_timestamp_to_datetime(lastUpdatedOn)
        self.createdBy = createdBy
        self.createdOn = self._convert_timestamp_to_datetime(createdOn)
        self.profiles = []  # Initialize profiles as a list of Profile objects

        if profiles_data and isinstance(profiles_data, list):
            for profile_dict in profiles_data:
                self.profiles.append(
                    Profile(
                        id=profile_dict.get("id"),
                        name=profile_dict.get("name"),
                        solution=profile_dict.get("solution"),
                        type=profile_dict.get("type"),
                        description=profile_dict.get("description"),
                        lastUpdatedBy=profile_dict.get("lastUpdatedBy"),
                        lastUpdatedOn=profile_dict.get("lastUpdatedOn"),
                        createdBy=profile_dict.get("createdBy"),
                        createdOn=profile_dict.get("createdOn"),
                        profileParcelCount=profile_dict.get("profileParcelCount"),
                        origin=profile_dict.get("origin"),
                    )
                )

        self.version = version
        self.state = state
        self.devices = devices
        self.numberOfDevices = numberOfDevices
        self.numberOfDevicesUpToDate = numberOfDevicesUpToDate
        self.origin = origin
        self.copyInfo = copyInfo
        self.originInfo = originInfo
        self.topology = topology
        self.fullConfigCli = fullConfigCli
        self.iosConfigCli = iosConfigCli
        self.versionIncrementReason = versionIncrementReason

    def _convert_timestamp_to_datetime(self, timestamp):
        """Converts a Unix timestamp (milliseconds) to a datetime object."""
        if timestamp is not None:
            return datetime.fromtimestamp(timestamp / 1000)  # Convert ms to seconds
        return None

    def _convert_datetime_to_timestamp(self, dt_obj):
        """Converts a datetime object to a Unix timestamp (milliseconds)."""
        if dt_obj is not None:
            return int(dt_obj.timestamp() * 1000)
        return None

    def to_dict(self):
        """Converts the ConfigGroup object to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "source": self.source,
            "solution": self.solution,
            "lastUpdatedBy": self.lastUpdatedBy,
            "lastUpdatedOn": self._convert_datetime_to_timestamp(self.lastUpdatedOn),
            "createdBy": self.createdBy,
            "createdOn": self._convert_datetime_to_timestamp(self.createdOn),
            "profiles": [
                profile.to_dict() for profile in self.profiles
            ],  # Recursively call to_dict for profiles
            "version": self.version,
            "state": self.state,
            "devices": self.devices,
            "numberOfDevices": self.numberOfDevices,
            "numberOfDevicesUpToDate": self.numberOfDevicesUpToDate,
            "origin": self.origin,
            "copyInfo": self.copyInfo,
            "originInfo": self.originInfo,
            "topology": self.topology,
            "fullConfigCli": self.fullConfigCli,
            "iosConfigCli": self.iosConfigCli,
            "versionIncrementReason": self.versionIncrementReason,
        }

    def save_to_file(self, directory="output/config_groups"):
        """
        Saves the ConfigGroup object's data to a JSON file.

        Args:
            directory (str): The directory where the file will be saved.
            Defaults to 'output_config_groups'.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)  # Create the directory if it doesn't exist

        # Sanitize the name to create a valid filename
        # Replace non-alphanumeric characters (except spaces, dots, underscores) with nothing
        # Then replace spaces with underscores for better filename compatibility
        sanitized_name = "".join(
            c for c in self.name if c.isalnum() or c in (" ", ".", "_", "-")
        ).strip()
        sanitized_name = sanitized_name.replace(" ", "_")

        # Fallback if name becomes empty or invalid after sanitization
        if not sanitized_name:
            filename = f"config_group_{self.id}.json"
        else:
            filename = f"{sanitized_name}.json"

        filepath = os.path.join(directory, filename)

        try:
            with open(filepath, "w") as f:
                json.dump(self.to_dict(), f, indent=4)
            print(f"Successfully saved ConfigGroup '{self.name}' to '{filepath}'")
        except Exception as e:
            print(f"Error saving ConfigGroup '{self.name}' to '{filepath}': {e}")

    def __repr__(self):
        return f"ConfigGroup(name='{self.name}', id='{self.id}', profiles_count={len(self.profiles)})"

    def display(self):
        """Prints the details of the config group and its profiles."""
        print(f"\n= Config Group: {self.name} (ID: {self.id})")
        print(f"  Description: {self.description}")
        print(f"  Solution: {self.solution}")
        print(f"  Last Updated On: {self.lastUpdatedOn}")
        print(f"  Number of Devices: {self.numberOfDevices}")
        print(f"  Number of Devices Up-to-Date: {self.numberOfDevicesUpToDate}")
        print(f"  Profiles ({len(self.profiles)}):")
        if self.profiles:
            for profile in self.profiles:
                profile.display()
        else:
            print("    No profiles associated with this configuration group.")


# -----------------------------------------------------------------------------
class ConfigGroupTable:
    # Initialize a list to store the structured output
    config_groups_objects = []

    def __init__(self, manager: MyManager):
        """
        '/v1/config-group'
        """

        self.manager = manager

        # API endpoint
        api_path = "/v1/config-group/"
        try:
            data = self.manager._api_get(api_path)  # Use the new helper method
            save_json(data, "1_config_group_table")  # save payload response
        except requests.exceptions.RequestException as e:
            print(f"Error fetching config group summary: {e}")
            return  # Exit if data cannot be fetched

        print("\n--- Collecting Config Groups ---")
        # Iterate through the raw data and create ConfigGroup objects
        for group_dict in data:
            # Pass all dictionary items directly to the ConfigGroup constructor
            config_group = ConfigGroup(
                id=group_dict.get("id"),
                name=group_dict.get("name"),
                description=group_dict.get("description"),
                source=group_dict.get("source"),
                solution=group_dict.get("solution"),
                lastUpdatedBy=group_dict.get("lastUpdatedBy"),
                lastUpdatedOn=group_dict.get("lastUpdatedOn"),
                createdBy=group_dict.get("createdBy"),
                createdOn=group_dict.get("createdOn"),
                profiles_data=group_dict.get("profiles"),  # profiles dict
                version=group_dict.get("version"),
                state=group_dict.get("state"),
                devices=group_dict.get("devices"),
                numberOfDevices=group_dict.get("numberOfDevices"),
                numberOfDevicesUpToDate=group_dict.get("numberOfDevicesUpToDate"),
                origin=group_dict.get("origin"),
                copyInfo=group_dict.get("copyInfo"),
                originInfo=group_dict.get("originInfo"),
                topology=group_dict.get("topology"),
                fullConfigCli=group_dict.get("fullConfigCli"),
                iosConfigCli=group_dict.get("iosConfigCli"),
                versionIncrementReason=group_dict.get("versionIncrementReason"),
            )
            self.config_groups_objects.append(config_group)

    def display(self):
        print("\n--- Displaying ConfigGroup Objects ---")
        for cg_obj in self.config_groups_objects:
            cg_obj.display()

    def save_to_file(self, directory="output"):
        print("\n---  Saving ConfigGroup Objects ---")
        for cg_obj in self.config_groups_objects:
            cg_obj.save_to_file()  # Save each config group to its own JSON file

    def access_data(self):
        print("\n--- Example: Accessing data from the first ConfigGroup object ---")
        if self.config_groups_objects:
            first_config_group = self.config_groups_objects[0]
            print(f"First Config Group Name: {first_config_group.name}")
            print(f"First Config Group ID: {first_config_group.id}")
            if first_config_group.profiles:
                print(f"Profiles in '{first_config_group.name}':")
                for profile in first_config_group.profiles:
                    print(
                        f"  - Profile Name: {profile.name}, Type: {profile.type}, ID: {profile.id}"
                    )
                    # You can also access other attributes directly, e.g., profile.lastUpdatedOn
            else:
                print("No profiles found for the first config group.")

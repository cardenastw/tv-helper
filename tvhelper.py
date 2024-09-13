# tvhelper.py
import argparse
import requests
import os
import json

# Constants
TVDB_API_URL = "https://api4.thetvdb.com/v4/"
TVDB_API_KEY = "<ADD_YOURS>"

def authenticate_tvdb():
    """Authenticate with the TVDB API."""
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        'apikey': TVDB_API_KEY,
    }
    response = requests.post(TVDB_API_URL + 'login', headers=headers, json=data)
    response.raise_for_status()
    return response.json()['data']['token']


def get_show_details(tvdb_id, token):
    """Fetch details about the TV show using the TVDB ID."""
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(TVDB_API_URL + f'series/{tvdb_id}/extended', headers=headers)
    response.raise_for_status()
    return response.json()['data']


def create_folder_structure(base_path, show_name, tvdb_id, seasons):
    """Create or rename folder structure for Plex with TVDB ID in folder name."""

    cleaned_show_name = show_name.replace(":", "")
    # Format the expected folder name
    formatted_show_name = f"{cleaned_show_name} {{tvdb-{tvdb_id}}}"
    show_path = os.path.join(base_path, formatted_show_name)

    # Check if a folder exists without the TVDB ID
    existing_folders = [folder for folder in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, folder))]
    possible_existing_folder = next((folder for folder in existing_folders if folder.startswith(cleaned_show_name) and f"{{tvdb-" not in folder), None)

    if possible_existing_folder:
        response = input(f"Folder '{possible_existing_folder}' exists. Is this the correct folder? (yes/no): ").strip().lower()
        if response == 'yes':
            # Option to update the folder name with tvdb ID
            update_response = input(
                f"Do you want to update the folder to '{formatted_show_name}'? (yes/no): ").strip().lower()
            if update_response == 'yes':
                # Rename the existing folder to include the TVDB ID
                old_show_path = os.path.join(base_path, possible_existing_folder)
                print(f"Renaming folder from {possible_existing_folder} to {formatted_show_name}")
                os.rename(old_show_path, show_path)
            else:
                print("Folder not updated.")
        else:
            print("No folder changes made.")

    else:
        print(f"Didn't find a matching directory, creating a new one")
        # Create the new folder with TVDB ID in name
        os.makedirs(show_path, exist_ok=True)

    # Create season folders inside the renamed or newly created show folder
    for season in seasons:
        season_folder = f"Season {str(season).zfill(2)}"
        season_path = os.path.join(show_path, season_folder)
        os.makedirs(season_path, exist_ok=True)

    return show_path


def save_show_details(show_path, show_details, season_episodes):
    """Save show details and episode count to a JSON file."""
    json_data = {
        "show": show_details['name'],
        "tvdb": {
            "id": show_details['id'],
            "overview": show_details.get('overview', 'No overview available'),
            "seasons": {}
        }
    }

    for season, episodes in season_episodes.items():
        json_data['tvdb']['seasons'][f"Season {str(season).zfill(2)}"] = {
            "episode_count": len(episodes),
            "episodes": [{"episodeName": ep['name'], "airedEpisodeNumber": ep['number']} for ep in
                         episodes]
        }

    with open(os.path.join(show_path, 'show_details.json'), 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

def add_series(base_path, tvdb_id):
    token = authenticate_tvdb()
    show_details = get_show_details(tvdb_id, token)

    seasons = set()
    season_episodes = {}

    series_name = show_details['name']

    show_path = create_folder_structure(base_path, series_name, tvdb_id, seasons)
    save_show_details(show_path, show_details, season_episodes)


def main():
    parser = argparse.ArgumentParser(description="TV Helper CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="sub-command help")

    # Define the 'add-series' command
    add_series_parser = subparsers.add_parser('add-series', help="Add a TV series by TVDB ID")
    add_series_parser.add_argument('--tvdb-id', required=True, help="The TVDB ID of the series")
    add_series_parser.add_argument('--base-path', required=True,
                                   help="The base path where the folder should be located")

    args = parser.parse_args()

    if args.command == "add-series":
        add_series(args.base_path, args.tvdb_id)

if __name__ == "__main__":
    main()

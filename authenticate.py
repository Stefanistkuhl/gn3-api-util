import requests
import json
import os
import getpass
import sys


def insert_as_first_val(dict_obj, key, value):
    """Insert a key-value pair as the first item in a dictionary."""
    new_dict = {key: value, **dict_obj}
    return new_dict


def get_user_credentials():
    """Prompt user for username and password."""
    try:
        username = input("Enter the user to login in as:\n")
        password = getpass.getpass("Enter your password:\n")
        return username, password
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error getting credentials: {str(e)}")
        sys.exit(1)


def authenticate_user(username, password, server_url):
    """Authenticate user against GNS3 server and return the response."""
    try:
        url = f'{server_url}/v3/access/users/authenticate'
        headers = {'Content-Type': 'application/json'}
        data = {'username': username, 'password': password}

        response = requests.post(url, json=data, headers=headers, timeout=10)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print("Authentication failed: Invalid username or password.")
            return None
        else:
            print(f"Server returned error: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except requests.exceptions.ConnectionError:
        print(f"Connection error: Could not connect to {server_url}")
        return None
    except requests.exceptions.Timeout:
        print("Connection timeout: The server took too long to respond.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error during authentication: {str(e)}")
        return None


def save_auth_data(auth_data, username, key_file):
    """Save authentication data to a file."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(key_file)), exist_ok=True)

        with open(key_file, "w") as f:
            resp_dic = insert_as_first_val(auth_data, "user", username)
            json.dump(resp_dic, f, indent=4)
            return resp_dic
    except IOError as e:
        print(f"Error writing to file {key_file}: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error saving authentication data: {str(e)}")
        return None


def loadKey(keyFile):
    # add err handeling
    with open(keyFile) as f:
        data = f.read()
    data = json.loads(data)
    return data


def tryKey(key, server_url):
    url = f'{server_url}/v3/access/users/me'
    access_token = key["access_token"]
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(url, headers=headers, timeout=10)
    try:
        if response.status_code == 200:
            return True, response.json()
        elif response.status_code == 401:
            print("User unautorized please log in to refresh your key")
            return False
        else:
            print(f"Server returned error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"Connection error: Could not connect to {server_url}")
        return False
    except requests.exceptions.Timeout:
        print("Connection timeout: The server took too long to respond.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        return False
    except Exception as e:
        print(f"Unexpected error during user check: {str(e)}")
        return False


def authenticate():
    """Main function to run the authentication process."""
    try:
        # Configuration
        key_file = os.path.expanduser("~/.gns3key")
        server_url = 'http://10.21.34.222:3080'

        keyData = loadKey(key_file)
        resp, usr = tryKey(keyData, server_url)
        if resp:
            print("api key works logged in as", usr["username"])
            sys.exit(1)
        # Get user credentials
        username, password = get_user_credentials()

        # Authenticate user
        auth_data = authenticate_user(username, password, server_url)
        if not auth_data:
            sys.exit(1)

        # Save authentication data
        saved_data = save_auth_data(auth_data, username, key_file)
        if saved_data:
            print("Authentication successful. Credentials saved.")
            print(saved_data)
        else:
            print("Failed to save authentication data.")
            sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    authenticate()

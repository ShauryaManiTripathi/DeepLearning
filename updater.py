import paramiko
import os
from pathlib import Path

def read_ssh_key(key_path="~/.ssh/id_rsa.pub"):
    """Read SSH public key from a file."""
    try:
        key_path = os.path.expanduser(key_path)
        with open(key_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Error: SSH public key file not found at {key_path}")
        print("Generate a key pair using: ssh-keygen -t rsa -b 4096")
        return None
    except Exception as e:
        print(f"Error reading SSH key file: {str(e)}")
        return None

def run_ssh_commands(hostname, username, password, commands):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"\nConnecting to {hostname} as {username}...")
        client.connect(hostname=hostname, username=username, password=password)
        
        for command in commands:
            print(f"\nExecuting: {command}")
            stdin, stdout, stderr = client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()
            
            out = stdout.read().decode().strip()
            err = stderr.read().decode().strip()
            
            if out:
                print("Output:", out)
            if err:
                print("Errors:", err)
            
            if exit_status != 0:
                print(f"Warning: Command exited with status {exit_status}")
        
        return True
    
    except Exception as e:
        print(f"Error connecting to {hostname} ({username}): {str(e)}")
        return False
    
    finally:
        client.close()

def read_accounts_from_file(filename):
    accounts = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                if ' - ' in line:
                    username, password = line.strip().split(' - ')
                    accounts.append({"username": username, "password": password})
    except FileNotFoundError:
        print(f"Error: Account file '{filename}' not found.")
    except Exception as e:
        print(f"Error reading accounts file: {str(e)}")
    return accounts

def main():
    # Ask for the path to the public key file
    default_key_path = "GPU.pub"
    key_path = input(f"Enter path to SSH public key file (default: {default_key_path}): ").strip()
    if not key_path:
        key_path = default_key_path

    # Read the SSH key
    ssh_key = read_ssh_key(key_path)
    if not ssh_key:
        return

    # File containing SSH account details
    accounts_file = "successful_logins.txt"
    
    # Read SSH accounts from file
    ssh_accounts = read_accounts_from_file(accounts_file)
    if not ssh_accounts:
        print("No accounts found. Exiting.")
        return

    # Commands to run on each host - with proper permissions
    commands_to_run = [
        "rm -rf ~/.ssh",  # Remove existing .ssh directory
        "mkdir -p ~/.ssh",  # Create new .ssh directory
        "chmod 700 ~/.ssh",  # Set correct directory permissions
        f"echo '{ssh_key}' > ~/.ssh/authorized_keys",  # Write the key
        "chmod 600 ~/.ssh/authorized_keys",  # Set correct file permissions
        "cat ~/.ssh/authorized_keys",  # Verify the key was written
        "ls -la ~/.ssh/"  # Check permissions
    ]

    # Hostname (adjust as needed)
    hostname = "172.16.2.17"

    # Run the commands on each account
    successful = 0
    for account in ssh_accounts:
        if run_ssh_commands(hostname, account["username"], account["password"], commands_to_run):
            successful += 1

    print(f"\nOperation completed. Successfully set up SSH keys for {successful}/{len(ssh_accounts)} accounts.")

if __name__ == "__main__":
    main()
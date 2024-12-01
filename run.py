import subprocess
import time
import logging
import sys
import psutil
import signal
import colorama
from colorama import Fore, Style
from datetime import datetime, time as dt_time, timedelta
from cryptography.fernet import Fernet
import ast
import os
from getpass import getpass

# Initialize colorama
colorama.init()

# Set up logging
logging.basicConfig(filename='ann_restart.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Multiple time intervals (24-hour format)
time_intervals = [
    ((11, 30), (13, 30)),    # 12:00 AM to 9:00 AM
    ((16, 30), (8, 30)) # 5:30 PM to 11:59 PM
]

def decrypt_command(encrypted_command, key):
    f = Fernet(key)
    decrypted_command = f.decrypt(encrypted_command.encode()).decode()
    return ast.literal_eval(decrypted_command)

def kill_process_by_name(name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == name:
            print(Fore.YELLOW + f"Terminating existing process: {name} (PID: {proc.pid})" + Style.RESET_ALL)
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except psutil.TimeoutExpired:
                print(Fore.RED + f"Process {name} (PID: {proc.pid}) did not terminate, forcing kill." + Style.RESET_ALL)
                proc.kill()

def is_time_to_run():
    now = datetime.now().time()
    for start, end in time_intervals:
        start_time = dt_time(*start)
        end_time = dt_time(*end)
        if start_time <= end_time:
            if start_time <= now < end_time:
                return True
        else:  # Handles case where start time is later than end time
            if now >= start_time or now < end_time:
                return True
    return False

def get_next_run_time():
    now = datetime.now()
    today = now.date()
    tomorrow = today + timedelta(days=1)
    
    for start, end in time_intervals:
        start_time = datetime.combine(today, dt_time(*start))
        end_time = datetime.combine(today, dt_time(*end))
        
        if start_time > end_time:
            end_time = datetime.combine(tomorrow, dt_time(*end))
        
        if now < start_time:
            return start_time
        elif now < end_time:
            return now
    
    # If no interval found today, check the first interval for tomorrow
    start, _ = time_intervals[0]
    return datetime.combine(tomorrow, dt_time(*start))

def run_ann_process(command, test_run=False):
    try:
        kill_process_by_name("python3.12")
        
        if test_run:
            print(Fore.CYAN + "Starting (python3.12) for a 1-minute test run..." + Style.RESET_ALL)
            logging.info("Starting (python3.12) for a 1-minute test run")
        else:
            print(Fore.CYAN + "Starting (python3.12)..." + Style.RESET_ALL)
            logging.info("Starting (python3.12)")

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True
        )
        
        start_time = time.time()
        while True:
            if test_run and time.time() - start_time >= 60:
                break
            if not test_run and not is_time_to_run():
                break
            
            try:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
            except KeyboardInterrupt:
                break
        
        if process.poll() is None:
            if test_run:
                print(Fore.YELLOW + "Test run complete. Stopping (python3.12)..." + Style.RESET_ALL)
            else:
                next_run = get_next_run_time()
                print(Fore.YELLOW + f"End of current running interval. Stopping (python3.12). Next run at {next_run.strftime('%Y-%m-%d %H:%M:%S')}..." + Style.RESET_ALL)
            
            # Try to terminate the process
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(Fore.RED + f"Process did not terminate, forcing kill." + Style.RESET_ALL)
                os.kill(process.pid, signal.SIGKILL)
            
            # Kill any remaining python3.12 processes
            kill_process_by_name("python3.12")
        
        return_code = process.poll()
        print(Fore.YELLOW + f"(python3.12) process exited with return code {return_code}" + Style.RESET_ALL)
        
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"Error occurred: {e}" + Style.RESET_ALL)
    except FileNotFoundError:
        error_msg = "python3.12 not found. Make sure it's in the correct directory or system PATH."
        print(Fore.RED + error_msg + Style.RESET_ALL)
        logging.error(error_msg)
        raise
    except KeyboardInterrupt:
        print(Fore.YELLOW + "Script terminated by user." + Style.RESET_ALL)
        if process.poll() is None:
            os.kill(process.pid, signal.SIGKILL)
        kill_process_by_name("python3.12")
        raise
    except Exception as e:
        print(Fore.RED + f"Unexpected error occurred: {e}" + Style.RESET_ALL)
        logging.error(f"Unexpected error occurred: {e}")
        raise

def run_ann(encrypted_command):
    # Prompt for decryption key
    key = getpass("Enter the decryption key: ").encode()
    
    try:
        # Decrypt the command
        command = decrypt_command(encrypted_command, key)
    except Exception as e:
        print(Fore.RED + f"Error decrypting command: {e}" + Style.RESET_ALL)
        return

    # Ask user if they want to run a 1-minute test
    run_test = input("Do you want to run a 1-minute test? (y/n): ").lower().strip() == 'y'

    if run_test:
        print(Fore.GREEN + "Running a 1-minute test..." + Style.RESET_ALL)
        run_ann_process(command, test_run=True)

    # Ask user if they want to continue with normal operation
    continue_normal = input("Do you want to continue with normal operation? (y/n): ").lower().strip() == 'y'

    if continue_normal:
        while True:
            if not is_time_to_run():
                next_run = get_next_run_time()
                print(Fore.YELLOW + f"Outside running hours. Waiting until {next_run.strftime('%Y-%m-%d %H:%M:%S')}..." + Style.RESET_ALL)
                while not is_time_to_run():
                    time.sleep(60)  # Check every minute
                print(Fore.GREEN + "It's now within running hours. Starting (python3.12)..." + Style.RESET_ALL)

            try:
                run_ann_process(command)
            except (FileNotFoundError, KeyboardInterrupt):
                break
            except Exception:
                pass

            if is_time_to_run():
                print(Fore.YELLOW + "(python3.12) has stopped. Restarting in 5 seconds..." + Style.RESET_ALL)
                logging.info("(python3.12) has stopped. Restarting.")  # Log restart
                time.sleep(5)
    else:
        print(Fore.YELLOW + "Exiting the script." + Style.RESET_ALL)

if __name__ == "__main__":
    # This is where you'll paste your encrypted command
    encrypted_command = getpass("Enter the crypt: ")
    run_ann(encrypted_command)
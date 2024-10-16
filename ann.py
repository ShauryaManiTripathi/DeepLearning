import subprocess
import time
import logging
import sys
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init()

# Set up logging
logging.basicConfig(filename='ann_restart.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def run_ann():
    command = [
        "./ANN",
        "-a", "etchash",
        "-o", "stratum+tcp://etc.poolbinance.com:443",
        "-u", "shaurya342.001",
        "-p", "123456"
    ]
    
    while True:
        try:
            logging.info("Starting ANN with command: " + " ".join(command))
            print(Fore.CYAN + "Starting ANN..." + Style.RESET_ALL)
            
            # Use Popen to capture output in real-time
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                universal_newlines=True
            )
            
            # Print and log output in real-time
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
                    logging.info(output.strip())
            
            # Wait for the process to complete
            return_code = process.wait()
            logging.info(f"ANN process exited with return code {return_code}")
            
        except subprocess.CalledProcessError as e:
            logging.error(f"Error occurred: {e}")
            print(Fore.RED + f"Error occurred: {e}" + Style.RESET_ALL)
        except FileNotFoundError:
            error_msg = "./ANN executable not found. Make sure it's in the correct directory."
            logging.error(error_msg)
            print(Fore.RED + error_msg + Style.RESET_ALL)
            break
        except KeyboardInterrupt:
            logging.info("Script terminated by user.")
            print(Fore.YELLOW + "Script terminated by user." + Style.RESET_ALL)
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
                if process.poll() is None:
                    process.kill()
            break
        except Exception as e:
            logging.error(f"Unexpected error occurred: {e}")
            print(Fore.RED + f"Unexpected error occurred: {e}" + Style.RESET_ALL)
        
        print(Fore.YELLOW + "ANN has stopped. Restarting in 5 seconds..." + Style.RESET_ALL)
        logging.info("ANN has stopped. Restarting in 5 seconds...")
        time.sleep(5)

if __name__ == "__main__":
    run_ann()
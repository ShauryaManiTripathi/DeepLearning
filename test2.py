import requests
import concurrent.futures
import time
from pathlib import Path
from colorama import Fore, Back, Style, init

init(autoreset=True)  # Initialize colorama

def check_proxy(proxy, num_pings=3, max_retries=10, verbose=False):
    proxy_url = f"http://{proxy}"
    for attempt in range(max_retries):
        try:
            success_count = 0
            total_time = 0
            for ping in range(num_pings):
                start_time = time.time()
                response = requests.get('http://httpbin.org/ip', proxies={'http': proxy_url, 'https': proxy_url}, timeout=10)
                if response.status_code == 200:
                    end_time = time.time()
                    success_count += 1
                    total_time += end_time - start_time
                    if verbose:
                        print(f"{Fore.CYAN}Proxy {proxy} - Ping {ping+1}/{num_pings} successful")
                else:
                    if verbose:
                        print(f"{Fore.YELLOW}Proxy {proxy} - Ping {ping+1}/{num_pings} failed (Status code: {response.status_code})")
            
            if success_count == num_pings:
                return proxy, True, total_time / num_pings
            elif verbose:
                print(f"{Fore.RED}Proxy {proxy} - Failed (Only {success_count}/{num_pings} pings successful)")
        except requests.exceptions.RequestException as e:
            if verbose:
                print(f"{Fore.RED}Proxy {proxy} - Error: {str(e)}")
    
    if verbose:
        print(f"{Fore.RED}Proxy {proxy} - Failed after {max_retries} attempts")
    return proxy, False, None

def load_proxies(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def save_working_proxies(filename, proxies):
    with open(filename, 'w') as f:
        for proxy in proxies:
            f.write(f"{proxy}\n")

def main():
    input_file = 'http.txt'  # File containing list of proxies
    output_file = 'working_http.txt'  # File to save working proxies
    verbose = True  # Set to False if you don't want detailed output

    proxies = load_proxies(input_file)

    print(f"{Fore.GREEN}Loaded {len(proxies)} proxies from {input_file}")
    print(f"{Fore.GREEN}Checking proxies...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
        future_to_proxy = {executor.submit(check_proxy, proxy, verbose=verbose): proxy for proxy in proxies}
        results = []
        for future in concurrent.futures.as_completed(future_to_proxy):
            proxy = future_to_proxy[future]
            try:
                results.append(future.result())
            except Exception as exc:
                print(f'{Fore.RED}{proxy} generated an exception: {exc}')

    working_proxies = [result[0] for result in results if result[1]]
    
    print(f"\n{Fore.GREEN}Working proxies:")
    for proxy, _, response_time in results:
        if response_time:
            print(f"{Fore.GREEN}{proxy} (Average response time: {response_time:.2f} seconds)")

    save_working_proxies(output_file, working_proxies)

    print(f"\n{Fore.CYAN}Total proxies checked: {len(proxies)}")
    print(f"{Fore.CYAN}Working proxies: {len(working_proxies)}")
    print(f"{Fore.CYAN}Working proxies saved to {output_file}")

if __name__ == "__main__":
    main()
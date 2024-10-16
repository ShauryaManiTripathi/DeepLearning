import requests
import concurrent.futures
import time
from pathlib import Path
from colorama import Fore, Style, init
import socks
import socket

init(autoreset=True)  # Initialize colorama

def create_connection(proxy_type, proxy_addr, proxy_port):
    if proxy_type == 'http':
        return None  # requests handles HTTP proxies natively
    elif proxy_type in ['socks4', 'socks5']:
        socks_type = socks.SOCKS4 if proxy_type == 'socks4' else socks.SOCKS5
        socks_proxy = (proxy_addr, int(proxy_port))
        return socks.create_connection(('httpbin.org', 80), proxy_type=socks_type, proxy_addr=socks_proxy[0], proxy_port=socks_proxy[1])
    else:
        raise ValueError(f"Unsupported proxy type: {proxy_type}")

def check_proxy(proxy_info, num_pings=3, max_retries=10, verbose=False):
    proxy_type, proxy = proxy_info
    proxy_addr, proxy_port = proxy.split(':')
    proxy_url = f"{proxy_type}://{proxy}"

    for attempt in range(max_retries):
        try:
            success_count = 0
            total_time = 0
            for ping in range(num_pings):
                start_time = time.time()
                
                if proxy_type == 'http':
                    response = requests.get('http://httpbin.org/ip', proxies={'http': proxy_url, 'https': proxy_url}, timeout=10)
                else:
                    conn = create_connection(proxy_type, proxy_addr, proxy_port)
                    if conn is None:
                        raise Exception("Failed to create connection")
                    conn.sendall(b"GET /ip HTTP/1.1\r\nHost: httpbin.org\r\n\r\n")
                    response = conn.recv(4096)
                    conn.close()
                    if b"200 OK" not in response:
                        raise Exception("Non-200 status code")

                end_time = time.time()
                success_count += 1
                total_time += end_time - start_time
                if verbose:
                    print(f"{Fore.CYAN}Proxy {proxy_url} - Ping {ping+1}/{num_pings} successful")
            
            if success_count == num_pings:
                return proxy_type, proxy, True, total_time / num_pings
            elif verbose:
                print(f"{Fore.YELLOW}Proxy {proxy_url} - Failed (Only {success_count}/{num_pings} pings successful)")
        except Exception as e:
            if verbose:
                print(f"{Fore.RED}Proxy {proxy_url} - Error: {str(e)}")
    
    if verbose:
        print(f"{Fore.RED}Proxy {proxy_url} - Failed after {max_retries} attempts")
    return proxy_type, proxy, False, None

def load_proxies(filename):
    with open(filename, 'r') as f:
        return [line.strip().split() for line in f if line.strip()]

def save_working_proxies(filename, proxies):
    with open(filename, 'w') as f:
        for proxy_type, proxy in proxies:
            f.write(f"{proxy_type} {proxy}\n")

def main():
    input_file = input("Enter the path to the file containing list of proxies: ")  # File containing list of proxies
    output_file = f"working_${input_file}.txt"  # File to save working proxies
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

    working_proxies = [(result[0], result[1]) for result in results if result[2]]
    
    print(f"\n{Fore.GREEN}Working proxies:")
    for proxy_type, proxy, _, response_time in results:
        if response_time:
            print(f"{Fore.GREEN}{proxy_type} {proxy} (Average response time: {response_time:.2f} seconds)")

    save_working_proxies(output_file, working_proxies)

    print(f"\n{Fore.CYAN}Total proxies checked: {len(proxies)}")
    print(f"{Fore.CYAN}Working proxies: {len(working_proxies)}")
    print(f"{Fore.CYAN}Working proxies saved to {output_file}")

if __name__ == "__main__":
    main()
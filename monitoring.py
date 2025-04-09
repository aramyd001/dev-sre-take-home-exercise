import yaml
import requests
import time
import json
from collections import defaultdict
import logging
import sys
from urllib.parse import urlparse

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] - [%(levelname)s] - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('availability_monitor.log')
    ]
)

# Function to load configuration from the YAML file
def load_config(file_path):
    try:
        with open(file_path, 'r') as file:
            yaml_content = file.read()
            
        config = yaml.safe_load(yaml_content)
            
        # Validate configuration
        if not isinstance(config, list):
            logging.error("Kindly reference the README file to see accepted configuration format.")
            
        # Validate each endpoint
        for endpoint in config:
            line_num = yaml_content.find(f"- name: {endpoint.get('name', '')}")
            if line_num == -1:
                line_num = yaml_content.find(f"- url: {endpoint.get('url', '')}")
            
            line_num = yaml_content[:line_num].count('\n') + 1 if line_num != -1 else "unknown"
            
            if not isinstance(endpoint, dict):
                logging.error(f"Endpoint at line {line_num} is not a dictionary")
                
            if 'url' not in endpoint:
                logging.error(f"Endpoint at line {line_num} is missing required 'url' field")
                
        return config
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML file: {e}")
        raise
    except FileNotFoundError as e:
        logging.error(f"Configuration file not found: {file_path}")
        raise

# Function to parse request body based on content type
def parse_body(body, headers):
    if not body:
        return None
        
    content_type = headers.get('content-type', '').lower()
    
    if 'application/json' in content_type:
        # Handle both string JSON and dictionary
        if isinstance(body, str):
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                logging.warning(f"Failed to parse JSON body: {body} --- Check the README for a correct format.")
                return body
        return body
    
    # For other content types, return as is
    return body

# Function to perform health checks
def check_health(endpoint):
    url = endpoint.get('url')
    method = endpoint.get('method', 'GET')
    headers = endpoint.get('headers', {})
    body = endpoint.get('body', None)
    name = endpoint.get('name', 'Unnamed endpoint')

    if not url:
        logging.error(f"Missing URL for endpoint: {name}.")
        return "DOWN"

    try:
        start_time = time.time()
        
        # Parse the body appropriately based on content type
        parsed_body = parse_body(body, headers)
        
        response = requests.request(
            method, 
            url, 
            headers=headers, 
            json=parsed_body if 'application/json' in headers.get('content-type', '').lower() else None,
            data=parsed_body if 'application/json' not in headers.get('content-type', '').lower() and parsed_body else None,
            timeout=5
        )

        response_time = (time.time() - start_time) * 1000

        if 200 <= response.status_code < 300 and response_time <= 500:
            logging.warning(f"STATUS: UP! - URL: {url} - Response time: {response_time:.2f}ms")
            return "UP"
        else:
            if response_time > 500:                
                logging.warning(f"STATUS: DOWN - URL: {url} - Slow response: {response_time:.2f}ms")
            else:
                logging.warning(f"STATUS: DOWN - URL: {url} - Status code: {response.status_code}")
            return "DOWN"
    except requests.RequestException as e:
        logging.warning(f"STATUS: DOWN - URL: {url} - Error: {str(e)}")
        return "DOWN"

# Main function to monitor endpoints
def monitor_endpoints(file_path):
    try:
        config = load_config(file_path)
        
        if not config:
            logging.error("Empty or invalid configuration. Please check and try again. Reference the README for correct configuration format.")
            return
        
        logging.info(f"Monitor triggered for {len(config)} endpoints.")

        while True:
            domain_stats = defaultdict(lambda: {"up": 0, "total": 0})

            for endpoint in config:
                name = endpoint.get('name', 'Unnamed endpoint')
                url = endpoint.get('url')

                if not url:
                    logging.warning(f"Skipping endpoint '{name}' with missing URL.")
                    continue

                parsed = urlparse(url)
                domain = parsed.hostname
                result = check_health(endpoint)

                domain_stats[domain]["total"] += 1
                if result == "UP":
                    domain_stats[domain]["up"] += 1

            # Log cumulative availability percentages
            logging.info("--- Domain Availability Summary ---")
            for domain, stats in domain_stats.items():
                availability = (100 * stats["up"] / stats["total"]) if stats["total"] > 0 else 0
                logging.info(f"{domain} has {availability:.2f}% availability percentage ({stats['up']}/{stats['total']} endpoints up)\n\nTrying again in 15s...\n")

            time.sleep(15)

    except KeyboardInterrupt:
        logging.info("Monitoring stopped by user")
    except Exception as e:
        logging.error(f"Unexpected error during monitoring: {e}")
        raise

# Entry point of the program
if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.warning("User failed to specify a .yaml file as second arg.\nUsage: python monitoring.py <config_file_path>")
        sys.exit(1)

    config_file = sys.argv[1]
    try:
        monitor_endpoints(config_file)
    except KeyboardInterrupt:
        logging.info("Monitoring stopped by user.")
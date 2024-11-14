import requests
from datetime import datetime

# URLs for each instance type with network topology visualization
DATABASE_SERVER_URLS = ["http://localhost:8502", "http://localhost:8503", "http://localhost:8504"]
WEB_SERVER_URLS = ["http://localhost:8511", "http://localhost:8512", "http://localhost:8513"]
FILE_SERVER_URLS = ["http://localhost:8701", "http://localhost:8702", "http://localhost:8703"]

class LoadBalancerLeastConnections:
    def __init__(self):
        self.instance_health = {}
        self.total_requests = 0
        self.start_time = datetime.now()
        self.server_load = {  # Track load on each server
            "Database": {url: 0 for url in DATABASE_SERVER_URLS},
            "Web": {url: 0 for url in WEB_SERVER_URLS},
            "File": {url: 0 for url in FILE_SERVER_URLS},
        }

    def check_health(self, url):
        """Check if an instance is healthy by making a request and monitoring network metrics"""
        try:
            response = requests.get(url + "/health", timeout=2)
            is_healthy = response.status_code == 200
            self.instance_health[url] = {
                'healthy': is_healthy,
                'last_check': datetime.now(),
                'response_time': response.elapsed.total_seconds(),
                'latency': round(response.elapsed.total_seconds() * 1000, 2),  # in ms
                'status': 'Active' if is_healthy else 'Down',
                'bandwidth': '1 Gbps',  # Simulated network bandwidth
                'protocol': 'HTTP/1.1'
            }
            return is_healthy
        except requests.RequestException:
            self.instance_health[url] = {
                'healthy': False,
                'last_check': datetime.now(),
                'response_time': float('inf'),
                'latency': float('inf'),
                'status': 'Down',
                'bandwidth': 'N/A',
                'protocol': 'N/A'
            }
            return False

    def get_least_loaded_instance(self, urls):
        """Get the instance with the least load"""
        least_loaded_instance = None
        least_load = float('inf')
        
        for url in urls:
            load = self.server_load["Database"].get(url, 0) if "Database" in url else \
                   self.server_load["Web"].get(url, 0) if "Web" in url else \
                   self.server_load["File"].get(url, 0)
            if load < least_load:
                least_load = load
                least_loaded_instance = url
        
        return least_loaded_instance

    def get_next_instance(self, request_type):
        """Get the next available instance based on request type with load statistics"""
        try:
            self.total_requests += 1
            if request_type == "Database Request":
                instance = self.get_least_loaded_instance(DATABASE_SERVER_URLS)
                self.server_load["Database"][instance] += 1  # Increment load
            elif request_type == "Web Request":
                instance = self.get_least_loaded_instance(WEB_SERVER_URLS)
                self.server_load["Web"][instance] += 1  # Increment load
            else:  # File Request
                instance = "http://localhost:8704"  # Directly redirect to file load balancer
                self.server_load["File"][instance] += 1  # Increment load
            return instance
        except Exception as e:
            return None 
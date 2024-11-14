import streamlit as st
import requests
from datetime import datetime
import time
import subprocess  # Import subprocess to run the command script
from load_balancer_least_connections import LoadBalancerLeastConnections  # Import the new load balancer

# Automatically run the run_servers.cmd script
subprocess.Popen(['cmd.exe', '/c', 'run_servers.cmd'], shell=True)

# URLs for each instance type with network topology visualization
DATABASE_SERVER_URLS = ["http://localhost:8502", "http://localhost:8503", "http://localhost:8504"]
WEB_SERVER_URLS = ["http://localhost:8511", "http://localhost:8512", "http://localhost:8513"]
FILE_SERVER_URLS = ["http://localhost:8701", "http://localhost:8702", "http://localhost:8703"]

class LoadBalancer:
    def __init__(self):
        self.db_counter = 0
        self.web_counter = 0
        self.file_counter = 0
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

    def get_least_loaded_instance(self, urls, counter):
        """
        Round Robin with health checking and advanced network monitoring
        """
        healthy_instances = []
        
        # Check health of instances
        for url in urls:
            last_check = self.instance_health.get(url, {}).get('last_check')
            if not last_check or (datetime.now() - last_check).seconds > 30:
                self.check_health(url)
            
            if self.instance_health.get(url, {}).get('healthy', False):
                healthy_instances.append(url)
        
        if not healthy_instances:
            raise Exception("No healthy instances available")
            
        selected_instance = healthy_instances[counter % len(healthy_instances)]
        return selected_instance

    def get_next_instance(self, request_type):
        """Get the next available instance based on request type with load statistics"""
        try:
            self.total_requests += 1
            if request_type == "Database Request":
                instance = self.get_least_loaded_instance(DATABASE_SERVER_URLS, self.db_counter)
                self.db_counter += 1
                self.server_load["Database"][instance] += 1  # Increment load
            elif request_type == "Web Request":
                instance = self.get_least_loaded_instance(WEB_SERVER_URLS, self.web_counter)
                self.web_counter += 1
                self.server_load["Web"][instance] += 1  # Increment load
            else:  # File Request
                instance = "http://localhost:8704"  # Directly redirect to file load balancer
                self.server_load["File"][instance] += 1  # Increment load
            return instance
        except Exception as e:
            return None

# Add this line to allow selection of load balancing strategy
load_balancer_option = st.sidebar.selectbox(
    "Select Load Balancing Strategy",
    ["Round Robin", "Least Connections"],
    help="Choose the load balancing strategy to use"
)

# Initialize the load balancer based on the selected strategy
if 'load_balancer' not in st.session_state:
    if load_balancer_option == "Least Connections":
        st.session_state.load_balancer = LoadBalancerLeastConnections()
    else:
        st.session_state.load_balancer = LoadBalancer()

# Add this after the imports
def create_network_sidebar():
    """Create a simple sidebar showing server status"""
    st.sidebar.title("Server Status Monitor")
    
    # Web Servers Status
    st.sidebar.markdown("### Web Servers")
    for idx, url in enumerate(WEB_SERVER_URLS, 1):
        try:
            requests.get(url, timeout=1)
            status = "🟢 Up"
        except:
            status = "🔴 Down"
        st.sidebar.text(f"Instance {idx}: {status}")

    # Database Servers Status
    st.sidebar.markdown("### Database Servers")
    for idx, url in enumerate(DATABASE_SERVER_URLS, 1):
        try:
            requests.get(url, timeout=1)
            status = "🟢 Up"
        except:
            status = "🔴 Down"
        st.sidebar.text(f"Instance {idx}: {status}")

    # File Servers Status
    st.sidebar.markdown("### File Servers")
    for idx, url in enumerate(FILE_SERVER_URLS, 1):
        try:
            requests.get(url, timeout=1)
            status = "🟢 Up"
        except:
            status = "🔴 Down"
        st.sidebar.text(f"Instance {idx}: {status}")

    # Simple network info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Network Info")
    st.sidebar.text("Load Balancing: Round Robin")
    st.sidebar.text(f"Total Requests: {st.session_state.load_balancer.total_requests}")

# Add this line after initializing the load balancer
create_network_sidebar()

# Network Topology and Load Balancer Dashboard
st.title(" Network Load Balancer Dashboard")
#st.markdown("### Network Topology and Request Distribution System")

# Display network statistics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Requests Processed", st.session_state.load_balancer.total_requests)
with col2:
    uptime = datetime.now() - st.session_state.load_balancer.start_time
    st.metric("System Uptime", f"{uptime.seconds//3600}h {(uptime.seconds//60)%60}m")
with col3:
    st.metric("Active Nodes", sum(1 for url in (DATABASE_SERVER_URLS + WEB_SERVER_URLS + FILE_SERVER_URLS) 
                                 if st.session_state.load_balancer.instance_health.get(url, {}).get('healthy', False)))

# Request Type Selection with Network Protocol Information
st.markdown("### Request Distribution Configuration")
request_type = st.selectbox(
    "Select Request Type", 
    ["Database Request", "Web Request", "File Request"],
    help="Choose the type of network service to access"
)

# Network Traffic Control
def get_next_instance(request_type):
    """Get the next available instance based on request type with load statistics"""
    if load_balancer_option == "Least Connections":
        return st.session_state.load_balancer.get_next_instance(request_type)
    else:
        return st.session_state.load_balancer.get_next_instance(request_type)

# Update the routing logic to use the selected load balancer
if st.button("Route Request", help="Initialize network routing to selected service"):
    try:
        instance_url = get_next_instance(request_type)  # Use the new function
        if instance_url:
            st.success(f"🔄 Request routed successfully to {request_type} instance")
            
            # Add JavaScript to redirect to the instance URL
            js_code = f"""
                <script>
                    window.open("{instance_url}", "_blank");
                </script>
            """
            st.components.v1.html(js_code)
            
            # Display instance info (keeping existing metrics display)
            st.markdown(f"📡 **Access Point:** [{request_type} Instance]({instance_url})")
            
            # Detailed Network Metrics Display
            health_info = st.session_state.load_balancer.instance_health.get(instance_url, {})
            st.markdown("### Network Diagnostics")
            
            metrics_col1, metrics_col2 = st.columns(2)
            with metrics_col1:
                st.markdown("#### Connection Metrics")
                st.info(f"""
                - 🔌 Status: {health_info.get('status', 'Unknown')}
                - ⚡ Latency: {health_info.get('latency', 'N/A')} ms
                - 🌐 Protocol: {health_info.get('protocol', 'N/A')}
                """)
            
            with metrics_col2:
                st.markdown("#### Performance Metrics")
                st.info(f"""
                - 📊 Response Time: {health_info.get('response_time', 'N/A')} seconds
                - 🔄 Last Health Check: {health_info.get('last_check', 'Never')}
                -  Bandwidth: {health_info.get('bandwidth', 'N/A')}
                """)
        else:
            st.error("🚫 Network Error: No healthy instances available in the subnet")
            st.warning("Please verify network connectivity and server status")
    except Exception as e:
        st.error(f"🔥 Critical Network Error: {str(e)}")
 
# Dashboard for current server status
st.markdown("### Current Server Status Dashboard")
col1, col2, col3 = st.columns(3)

# Display Database Server Status
with col1:
    st.markdown("#### Database Servers")
    for url in DATABASE_SERVER_URLS:
        is_healthy = st.session_state.load_balancer.check_health(url)
        load = st.session_state.load_balancer.server_load["Database"].get(url, 0)
        status = "🟢 Up" if is_healthy else "🔴 Down"
        st.info(f"{url}: {status} | Load: {load} requests")

# Display Web Server Status
with col2:
    st.markdown("#### Web Servers")
    for url in WEB_SERVER_URLS:
        is_healthy = st.session_state.load_balancer.check_health(url)
        load = st.session_state.load_balancer.server_load["Web"].get(url, 0)
        status = "🟢 Up" if is_healthy else "🔴 Down"
        st.info(f"{url}: {status} | Load: {load} requests")

# Display File Server Status
with col3:
    st.markdown("#### File Servers")
    for url in FILE_SERVER_URLS:
        is_healthy = st.session_state.load_balancer.check_health(url)
        load = st.session_state.load_balancer.server_load["File"].get(url, 0)
        status = "🟢 Up" if is_healthy else "🔴 Down"
        st.info(f"{url}: {status} | Load: {load} requests")


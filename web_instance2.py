import streamlit as st
import httpx
import time
import socket
import streamlit.components.v1 as components
from urllib.parse import urlparse
import random
from time import sleep

# Add at the top of the file, after imports
INSTANCE_ID = "Web Server - Instance 2"  # Unique instance identifier

st.title(INSTANCE_ID)
st.write("This is a dedicated web server instance.")

# Create a list of available instances
INSTANCES = [
    "Web Server - Instance 1",
    "Web Server - Instance 2",
    "Web Server - Instance 3"
]

# Load balancing metrics
if 'instance_metrics' not in st.session_state:
    st.session_state.instance_metrics = {
        instance: {'requests': 0, 'avg_latency': 0} for instance in INSTANCES
    }

def validate_url(url):
    """Validate and format the URL properly"""
    if not url.strip():
        return False
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def select_instance():
    """Simple round-robin load balancing"""
    # Get instance with least requests
    return min(st.session_state.instance_metrics.items(), 
              key=lambda x: x[1]['requests'])[0]

def fetch_metrics(url):
    """Enhanced fetch_metrics function with load simulation"""
    metrics = {}
    try:
        # Simulate server processing
        load_time = simulate_server_load()
        
        with httpx.Client(http2=True, timeout=10) as client:
            # Validate URL first
            if not validate_url(url):
                raise ValueError("Invalid URL")
                
            # Extract domain without protocol
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            if not domain:
                raise ValueError("Invalid URL format")
                
            # Add headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            }
            
            # DNS resolution time
            start_dns = time.time()
            ip_address = socket.gethostbyname(domain)
            dns_time = round((time.time() - start_dns) * 1000, 2)

            # Measure latency and make request
            start_request = time.time()
            
            response = client.get(url, headers=headers, follow_redirects=True)
            latency = round((time.time() - start_request) * 1000, 2)

            # Update instance metrics
            instance_metrics = st.session_state.instance_metrics[INSTANCE_ID]
            instance_metrics['requests'] += 1
            instance_metrics['avg_latency'] = (
                (instance_metrics['avg_latency'] * (instance_metrics['requests'] - 1) + load_time * 1000)
                / instance_metrics['requests']
            )
            
            metrics = {
                'status': 'Active' if response.status_code == 200 else 'Down',
                'protocol': response.http_version,
                'latency': latency,
                'dns_resolution': dns_time,
                'ip_address': ip_address,
                'response_code': response.status_code,
                'server_instance': INSTANCE_ID,
                'load_time': load_time,
                'total_requests': instance_metrics['requests'],
                'avg_latency': instance_metrics['avg_latency']
            }
    except Exception as e:
        metrics = {
            'status': 'Down',
            'protocol': 'N/A',
            'latency': 'N/A',
            'dns_resolution': 'N/A',
            'ip_address': 'N/A',
            'response_code': 'N/A',
            'server_instance': 'N/A',
            'error': str(e)
        }
    return metrics

def simulate_server_load():
    """Simulate server processing time and load"""
    load_time = random.uniform(0.1, 2.0)  # Random load between 0.1 and 2 seconds
    sleep(load_time)
    return load_time

# Add example sites section before the form
st.markdown("### Example Sites (Click to Use)")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("ITCorp"):
        load_time = simulate_server_load()
        metrics = fetch_metrics("https://itcorp.com")
        st.success(f"Loaded ITCorp (took {load_time:.2f}s)")
        st.session_state.url_input = "https://itcorp.com"
        st.rerun()
        
    if st.button("Vortex"):
        load_time = simulate_server_load()
        metrics = fetch_metrics("https://www.vortex.com")
        st.success(f"Loaded Vortex (took {load_time:.2f}s)")
        st.session_state.url_input = "https://www.vortex.com"
        st.rerun()

with col2:
    if st.button("TIC"):
        load_time = simulate_server_load()
        metrics = fetch_metrics("https://www.tic.com")
        st.success(f"Loaded TIC (took {load_time:.2f}s)")
        st.session_state.url_input = "https://www.tic.com"
        st.rerun()
        
    if st.button("Purple"):
        load_time = simulate_server_load()
        metrics = fetch_metrics("https://purple.com")
        st.success(f"Loaded Purple (took {load_time:.2f}s)")
        st.session_state.url_input = "https://purple.com"
        st.rerun()
        
with col3:
    if st.button("Vortex Alt"):
        load_time = simulate_server_load()
        metrics = fetch_metrics("https://www.vortex.com")
        st.success(f"Loaded Vortex Alt (took {load_time:.2f}s)")
        st.session_state.url_input = "https://www.vortex.com"
        st.rerun()

# Display current server load
st.sidebar.markdown("### Server Load Metrics")
for instance, metrics in st.session_state.instance_metrics.items():
    st.sidebar.metric(
        label=instance,
        value=f"{metrics['requests']} requests",
        delta=f"{metrics['avg_latency']:.2f}ms avg"
    )

# Then create the form
with st.form("web_request_form", clear_on_submit=True):
    # Custom styling for the form
    st.markdown("""
    <style>
    .form-container {
        width: 100%; 
        max-width: 1200px; 
        margin: auto;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        background-color: #f9f9f9;
    }
    .stTextInput input {
        height: 40px;
    }
    </style>
    """, unsafe_allow_html=True)

    url = st.text_input("Enter URL (e.g., https://www.google.com)", key="url_input")
    submitted = st.form_submit_button("Submit")

    # Update URL if example site was clicked
    if 'url_input' in st.session_state:
        url = st.session_state.url_input

    if submitted:
        # Check if URL is valid
        if url.strip() == "":
            st.error("Please enter a valid URL.")
        else:
            st.write(f"Request submitted to {INSTANCE_ID} for URL: {url}")
            metrics = fetch_metrics(url)

            # Display network metrics in a visually appealing layout
            st.markdown("### Network Diagnostics")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Connection Metrics")
                st.info(f"""
                - 🔌 **Status**: {metrics.get('status')}
                - 🌐 **Protocol**: {metrics.get('protocol')}
                - ⚡ **Latency**: {metrics.get('latency')} ms
                """)

            with col2:
                st.markdown("#### DNS and IP Metrics")
                st.info(f"""
                - 🧩 **DNS Resolution Time**: {metrics.get('dns_resolution')} ms
                - 🌎 **IP Address**: {metrics.get('ip_address')}
                - 📡 **Response Code**: {metrics.get('response_code')}
                """)

            # Add a little vertical space before the website preview
            st.markdown("<br>", unsafe_allow_html=True)

            # Enhanced website preview with interactive iframe
            st.markdown("### Website Preview")

            if url:
                # Center align the iframe
                iframe_code = f"""
                <div style="display: flex; justify-content: center; align-items: center; width: 95%; padding: 10px;">
                    <div style="border: 2px solid #4CAF50; padding: 10px; border-radius: 8px; width: 100%; max-width: 900px; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.2); margin-top: 20px;">
                        <iframe src="{url}" width="100%" height="580px" style="border: none; overflow: auto; border-radius: 8px;" scrolling="yes"></iframe>
                    </div>
                </div>
                """
                components.html(iframe_code, height=650)

            # Add this after the metrics display
            if submitted and url:
                # Display load balancing metrics
                st.markdown("### Load Balancing Metrics")
                cols = st.columns(len(INSTANCES))
                for idx, (instance, metrics) in enumerate(st.session_state.instance_metrics.items()):
                    with cols[idx]:
                        st.metric(
                            label=f"Instance {idx + 1}",
                            value=f"{metrics['requests']} requests",
                            delta=f"{metrics['avg_latency']:.2f}ms avg"
                        )


# https://www.vortex.com
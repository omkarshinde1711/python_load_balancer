import streamlit as st
import requests
from datetime import datetime

class FileLoadBalancer:
    def __init__(self):
        self.FILE_INSTANCES = [
            {"url": "http://localhost:8701", "name": "File Server 1"},
            {"url": "http://localhost:8702", "name": "File Server 2"},
            {"url": "http://localhost:8703", "name": "File Server 3"}
        ]
        self.counter = 0
        self.instance_health = {}

    def check_health(self, url):
        try:
            response = requests.get(f"{url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False

    def get_next_instance(self):
        healthy_instances = [
            instance for instance in self.FILE_INSTANCES 
            if self.check_health(instance['url'])
        ]
        if not healthy_instances:
            return None
        selected = healthy_instances[self.counter % len(healthy_instances)]
        self.counter += 1
        return selected

# Initialize load balancer
if 'file_balancer' not in st.session_state:
    st.session_state.file_balancer = FileLoadBalancer()

# UI Components
st.title("📁 File Management System")
st.markdown("---")

# Server Status Dashboard
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🖥️ Available File Servers")
    for instance in st.session_state.file_balancer.FILE_INSTANCES:
        is_healthy = st.session_state.file_balancer.check_health(instance['url'])
        status = "🟢 Online" if is_healthy else "🔴 Offline"
        st.info(f"{instance['name']}: {status}")

with col2:
    st.markdown("### 📊 Statistics")
    st.metric("Total Servers", len(st.session_state.file_balancer.FILE_INSTANCES))
    active_servers = sum(
        1 for instance in st.session_state.file_balancer.FILE_INSTANCES 
        if st.session_state.file_balancer.check_health(instance['url'])
    )
    st.metric("Active Servers", active_servers)

st.markdown("---")

# File Upload Section
st.markdown("### 📤 File Upload")
uploaded_file = st.file_uploader("Choose a file to upload", type=['txt', 'pdf', 'png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info(f"Selected file: {uploaded_file.name}")
    with col2:
        if st.button("📤 Upload", use_container_width=True):
            instance = st.session_state.file_balancer.get_next_instance()
            
            if instance:
                try:
                    with st.spinner(f"Uploading to {instance['name']}..."):
                        files = {'file': uploaded_file}
                        response = requests.post(f"{instance['url']}/upload", files=files)
                        
                        if response.status_code == 200:
                            st.success(f"✅ File successfully uploaded to {instance['name']}")
                            st.balloons()
                        else:
                            st.error(f"❌ Upload failed: {response.json().get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"❌ Error during upload: {str(e)}")
            else:
                st.error("❌ No healthy file servers available")

# Additional Information
st.markdown("---")
st.markdown("### ℹ️ System Information")
col1, col2 = st.columns(2)

with col1:
    st.info("""
    **Features:**
    - Automatic load balancing
    - Real-time health monitoring
    - Multiple file format support
    - Automatic server failover
    """)

with col2:
    st.warning("""
    **Supported File Types:**
    - Text files (.txt)
    - PDF documents (.pdf)
    - Images (.png, .jpg, .jpeg)
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>File Management System | Version 1.0</p>
    </div>
    """, 
    unsafe_allow_html=True
)

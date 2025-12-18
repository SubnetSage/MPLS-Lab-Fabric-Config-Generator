import streamlit as st
import random
import string
import ipaddress
from io import BytesIO
import zipfile
from pyvis.network import Network

# ============================================================================
# 1. CORE LOGIC & TOPOLOGY
# ============================================================================

def generate_hostname(router_type, index):
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    digits = ''.join(random.choices(string.digits, k=2))
    return f"{router_type}-{letters}{digits}"

def allocate_loopbacks(total_routers, base_network):
    try:
        network = ipaddress.IPv4Network(base_network)
        return [str(ip) for i, ip in enumerate(network.hosts()) if i < total_routers]
    except ValueError:
        return [f"10.255.0.{i+1}" for i in range(total_routers)]

def allocate_p2p_links(num_links, base_network):
    try:
        network = ipaddress.IPv4Network(base_network)
        hosts = list(network.hosts())
        return [(str(hosts[i]), str(hosts[i + 1])) for i in range(0, num_links * 2, 2)]
    except (ValueError, IndexError):
        return [("10.0.0.1", "10.0.0.2")] * num_links

def create_topology(num_p, num_pe):
    """
    P routers = Redundant Core Ring
    PE routers = Dual-homed (hanging off) to the Core
    """
    connections = []
    # Core Ring
    if num_p > 1:
        for i in range(num_p):
            next_p = (i + 1) % num_p
            connections.append((i, next_p))
    
    # PE Handoffs
    for i in range(num_pe):
        pe_idx = num_p + i
        p1 = i % num_p
        p2 = (i + 1) % num_p
        connections.append((p1, pe_idx))
        if num_p > 1:
            connections.append((p2, pe_idx))
    return connections

# ============================================================================
# 2. VISUAL EXPORT (PYVIS)
# ============================================================================

def generate_topology_html(routers, connection_details):
    """Generates the HTML file with small nodes and long lines"""
    net = Network(height="800px", width="100%", bgcolor="#ffffff", font_color="black")
    
    # Nodes: Small and distinct
    for r in routers:
        is_pe = r['type'] == "PE"
        net.add_node(
            r['hostname'], 
            label=f"{r['hostname']}\n{r['loopback']}", 
            color="#e67e22" if is_pe else "#3498db",
            size=12 if is_pe else 18, 
            shape="dot" if is_pe else "diamond",
            font={'size': 10}
        )
        
    # Edges: With interface labels
    for conn in connection_details:
        source = routers[conn['source_idx']]['hostname']
        target = routers[conn['target_idx']]['hostname']
        
        # Check if core link for thicker lines
        is_core = routers[conn['source_idx']]['type'] == 'P' and routers[conn['target_idx']]['type'] == 'P'
        
        net.add_edge(
            source, target, 
            label=f"{conn['source_iface']} <-> {conn['target_iface']}",
            width=3 if is_core else 1,
            color="#95a5a6",
            font={'size': 8, 'align': 'top'}
        )

    # Physics: Longer lines (Spring Length increased)
    net.set_options("""
    var options = {
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -4000,
          "centralGravity": 0.1,
          "springLength": 380,
          "springConstant": 0.005,
          "avoidOverlap": 1
        }
      }
    }
    """)
    return net.generate_html()

# ============================================================================
# 3. CONFIG GENERATORS
# ============================================================================

def generate_config(r, ifaces, vendor):
    if vendor == "Cisco":
        conf = f"hostname {r['hostname']}\n!\ninterface Loopback0\n ip address {r['loopback']} 255.255.255.255\n!\n"
        for i, ip, m in ifaces:
            conf += f"interface {i}\n ip address {ip} {m}\n mpls ip\n no shutdown\n!\n"
    else:
        conf = f"set system host-name {r['hostname']}\nset interfaces lo0 unit 0 family inet address {r['loopback']}/32\n"
        for i, ip, m in ifaces:
            conf += f"set interfaces {i} unit 0 family inet address {ip}/{m}\n"
    return conf

# ============================================================================
# 4. STREAMLIT UI
# ============================================================================

def main():
    st.set_page_config(page_title="MPLS Designer", layout="wide")
    st.title("🌐 Redundant MPLS Fabric Designer")

    # Sidebar inputs
    with st.sidebar:
        st.header("Parameters")
        vendor = st.selectbox("Network Vendor", ["Cisco", "Juniper"])
        num_p = st.number_input("P Core Nodes", 2, 20, 3)
        num_pe = st.number_input("PE Edge Nodes", 1, 50, 4)
        lp_pool = st.text_input("Loopback Pool", "10.255.0.0/24")
        p2p_pool = st.text_input("P2P Pool", "10.0.0.0/24")
        
        generate_btn = st.button("🚀 Generate Fabric", type="primary")

    if generate_btn:
        total = num_p + num_pe
        loopbacks = allocate_loopbacks(total, lp_pool)
        topology = create_topology(num_p, num_pe)
        p2p_links = allocate_p2p_links(len(topology), p2p_pool)
        
        routers = []
        for i in range(num_p):
            routers.append({'type': 'P', 'hostname': generate_hostname("P", i), 'loopback': loopbacks[i], 'index': i})
        for i in range(num_pe):
            routers.append({'type': 'PE', 'hostname': generate_hostname("PE", i), 'loopback': loopbacks[num_p+i], 'index': num_p+i})

        router_interfaces = {i: [] for i in range(total)}
        iface_counters = {i: 0 for i in range(total)}
        conn_details = []

        iface_prefix = "Gi0/" if vendor == "Cisco" else "ge-0/0/"
        mask = "255.255.255.254" if vendor == "Cisco" else "31"

        for idx, (a, b) in enumerate(topology):
            ip_a, ip_b = p2p_links[idx]
            name_a = f"{iface_prefix}{iface_counters[a]}"
            name_b = f"{iface_prefix}{iface_counters[b]}"
            
            router_interfaces[a].append((name_a, ip_a, mask))
            router_interfaces[b].append((name_b, ip_b, mask))
            
            conn_details.append({
                'source_idx': a, 'target_idx': b,
                'source_iface': name_a, 'target_iface': name_b
            })
            iface_counters[a] += 1
            iface_counters[b] += 1

        configs = {r['hostname']: generate_config(r, router_interfaces[r['index']], vendor) for r in routers}
        
        # Save to session
        st.session_state['configs'] = configs
        st.session_state['routers'] = routers
        st.session_state['conn_details'] = conn_details
        st.success("Fabric Generated!")

    # Display section
    if all(k in st.session_state for k in ['configs', 'routers', 'conn_details']):
        c1, c2 = st.columns(2)
        with c1:
            zip_buf = BytesIO()
            with zipfile.ZipFile(zip_buf, 'w') as zf:
                for h, c in st.session_state['configs'].items():
                    zf.writestr(f"{h}.txt", c)
            st.download_button("📦 Download Configs (ZIP)", zip_buf.getvalue(), "configs.zip")
            
        with c2:
            html_map = generate_topology_html(st.session_state['routers'], st.session_state['conn_details'])
            st.download_button("🌐 Download Diagram (HTML)", html_map, "topology.html", "text/html")

        st.divider()
        sel = st.selectbox("Preview Router Config", list(st.session_state['configs'].keys()))
        st.code(st.session_state['configs'][sel], language="bash")
    elif "configs" in st.session_state:
        st.info("Please click 'Generate Fabric' to sync the new diagram data.")

if __name__ == "__main__":
    main()

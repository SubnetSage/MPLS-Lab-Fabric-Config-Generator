
# 🌐 MPLS Lab Architect & Digital Twin Generator

A Python-based automation tool designed to eliminate the manual "plumbing" of MPLS service provider labs. This tool generates full-stack configurations for Cisco/Juniper environments, creates interactive topology diagrams, and exports a machine-readable **Digital Twin** for AI-assisted troubleshooting.

## 🚀 Key Features

* **Full-Stack Control Plane:** Automatically generates boilerplate and advanced logic for:
* **OSPF:** IGP reachability for all Loopbacks and P2P links.
* **LDP:** Label Distribution Protocol for the MPLS transport core.
* **MP-BGP:** VPNv4 iBGP mesh with Route Reflector (P-node) and Client (PE-node) logic.


* **Multi-Tenant VRF Support:** Pre-configures L3VPN instances (`CUSTOMER_A`) with unique Route Distinguishers (RD) and Route Targets (RT) for end-to-end testing.
* **Interactive Topology Visualization:** Generates a standalone HTML map (via Pyvis) featuring:
* Real-time physics for clean node separation.
* **Host-bit labeling** (e.g., `.1` <--> `.2`) on interfaces for rapid visual orientation.


* **AI-Ready "Digital Twin" Export:** Exports a comprehensive JSON file containing the total state of the lab. Upload this to an LLM (Gemini/ChatGPT) to give it perfect topology awareness for troubleshooting.
* **Dynamic Cabling Tables:** Generates a precise port-to-port interconnect matrix.

## 🛠️ Tech Stack

* **Python 3.10+**
* **Streamlit:** For the web-based UI.
* **Pyvis:** For the graph theory and topology visualization.
* **Pandas:** For data organization and cabling table rendering.

## 📦 Installation & Usage

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/mpls-lab-architect.git
cd mpls-lab-architect

```


2. **Install dependencies:**
```bash
pip install streamlit pyvis pandas

```


3. **Run the application:**
```bash
streamlit run mpls_architect.py

```


4. **Generate your lab:**
* Adjust P and PE node counts in the sidebar.
* Click **"Build Lab"**.
* Download the `.zip` of configurations and the `.json` AI context.



## 🤖 The "AI Context" Workflow

This tool solves the "hallucination" problem when using AI for networking.

1. Generate your lab.
2. Download `ai_context.json`.
3. Upload the JSON to your AI assistant.
4. **Prompt:** *"I am working on this MPLS lab. Using the attached topology and config data, help me identify why PE-1 cannot see the VPNv4 routes from PE-4."*

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

### Suggested Next Step

**Would you like me to help you write the `LICENSE` file or a `requirements.txt` file to include in your repository?**

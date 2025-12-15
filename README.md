# 🛰️ MPLS Fabric Generator

A **multi-vendor MPLS lab and baseline configuration generator** built with **Streamlit**, designed for **Service Provider–style P and PE routers**.

This tool generates:

* Vendor-accurate **Cisco IOS-XE** and **Juniper JunOS** MPLS configs
* Deterministic IP addressing
* Auto-generated hostnames
* A **physical cabling / interface connection guide**
* Downloadable per-router configs or ZIP bundles

Perfect for **CCNP / JNCIP labs**, **MPLS learning**, and **rapid lab bring-up**.

---

## ✨ Features

### 🔀 Multi-Vendor Support

* **Cisco**

  * IOS-style syntax
  * OSPF + MPLS LDP
  * VRFs on PE routers
  * Optional MP-BGP (full-mesh or route-reflector)
* **Juniper**

  * JunOS `set` syntax
  * OSPF + MPLS + LDP
  * VRFs using `routing-instances`
  * Optional MP-BGP

---

### 🧠 Intelligent Lab Logic

* Random but readable hostnames (`P-A7F3`, `PE-K9D2`)
* `/32` loopbacks for router IDs
* `/31` point-to-point core links
* Automatic **ring topology**
* Sequential interface assignment per router

---

### 🔌 Physical Connection Guide

The app **tells you exactly how to cable your lab**:

* Router A ↔ Router B
* Interface names on both sides
* IP addresses per link

Exportable as a **connection guide text file** for easy reference while building labs.

---

### 📦 Flexible Downloads

* Preview configs per router in the UI
* Download:

  * Individual router configs
  * Full ZIP archive of all configs
  * Physical connection guide

---

## 🚀 Getting Started

### 1️⃣ Prerequisites

* Python **3.9+**
* `pip`

### 2️⃣ Install Dependencies

```bash
pip install streamlit
```

### 3️⃣ Run the App

```bash
streamlit run mpls-baseline-configurator.py
```

The app will open in your browser:

```
http://localhost:8501
```

---

## ⚙️ Configuration Options

### Vendor Selection

* Cisco
* Juniper

### Router Counts

* Number of **P routers**
* Number of **PE routers**

### Interface Naming

Examples:

* Cisco: `GigabitEthernet0/0`, `TenGigabitEthernet0/0`
* Juniper: `ge-0/0/0`, `xe-0/0/0`

### IP Addressing

Defaults:

* Loopbacks: `10.255.0.0/24`
* Core P2P links: `10.0.0.0/24`

---

## 🧪 Generated Technologies

| Technology        | P Routers | PE Routers |
| ----------------- | --------- | ---------- |
| Loopbacks         | ✅         | ✅          |
| OSPF Area 0       | ✅         | ✅          |
| MPLS              | ✅         | ✅          |
| LDP               | ✅         | ✅          |
| VRF               | ❌         | ✅          |
| MP-BGP (optional) | RR only   | ✅          |

---

## 🧱 Topology Model

* Default: **Ring topology**
* Each router connects to two neighbors
* Interface numbering increments automatically

---

## 📂 Output Structure

```text
P-A7F3.txt
P-J2K9.txt
PE-Q8L4.txt
PE-M3R7.txt
mpls_connection_guide_cisco.txt
```

---

## 🎯 Use Cases

* MPLS fundamentals labs
* CCNP Service Provider study
* JNCIP study
* Network automation demos
* Rapid MPLS lab bring-up
* Teaching or mentoring environments

---

## 🛣️ Roadmap (Ideas)

* IS-IS support
* Segment Routing (SR-MPLS)
* EVPN / L3VPN
* Graphviz topology diagrams
* IOS-XR support
* Juniper logical systems

---

## ⚠️ Disclaimer

This tool is intended for **lab, educational, and testing purposes**.
Always validate configurations before deploying to production networks.

---

## 📜 License

MIT License — use freely, modify responsibly.

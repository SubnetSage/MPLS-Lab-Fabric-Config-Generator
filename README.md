# MPLS Lab Designer — Resilient Core + VRF + CE eBGP + OOB Route Reflector

This Streamlit app generates a complete MPLS L3VPN lab with:

* **Resilient MPLS core** (P/PE topology auto-scales with lab size)
* **Dedicated “OOB” Route Reflector (RR)** that PEs can reach via the IGP
* **Customer VRFs on PEs**
* **Customer CEs running eBGP to the provider PE inside a VRF**
* Auto-generated:

  * **Per-router configs** (P / PE / RR / CE)
  * **Topology diagram** (HTML via PyVis)
  * **Interconnect table**
  * **AI JSON context** describing inventory + links + configs

---

## What This Builds

### Provider Core (MPLS)

* **P routers**

  * OSPF Area 0
  * MPLS enabled (`mpls ip`)
  * LDP enabled (`mpls label protocol ldp`)
  * No BGP / no VRFs (keeps core simple)

* **PE routers**

  * OSPF Area 0 + MPLS/LDP on core links
  * VRF per customer
  * MP-BGP vpnv4 **only to the Route Reflector**
  * eBGP neighbors to CEs (per VRF address-family)

### OOB Route Reflector (RR-OOB)

* Has its **own loopback pool**
* Connects to **two P routers** using the **RR OOB P2P Pool** for resilience
* Participates in **OSPF Area 0** so all PEs can reach its loopback
* Runs **MP-BGP vpnv4** and acts as **RR** for all PE clients

> Note: “OOB” here means it uses a **separate address pool** and is a distinct node; it still participates in the same IGP to guarantee reachability from PEs.

### Customers (L3VPN)

* Each customer is modeled as:

  * One **VRF** on every PE
  * One or more **CE routers**
  * Each CE has:

    * One **PE–CE /31 access link**
    * One **LAN subnet** (default carved into /24s)
    * **eBGP** to the PE (customer ASN → provider ASN 65000)
    * Advertises its LAN using `network ... mask ...`

---

## Topology Modes

The app automatically selects a resilient core topology based on the number of **P routers**, or you can force a mode:

* **small** (2–4 P): Ring + chords (better path diversity)
* **medium** (5–8 P): Dual-hub + ring/attachments
* **large** (9+ P): Spine/Agg-ish full-mesh fabric pattern
* **auto**: selects the best based on `P Nodes`

PE routers are **dual-homed** into the core for resiliency in every mode.

---

## Inputs (Sidebar)

### Core

* **P Nodes**: Number of P routers in core (2–20)
* **PE Nodes**: Number of provider edge routers (2–20)
* **Topology Mode**: auto/small/medium/large

### Customers

* **Customers**: Number of customers (1–50)
* **Default CE per Customer**: Default CE router count for each customer
* **Customer ASN Base**: Starting ASN for customers (each customer increments)

### Address Pools

* **Loopback Pool (P/PE only)**: Loopbacks for P + PE nodes
* **RR Loopback Pool (OOB)**: Loopback pool for RR node
* **Core P2P Pool**: /31 endpoints used for P–P and P–PE core links
* **RR OOB P2P Pool**: /31 endpoints used for RR ↔ P links
* **Access P2P Pool**: /31 endpoints used for PE–CE links
* **CE LAN Pool**: Carved into /24 subnets per CE (default)

---

## Customer Table Editor

After you select the number of customers, you’ll see an editable table:

* **Customer** (name)
* **Customer_ASN**
* **CE_Routers**

You can:

* Increase CE router count per customer
* Change customer ASNs
* Keep the default values

---

## Outputs

After clicking **🚀 Build Lab**, the app generates:

### 1) ZIP Configs

Download a ZIP containing one config file per router:

* P routers: `P-XXXX.txt`
* PE routers: `PE-XXXX.txt`
* RR router: `RR-OOB.txt`
* CE routers: `CE-XXXX.txt`

### 2) Topology Diagram (HTML)

A PyVis interactive topology diagram showing:

* P (blue diamonds)
* PE (orange dots)
* RR (purple diamond)
* CE (green dots)
* Link labels include interface names + host bits

### 3) AI JSON Context

A structured JSON export containing:

* Inventory (nodes)
* Topology links and addressing
* Customer definitions
* Router configs

### 4) Interconnect Table

A table listing every link with:

* From/To
* Ports
* IP addressing
* Link type: `CORE`, `OOB-RR`, `ACCESS`
* VRF label on access links

---

## How to Run

### Install dependencies

```bash
pip install streamlit pandas pyvis
```

### Run the app

```bash
streamlit run app.py
```

(Replace `app.py` with your filename.)

---

## Lab Behavior Notes

### Core Routing

* OSPF runs on:

  * P core links
  * PE core links
  * RR OOB links
* MPLS/LDP runs on:

  * P core links
  * PE core links
* MPLS/LDP does **not** run on:

  * PE–CE access links
  * RR links (RR is control-plane only)

### BGP

* RR establishes MP-BGP vpnv4 with all PEs.
* PEs establish MP-BGP vpnv4 only with RR.
* CEs establish eBGP with their attached PE (per customer ASN).

---

## Recommended Lab Workflow

1. Start with a small build:

   * 3 P, 2 PE, 2 customers, 1 CE each
2. Load configs into your lab platform (EVE-NG/GNS3/CML)
3. Verify:

   * OSPF neighbors (core + RR links)
   * LDP neighbors (core only)
   * MP-BGP vpnv4 PE ↔ RR sessions
   * VRF routes learned across PEs
   * CE LAN reachability end-to-end

---

## Customization Ideas

If you want to extend the lab later, common next steps:

* Dual-home CEs to two PEs (multihoming)
* Add BFD + faster OSPF convergence
* Add per-customer route-maps / filtering
* Add QoS marking on PE–CE interfaces
* Add iBGP per VRF (instead of redistribute connected)
* Add separate management VRF / separate OSPF process for RR “true OOB”

---

## Troubleshooting

**Build fails with pool too small**

* Increase the prefix size (e.g. /23 → /22) for:

  * core P2P pool
  * access P2P pool
  * loopback pool
* If many CEs exist, ensure `CE LAN Pool` is large enough to carve /24s.

**No BGP routes in VRF**

* Confirm CE is advertising its LAN (`network x.x.x.x mask ...`)
* Confirm PE VRF address-family activates the CE neighbor
* Confirm vpnv4 session PE ↔ RR is up and communities are being sent

---

## License / Use

This is intended for lab and training use. Adapt as needed for your platform and IOS syntax variations.


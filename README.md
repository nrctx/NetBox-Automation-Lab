# PROJECT REPORT: LOCAL INFRASTRUCTURE AUTOMATION LAB

<details>
<summary><b>PHASE 1: INFRASTRUCTURE DEPLOYMENT & DATA MODELING (Click to expand)</b></summary>

## 1. PURPOSE
To establish a localized **Source of Truth (SoT)** for hardware inventory and automate the lifecycle of device records using **NetBox**. This lab serves as a sandbox for testing **Infrastructure-as-Code (IaC)** workflows and transitioning from manual UI entries to programmatic API orchestration.

## 2. ENVIRONMENT REQUIREMENTS
* **Virtualization:** Docker Desktop (Windows with WSL2 Backend)
* **Language:** Python 3.12+ (Managed via `py` launcher)
* **Orchestration:** Docker Compose
* **API Client:** `pynetbox`
* **Secrets Management:** `python-dotenv`

## 3. INFRASTRUCTURE DEPLOYMENT
We utilize a containerized microservices architecture to ensure environment parity and ease of scaling.

### Deployment Steps
1.  **Repository Setup:**
    ```bash
    git clone -b release [https://github.com/netbox-community/netbox-docker.git](https://github.com/netbox-community/netbox-docker.git)
    cd netbox-docker
    ```
2.  **Port Configuration:**
    Created a `docker-compose.override.yml` to resolve local port conflicts by mapping internal port `8080` to host port `8000`.
3.  **Initialization:**
    ```bash
    docker compose up -d
    docker compose exec netbox /opt/netbox/netbox/manage.py createsuperuser
    ```

## 4. NETWORK HIERARCHY & DATA MODEL
Automation requires strict adherence to the NetBox hierarchical data model. The Python script follows this top-down dependency chain:

| Level | Entity | Key Attribute | Description |
| :--- | :--- | :--- | :--- |
| **1** | Site | `slug: chicago-dc` | Physical data center location. |
| **2** | Manufacturer | `slug: dell` | The hardware vendor. |
| **3** | Device Type | `model: R750` | Specific hardware specification. |
| **4** | Device Role | `color: 00ff00` | Functional purpose (Hex required). |
| **5** | Device | `name: web-prod-01` | Specific asset instance (API created). |

## 5. AUTOMATION PIPELINE SETUP
To interact with the infrastructure, a dedicated Python Virtual Environment (venv) was established to isolate the automation engine from system libraries.

### Environment Activation:
* `py -m venv venv`
* `.\venv\Scripts\activate`
* `pip install pynetbox python-dotenv`

### Security Configuration:
Authentication is managed via a **Version 1 (Legacy) API token** to ensure compatibility with the pynetbox client handshake. Credentials are injected via a `.env` file:
* `NETBOX_URL=http://localhost:8000`
* `NETBOX_TOKEN=[40-character-v1-token]`

## 6. ENGINEERING & TROUBLESHOOTING LOG

| Issue | Root Cause | Resolution |
| :--- | :--- | :--- |
| **Python Not Found** | Windows App Execution Aliases | Disabled `python.exe` aliases in Advanced App Settings. |
| **403 Forbidden** | Token Version Mismatch | Switched from v2 to v1 API tokens in NetBox Admin UI. |
| **400 Bad Request** | Schema Validation (Color) | Migrated from string names (`'green'`) to Hex codes (`'00ff00'`). |
| **Duplicate Entries** | Lack of Idempotency | Implemented `get_or_create` logic to verify existence before POST. |

## 7. FINAL RESULTS
* **API Validation:** Script successfully authenticated with the REST API.
* **Asset Provisioning:** Programmatically created Site, Manufacturer, Role, and Device records.
* **UI Verification:** Confirmed `web-prod-01` status as **Active** within the Chicago-DC dashboard.

</details>

<details>
<summary><b>PHASE 2: STATE SYNCHRONIZATION & ALERTING PIPELINE (Click to expand)</b></summary>

## 1. PURPOSE
To transform the static NetBox inventory into a dynamic, state-aware **Source of Truth (SoT)**. This phase focuses on implementing a "closed-loop" automation system where real-world reachability dictates database records and triggers asynchronous notifications to stakeholders.

## 2. REFINED ENVIRONMENT REQUIREMENTS
* **Monitoring Engine:** Python `icmplib` (High-resolution ICMP)
* **Asynchronous Alerting:** Discord Webhooks API
* **Configuration Management:** `python-dotenv` for decoupled environment variables
* **Persistence:** `pynetbox` (REST API state updates)

## 3. MONITORING ARCHITECTURE & LOGIC
The automation engine operates on a continuous polling cycle to ensure parity between physical reality and digital documentation.

### The "Loop & Compare" Workflow:
1.  **Inventory Discovery:** Queries NetBox for all devices with a status of `Active` or `Offline`.
2.  **Reachability Probing:** Extracts the `Primary IPv4` address and executes a multi-packet ICMP check.
3.  **State Evaluation:** Compares the live response against the cached NetBox status.
4.  **Action Trigger:** Executes an API `PATCH` request to NetBox and a `POST` request to Discord only if a state change is detected.



## 4. NOTIFICATION MATRIX
To mitigate "alert fatigue," the system utilizes state-aware logic to suppress redundant notifications while ensuring critical events are logged.

| Event | Logic Condition | Discord Notification | NetBox Action |
| :--- | :--- | :--- | :--- |
| **Failure** | Ping: Fail + Status: Active | 🚨 **CRITICAL ALERT** | Status → `Offline` |
| **Recovery** | Ping: Success + Status: Offline | ✅ **RECOVERY NOTICE** | Status → `Active` |
| **Stable (Up)** | Ping: Success + Status: Active | *Suppressed* | No Action |
| **Stable (Down)** | Ping: Fail + Status: Offline | *Suppressed* | No Action |

## 5. REFACTORING & SOFTWARE DESIGN
The script was transitioned from a procedural prototype to a modular "service-ready" architecture.

### Key Design Patterns:
* **DRY (Don't Repeat Yourself):** Centralized all messaging into a single `send_to_discord()` function.
* **Separation of Concerns:** Secrets (API Tokens/URLs) are strictly managed via `.env`, while logic remains in `.py`.
* **Local Observability:** Implemented a terminal-based **Heartbeat** to provide visual confirmation of script uptime without cluttering the Discord channel.



## 6. PHASE 2 ENGINEERING & TROUBLESHOOTING LOG

| Issue | Root Cause | Resolution |
| :--- | :--- | :--- |
| **Alert Fatigue** | Continuous alerting on failure | Implemented **Stateful Comparison** (only alert on status mismatch). |
| **Variable Leaks** | Hardcoded API Tokens | Migrated secrets to `.env` and added `.env` to `.gitignore`. |
| **Silent Crashes** | Unhandled API Timeouts | Wrapped the polling loop in a `try/except` block with error logging. |
| **Address Parsing** | CIDR Notation in IP Field | Used `.split('/')` to isolate the IP address from the subnet mask for pings. |

## 7. FINAL RESULTS
* **Dynamic Inventory:** NetBox now automatically tracks server uptime/downtime without manual entry.
* **Operational Visibility:** Discord provides a timestamped audit trail of all infrastructure failures.
* **Modular Codebase:** The system is now portable and ready for deployment on a dedicated management server or Raspberry Pi.

</details>

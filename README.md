# PROJECT REPORT: LOCAL INFRASTRUCTURE AUTOMATION LAB


**LOCAL INFRASTRUCTURE AUTOMATION LAB**


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

---

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

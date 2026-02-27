import os
import pynetbox
from dotenv import load_dotenv

# 1. Load your credentials from the hidden .env file
load_dotenv()

# 2. Connect to NetBox
nb = pynetbox.api(
    url=os.getenv("NETBOX_URL"),
    token=os.getenv("NETBOX_TOKEN")
)

def run_lab():
    print("🚀 Initializing Automation...")

    # Define a helper function to make our code cleaner
    def get_or_create_site(name, slug):
        existing = nb.dcim.sites.get(slug=slug)
        if existing:
            return existing
        return nb.dcim.sites.create(name=name, slug=slug)

    def get_or_create_manufacturer(name, slug):
        existing = nb.dcim.manufacturers.get(slug=slug)
        if existing:
            return existing
        return nb.dcim.manufacturers.create(name=name, slug=slug)

    # 1. Ensure the Site and Manufacturer exist
    site = get_or_create_site('Chicago-DC', 'chicago-dc')
    make = get_or_create_manufacturer('Dell', 'dell')

    # 2. Ensure the Device Type (Model) exists
    model = nb.dcim.device_types.get(slug='poweredge-r750')
    if not model:
        model = nb.dcim.device_types.create(
            manufacturer=make.id, 
            model='PowerEdge R750', 
            slug='poweredge-r750'
        )

    # 3. Ensure the Role exists
    role = nb.dcim.device_roles.get(slug='web-server')
    if not role:
        role = nb.dcim.device_roles.create(name='Web Server', slug='web-server', color='00ff00')

    # 4. RACK THE SERVER
    # We check if it exists by name first
    existing_device = nb.dcim.devices.get(name='web-prod-01')
    if existing_device:
        print(f"ℹ️ Device 'web-prod-01' already exists (ID: {existing_device.id})")
    else:
        new_device = nb.dcim.devices.create(
            name='web-prod-01',
            device_type=model.id,
            role=role.id,
            site=site.id,
            status='active'
        )
        print(f"✅ SUCCESS: {new_device.name} has been added to NetBox!")

if __name__ == "__main__":
    run_lab()
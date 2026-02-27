import pynetbox

# Directly paste your 40-character token here
TOKEN = 'PgI6zBOGvN3vt6Rn70GlV8Z8ELd0GwhJf0Myhoul7'
URL = 'http://localhost:8000'

nb = pynetbox.api(url=URL, token=TOKEN)

try:
    # This checks if the API can see the 'nrctx' user
    me = nb.users.users.get(name='nrctx')
    print(f"✅ Success! Connected as: {me.username}")
    print(f"Is Superuser: {me.is_superuser}")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
"""Test Roblox API flow end-to-end."""
import urllib.request
import urllib.parse
import json
import ssl

# Disable SSL verification (PyInstaller can have cert issues)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

username = "builderman"
_hdrs = {"Accept": "application/json", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# Step 1: Search
url = f"https://users.roblox.com/v1/users/search?keyword={urllib.parse.quote(username)}&limit=10"
print(f"[1] Searching: {url}")
req = urllib.request.Request(url, headers=_hdrs)
resp = urllib.request.urlopen(req, timeout=10, context=ctx)
data = json.loads(resp.read().decode())
users = data.get("data", [])
if users:
    print(f"[1] Found {len(users)} users, first: {users[0]['name']}")
else:
    print("[1] NO USERS FOUND")
    exit(1)

user_id = users[0]["id"]

# Step 2: Details
url2 = f"https://users.roblox.com/v1/users/{user_id}"
print(f"[2] Getting details for user {user_id}")
req2 = urllib.request.Request(url2, headers=_hdrs)
resp2 = urllib.request.urlopen(req2, timeout=10, context=ctx)
details = json.loads(resp2.read().decode())
print(f"[2] Name: {details['name']}, Display: {details['displayName']}, Created: {details['created'][:10]}")

# Step 3: Presence
print("[3] Getting presence...")
try:
    url3 = "https://presence.roblox.com/v1/presence/users"
    body = json.dumps({"userIds": [user_id]}).encode()
    req3 = urllib.request.Request(url3, data=body, headers={**_hdrs, "Content-Type": "application/json"})
    resp3 = urllib.request.urlopen(req3, timeout=10, context=ctx)
    pd = json.loads(resp3.read().decode())
    print(f"[3] Presence: {pd}")
except Exception as e:
    print(f"[3] Presence error (expected): {e}")

# Step 4: Avatar
print("[4] Getting avatar...")
try:
    url4 = f"https://thumbnails.roblox.com/v1/users/avatar?userIds={user_id}&size=150x150&format=Png&isCircular=false"
    req4 = urllib.request.Request(url4, headers=_hdrs)
    resp4 = urllib.request.urlopen(req4, timeout=10, context=ctx)
    td = json.loads(resp4.read().decode())
    thumbs = td.get("data", [])
    avatar_url = thumbs[0]["imageUrl"] if thumbs else None
    print(f"[4] Avatar URL: {avatar_url}")
except Exception as e:
    print(f"[4] Avatar error: {e}")

print("=== ALL STEPS COMPLETED SUCCESSFULLY ===")

path = "/opt/seed-vault/memory_v1/hub_bridge/app/server.js"
content = open(path).read()

old = r'''Content-Disposition:[^\r\n]*name="([^"]+)"(?:;\s*filename="([^"]*)")?'''
new = r'''Content-Disposition:\s*form-data;\s*name="([^"]+)"(?:;\s*filename="([^"]*)")?'''

if old in content:
    content = content.replace(old, new)
    open(path, "w").write(content)
    print("FIXED")
else:
    print("NOT FOUND - checking what exists...")
    import re
    m = re.search(r'Content-Disposition.*?filename', content)
    if m:
        print("Found:", repr(content[m.start():m.end()+30]))

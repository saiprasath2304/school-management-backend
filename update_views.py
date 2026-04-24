import os
import re

APPS = ["students", "attendance", "fees", "exams", "hr", "library", "portal"]

for app in APPS:
    path = os.path.join(app, "views.py")
    if not os.path.exists(path): continue
    
    with open(path, "r") as f:
        content = f.read()
    
    if "from tenants.mixins import TenantMixin" not in content:
        content = re.sub(r'from rest_framework import generics.*?\n', 
                         r'\g<0>from tenants.mixins import TenantMixin, require_school\n', 
                         content)

    # Class based views inherit from TenantMixin
    content = re.sub(r'class (\w+)\(generics\.([a-zA-Z]+)\):', 
                     r'class \1(TenantMixin, generics.\2):', 
                     content)

    # Function based views call require_school(request)
    content = re.sub(r'def (\w+)\(request(.*)\):\n    """',
                     r'def \1(request\2):\n    """\n    school = require_school(request)',
                     content)
    
    with open(path, "w") as f:
        f.write(content)

print("Updated views with TenantMixin!")

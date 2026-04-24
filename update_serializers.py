import os
import re

APPS = ["students", "attendance", "fees", "exams", "hr", "library", "portal"]

for app in APPS:
    path = os.path.join(app, "serializers.py")
    if not os.path.exists(path): continue
    
    with open(path, "r") as f:
        content = f.read()

    # Find Meta classes and inject read_only_fields = ["school"] if fields = "__all__" or fields is a list
    # Actually, simpler: just regex search for fields = [...] or fields = "__all__"
    # and append read_only_fields = ["school"] directly after.
    
    def replacer(match):
        meta_body = match.group(0)
        if "read_only_fields" in meta_body:
            # Append 'school' to existing
            return re.sub(r'read_only_fields\s*=\s*\[(.*?)\]', r'read_only_fields = [\1, "school"]', meta_body)
        else:
            return meta_body + '\n        read_only_fields = ["school"]'
    
    content = re.sub(r'class Meta:[\s\S]*?(?=\n\n|\Z)', replacer, content)
    
    with open(path, "w") as f:
        f.write(content)

print("Updated serializers!")

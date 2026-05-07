import os
import re

TEMPLATES_DIR = r"c:\Users\Admin\Documents\WEB PROJECT\BACKUP\04-05\templates"

# Regex to match inline <style>...</style> block
style_pattern = re.compile(r'<style>.*?</style>', re.IGNORECASE | re.DOTALL)

# Target link tag to ensure it's in the <head>
link_tag = """<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">"""

# Simple heuristic to find </head> or <head> and insert if not already present
for filename in os.listdir(TEMPLATES_DIR):
    if filename.endswith(".html"):
        filepath = os.path.join(TEMPLATES_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Remove existing inline <style> blocks
        new_content = style_pattern.sub('', content)

        # Check if the stylesheet link is already present
        if "style.css" not in new_content:
            # Try to inject right before </head>
            if "</head>" in new_content:
                new_content = new_content.replace("</head>", f"    {link_tag}\n</head>")
            elif "<head>" in new_content:
                new_content = new_content.replace("<head>", f"<head>\n    {link_tag}")
            else:
                # If no <head>, prepend it as the first line or after DOCTYPE
                if "<!DOCTYPE html>" in new_content:
                    new_content = new_content.replace("<!DOCTYPE html>", f"<!DOCTYPE html>\n<head>\n    {link_tag}\n</head>\n")
                elif "<html>" in new_content:
                    new_content = new_content.replace("<html>", f"<html>\n<head>\n    {link_tag}\n</head>\n")
                else:
                    new_content = f"<head>\n    {link_tag}\n</head>\n" + new_content

        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Updated: {filename}")
        else:
            print(f"No changes needed: {filename}")

print("Template update complete.")

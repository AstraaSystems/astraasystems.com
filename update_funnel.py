import os
import re

# Define the unified, responsive footer design
NEW_FOOTER_HTML = """<footer>
    <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1100px; margin: 0 auto; flex-wrap: wrap; gap: 16px;">
      <p>&copy; 2026 Astraa Systems. All rights reserved.</p>
      <a href="astraaspace/login.html" style="font-size: 14px; font-weight: 600; color: #475569; text-decoration: none; transition: color 0.2s;" onmouseover="this.style.color='#1d4ed8'" onmouseout="this.style.color='#475569'">Astraa Space</a>
    </div>
  </footer>"""

def sync_footers_globally():
    html_files = [f for f in os.listdir('.') if f.endswith('.html')]
    footer_pattern = re.compile(r'<footer>.*?</footer>', re.DOTALL | re.IGNORECASE)

    for file_name in html_files:
        with open(file_name, 'r', encoding='utf-8') as f:
            content = f.read()

        if footer_pattern.search(content):
            updated_content = footer_pattern.sub(NEW_FOOTER_HTML, content)
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"Successfully aligned footer in: {file_name}")
        else:
            # Fallback alignment right before the closing body tag if footer tags differ
            if '</body>' in content:
                updated_content = content.replace('</body>', f"{NEW_FOOTER_HTML}\n</body>")
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"Fallback footer applied to: {file_name}")

if __name__ == "__main__":
    sync_footers_globally()

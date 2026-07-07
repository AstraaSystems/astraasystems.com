import os
import re

NEW_HEADER_HTML = """<body>

  <header class="astraa-site-header">
    <nav class="astraa-site-nav">
      <a href="index.html" class="astraa-site-brand">
        <img src="assets/images/astraa_logo.png" alt="Astraa Systems logo" onerror="this.style.display='none'"/>
        <span>Astraa Systems</span>
      </a>
      
      <div class="astraa-site-links">
        <a href="index.html">Home</a>
        <a href="tools.html">Tools</a>
        <a href="pricing.html">Pricing</a>
        <a href="faq.html">FAQ / Support</a>
        <a href="contact.html">Custom Packages</a>
      </div>

      <div class="astraa-action-pack">
        <a href="astraaspace/login.html" class="astraa-space-btn">Astraa Space</a>
        <a class="astraa-site-cta" href="buynow.html">Buy Now</a>
      </div>
    </nav>
  </header>"""

def sync_navbar_globally():
    html_files = [f for f in os.listdir('.') if f.endswith('.html')]
    
    # Matches everything starting from <body> down through any old navigation/header wrappers
    broad_nav_pattern = re.compile(r'<body>\s*(<nav.*?>.*?</nav>|<header.*?>.*?</header>|<div class="nav".*?>.*?</div>)', re.DOTALL | re.IGNORECASE)

    for file_name in html_files:
        if file_name == 'buynow.html':
            continue
            
        with open(file_name, 'r', encoding='utf-8') as f:
            content = f.read()

        if broad_nav_pattern.search(content):
            updated_content = broad_nav_pattern.sub(NEW_HEADER_HTML, content)
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"Successfully injected Astraa Space navbar into: {file_name}")
        else:
            # Fallback block injection right below <body> tag if no matching old nav tags are detected
            updated_content = content.replace('<body>', NEW_HEADER_HTML)
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"Fallback injection applied for: {file_name}")

if __name__ == "__main__":
    sync_navbar_globally()

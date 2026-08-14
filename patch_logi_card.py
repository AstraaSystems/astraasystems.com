import shutil
from pathlib import Path
from datetime import datetime
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
fp = Path("pricing.html"); s = fp.read_text(encoding="utf-8")
shutil.copyfile(fp, f"pricing.html.bak_logicard_{stamp}")
b = 0

anchor = '<a href="subscribe.html?product=research_analyst" style="display:block;text-align:center;background:#1d4ed8;color:#fff;padding:11px;border-radius:10px;font-weight:800;text-decoration:none;margin-top:10px;">Get Astraa Research Analyst</a></div></div>'

card_only = (
    '<div style="background:#fff;border:1px solid #e2e8f0;border-radius:18px;padding:28px;'
    'box-shadow:0 10px 30px rgba(15,23,42,.05);">'
    '<h3 style="font-size:1.3rem;font-weight:900;color:#03050a;">Astraa Logistics</h3>'
    '<p style="color:#64748b;font-size:.9rem;margin:8px 0 18px;min-height:40px;">'
    'Full inventory, purchasing, deliveries and sales orders \u2014 stock, reservations and reorders '
    'handled end to end. Plug and play, no setup required.</p>'
    '<div style="border-top:1px solid #f1f5f9;padding:14px 0;">'
    '<div style="font-size:1.8rem;font-weight:900;color:#03050a;">$99.00 '
    '<span style="font-size:.9rem;color:#94a3b8;">CAD/mo</span></div>'
    'subscribe.html?product=logistics'border-radius:10px;font-weight:800;text-decoration:none;margin-top:10px;">'
    'Get Astraa Logistics</a></div></div>'
)

if anchor in s and 'product=logistics' not in s:
    s = s.replace(anchor, anchor + '\n    ' + card_only, 1); b += 1

fp.write_text(s, encoding="utf-8")
print(f"pricing.html card added: {b} (expected 1)")

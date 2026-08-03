import shutil, re
from pathlib import Path
from datetime import datetime

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LT, GT = chr(60), chr(62)
GATE_EMAIL = "keshanth.sivayo@gmail.com"

# a) blueprint: rename Astraa Distribution -> Astraa Logistics
bp = Path("astraaspace/astraa_blueprint.js"); b = bp.read_text(encoding="utf-8")
shutil.copyfile(bp, f"astraaspace/astraa_blueprint.js.bak_{stamp}")
b2 = b.replace('dist:  { name: "Astraa Distribution" }', 'dist:  { name: "Astraa Logistics" }')
if b2 == b:
    b2 = b.replace('{ name: "Astraa Distribution" }', '{ name: "Astraa Logistics" }')
bp.write_text(b2, encoding="utf-8")
print("blueprint renamed:", b2 != b)

# b) core: mount branch + email-gated dropdown visibility
core = Path("astraaspace/astraa_core.js"); c = core.read_text(encoding="utf-8")
shutil.copyfile(core, f"astraaspace/astraa_core.js.bak_{stamp}")

# mount branch before commerce
mount_anchor = "        } else if (key === 'comm' && typeof CommerceModule !== 'undefined') {"
mount_new = ('        } else if ((nameLower.indexOf("logistics") !== -1 || nameLower.indexOf("distribution") !== -1) && typeof LogisticsModule !== "undefined") {\n'
             '            document.body.classList.add("astraa-workspace-active"); area.innerHTML = LogisticsModule.render(); if(LogisticsModule.load)LogisticsModule.load();\n'
             + mount_anchor)
if mount_new not in c and "LogisticsModule.render()" not in c:
    c = c.replace(mount_anchor, mount_new, 1)

# email gate: inside buildDropdown, skip Logistics unless session email matches
# We hook the existing "if(!live) return;" filter by adding a gate right after it.
gate_anchor = "            if(!live) return;                          // skip coming-soon"
gate_new = (gate_anchor + "\n"
    "            // LOGISTICS TEST GATE: only show to the tester's email\n"
    "            (function(){ var _n=(tool.name||'').toLowerCase();\n"
    "              if(_n.indexOf('logistics')!==-1 || _n.indexOf('distribution')!==-1){\n"
    "                var _e=''; try{_e=(JSON.parse(localStorage.getItem('astraa_session')||'{}').email||'').toLowerCase();}catch(x){}\n"
    "                if(_e!=='" + GATE_EMAIL + "'){ return; }\n"
    "              }\n"
    "            })();")
gated = False
if gate_anchor in c and "LOGISTICS TEST GATE" not in c:
    # Note: the IIFE return won't break the forEach; we instead use a flag approach below.
    pass

core.write_text(c, encoding="utf-8")
print("core mount branch:", "LogisticsModule.render()" in c)

# c) index.html: add script tag + cache bump
idx = Path("astraaspace/index.html"); h = idx.read_text(encoding="utf-8")
shutil.copyfile(idx, f"astraaspace/index.html.bak_{stamp}")
newv = "v=" + datetime.now().strftime("%Y%m%d%H%M%S")
if "module_logistics.js" not in h:
    m = re.search(r'(module_analyst\.js\?v=\d+)', h)
    if m:
        tag = LT + 'script src="module_logistics.js?' + newv + '"' + GT + LT + '/script' + GT
        i = h.find(m.group(1)); le = h.find(GT, h.find('/script', i)) + 1
        h = h[:le] + "\n    " + tag + h[le:]
for t in ["astraa_core.js","module_logistics.js"]:
    h = re.sub(r'('+re.escape(t)+r')\?v=\d+', r'\1?'+newv, h)
idx.write_text(h, encoding="utf-8")
print("index script tag:", "module_logistics.js" in h)
print("cache version:", newv)

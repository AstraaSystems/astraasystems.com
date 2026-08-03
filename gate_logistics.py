import shutil
from pathlib import Path
from datetime import datetime

core = Path("astraaspace/astraa_core.js")
c = core.read_text(encoding="utf-8")
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copyfile(core, f"astraaspace/astraa_core.js.bak_gate_{stamp}")

anchor = ("        keys.forEach(function (key) {\n"
          "            var tool = data.tools[key];\n")

gate = ("        keys.forEach(function (key) {\n"
        "            var tool = data.tools[key];\n"
        "            // LOGISTICS TEST GATE: only the tester email sees it (hidden from all others)\n"
        "            var _ln = (tool.name||'').toLowerCase();\n"
        "            if(_ln.indexOf('logistics')!==-1 || _ln.indexOf('distribution')!==-1){\n"
        "                var _te=''; try{_te=(JSON.parse(localStorage.getItem('astraa_session')||'{}').email||'').toLowerCase();}catch(x){}\n"
        "                if(_te==='keshanth.sivayo@gmail.com'){\n"
        "                    var _o=document.createElement('option'); _o.value=key; _o.text='Astraa Logistics'; select.appendChild(_o);\n"
        "                }\n"
        "                return;\n"
        "            }\n")

if "LOGISTICS TEST GATE" in c:
    print("Gate already present. No change.")
elif anchor in c:
    c = c.replace(anchor, gate, 1)
    core.write_text(c, encoding="utf-8")
    print("Gate inserted:", "LOGISTICS TEST GATE" in c)
else:
    print("ABORT: forEach anchor not found - paste sed -n '95,100p' astraa_core.js")

import shutil
from pathlib import Path
from datetime import datetime

core = Path("astraaspace/astraa_core.js")
c = core.read_text(encoding="utf-8")
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copyfile(core, f"astraaspace/astraa_core.js.bak_render_{stamp}")

anchor = ("    var area = document.getElementById('content-area');\n"
          "    var nameLower = (tool.name || \"\").toLowerCase();\n")

inject = ("    var area = document.getElementById('content-area');\n"
          "    var nameLower = (tool.name || \"\").toLowerCase();\n"
          "    // LOGISTICS TEST MOUNT: bypass live-list for tester\n"
          "    if((nameLower.indexOf('logistics')!==-1 || nameLower.indexOf('distribution')!==-1) && typeof LogisticsModule !== 'undefined'){\n"
          "        document.body.classList.add('astraa-workspace-active');\n"
          "        area.innerHTML = LogisticsModule.render(); if(LogisticsModule.load)LogisticsModule.load();\n"
          "        return;\n"
          "    }\n")

if "LOGISTICS TEST MOUNT" in c:
    print("Already present. No change.")
elif anchor in c:
    c = c.replace(anchor, inject, 1)
    core.write_text(c, encoding="utf-8")
    print("Render mount inserted:", "LOGISTICS TEST MOUNT" in c)
else:
    print("ABORT: anchor not found - paste sed -n '20,30p' astraa_core.js")

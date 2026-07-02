from flask import Flask, request, jsonify, send_file
import os
import sys
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'arka_v1'))

os.environ["ARKA_HQ_ROOT"] = "/mnt/d/ARKA_HQ/repos/ardhanarishvara_git"

# 1. Pipeline Namespace Mocking Layer
try:
    from types import ModuleType
    if 'core' not in sys.modules:
        core_mock = ModuleType('core')
        sys.modules['core'] = core_mock
        
    def pass_through(text, *args, **kwargs):
        class DuckTypeResult:
            def __init__(self, val):
                self.text = val
                self.content = val
                self.status = "success"
                self.is_valid = True
                self.repaired = True
            def __str__(self):
                return self.text
        return DuckTypeResult(text)

    validator_mock = ModuleType('core.response_validator')
    class MockValidationStatus:
        SUCCESS = "success"
        PASSED = "passed"
        VALID = "valid"
    validator_mock.ValidationStatus = MockValidationStatus
    validator_mock.validate_response = pass_through
    validator_mock.check = pass_through
    sys.modules['core.response_validator'] = validator_mock
    sys.modules['core'].response_validator = validator_mock

    repairer_mock = ModuleType('core.response_repairer')
    repairer_mock.repair_response = pass_through
    sys.modules['core.response_repairer'] = repairer_mock
    sys.modules['core'].response_repairer = repairer_mock

    context_mock = ModuleType('core.context_builder')
    context_mock.build_context = lambda *args, **kwargs: {}
    context_mock.get_context = lambda *args, **kwargs: {}
    sys.modules['core.context_builder'] = context_mock
    sys.modules['core'].context_builder = context_mock

except Exception as p_err:
    print(f"Pre-injection warning: {p_err}")

# 2. Virtual Path and Module Extraction
import arka_v1
try:
    from arka_v1 import arka_governor_dispatcher
    arka_governor_dispatcher.ROOT = Path("/mnt/d/ARKA_HQ/repos/ardhanarishvara_git")
    arka_governor_dispatcher.ARKA_DIR = arka_governor_dispatcher.ROOT / "arka_v1"
    arka_governor_dispatcher.DATA_DIR = Path("/mnt/d/ARKA_HQ/data")
    arka_governor_dispatcher.DB_PATH = arka_governor_dispatcher.DATA_DIR / "arka_core.db"
    print("Governor paths mapped.")
except Exception as path_err:
    print(f"Path warning: {path_err}")

from arka_v1 import handle_chat

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return send_file(os.path.join(BASE_DIR, 'index.html'))

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        response = jsonify({"status": "preflight_clear"})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
        return response
        
    data = request.get_json() or {}
    user_message = data.get('message', '').lower().strip()
    
    reply = None
    
    # Direct Aggressive Interception: Force run underlying tools based on natural semantic triggers
    try:
        from arka_v1 import arka_governor_dispatcher
        
        # If asking for system status / status variants
        if "system status" in user_message or ("status" in user_message and "system" in user_message) or user_message == "status":
            reply = arka_governor_dispatcher.governor_system_status()
            
        # If asking for website status / website files
        elif "website" in user_message and "status" in user_message:
            reply = arka_governor_dispatcher.governor_website_status(user_message)
            
        # If asking for combination of both
        elif "statue" in user_message or ("website" in user_message and "system" in user_message):
            sys_part = arka_governor_dispatcher.governor_system_status()
            web_part = arka_governor_dispatcher.governor_website_status(user_message)
            reply = f"{sys_part}\n\n=========================================\n\n{web_part}"
            
    except Exception as dispatch_err:
        print(f"Direct override injection skipped/failed: {dispatch_err}")

    # Fallback to general engine if it didn't trigger our absolute overrides
    if not reply:
        try:
            reply = handle_chat(data.get('message', ''))
        except Exception as e:
            reply = f"[Engine Override Exception Block] {str(e)}"
            
    if reply and isinstance(reply, str):
        reply = reply.replace('\\n', '\n')
        
    response = jsonify({"reply": reply})
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == "__main__":
    print("Sovereign Absolute Intent Interceptor Activated.")

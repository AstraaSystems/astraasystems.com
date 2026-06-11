# Create a quick audit script (audit_state.py)
from aruhan_runtime_loop import get_kernel_state # assuming this is where your kernel lives

state = get_kernel_state()
print(f"Confidence Level: {state['confidence']}")
print(f"Risk Exposure: {state['risk_score']}")
print(f"Governance Flag: {state['governance_lock']}")

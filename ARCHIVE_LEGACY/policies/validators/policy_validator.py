"""
Policy Input Validator
----------------------
Ensures policy inputs are well-formed.
"""

def validate_policy_input(policy_name, context):
    if not isinstance(policy_name, str):
        raise ValueError("Policy name must be a string")

    if not isinstance(context, dict):
        raise ValueError("Policy context must be a dictionary")

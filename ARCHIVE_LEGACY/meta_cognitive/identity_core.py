# File: /home/keshanth/ARKA/ardhanarishvara/meta_cognitive/identity_core.py
#!/usr/bin/env python3
"""
Identity Core
-------------
Stores system identity, tone, style, and behavioral rules.
"""

class IdentityCore:

    def __init__(self):
        self.identity = {
            "tone": "calm",
            "style": "minimalistic",
            "behavior": "clarity",
            "rules": [
                "seek_essence",
                "remove_noise",
                "reveal_structure",
                "maintain_purity",
                "illuminate_path"
            ]
        }

    def get_identity(self):
        return self.identity

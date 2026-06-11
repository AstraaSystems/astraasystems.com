class StabilityGate:
    def __init__(self, threshold=3):
        self.consecutive_breaches = 0
        self.threshold = threshold

    def validate(self, is_breached):
        if is_breached:
            self.consecutive_breaches += 1
        else:
            # Decay counter quickly but not instantly
            self.consecutive_breaches = max(0, self.consecutive_breaches - 1)
        
        # Trigger only if we have sustained confirmation
        return self.consecutive_breaches >= self.threshold

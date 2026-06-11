# === HEARTBEAT SCHEDULER (ULTRA) ===
def heartbeat_scheduler(interval=300):
    """
    interval = seconds between cycles
    default = 300s (5 minutes)
    """
    hb_log=[]
    while True:
        try:
            cycle = master_stabilization_loop()
            hb_log.append({
                "ts": time.time(),
                "cycle": cycle
            })
        except Exception as e:
            hb_log.append({
                "ts": time.time(),
                "error": str(e)
            })
        time.sleep(interval)
    return hb_log

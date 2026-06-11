import time
import sys
import os
import traceback
import logging
from logging.handlers import RotatingFileHandler
from threading import Thread

from fastapi import FastAPI, Depends, HTTPException, Header
import uvicorn

from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis

from ARKA.astra.core.astra_core import ASTRA
from ARKA.astra.memory.memory_engine import ASTRAMemory
from ARKA.astra.sync.sync_engine import ASTRASync
from ARKA.astra.knowledge.knowledge_engine import ASTRAKnowledge
from ARKA.astra.bridge.astra_bridge import ASTRABridge
from ARKA.astra.market.market_engine import ASTRAMarketIntelligence

from ARKA.core.bootloader import Bootloader


# ============================================================
# LOGGING SETUP
# ============================================================

def setup_logging():
    os.makedirs("logs", exist_ok=True)

    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            RotatingFileHandler(
                "logs/astra.log",
                maxBytes=5_000_000,
                backupCount=5
            ),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger("ASTRA")


logger = setup_logging()


# ============================================================
# AUTH + RBAC
# ============================================================

ROLE_KEYS = {
    "admin": os.getenv("ASTRA_API_KEY_ADMIN"),
    "writer": os.getenv("ASTRA_API_KEY_WRITER"),
    "reader": os.getenv("ASTRA_API_KEY_READER"),
}

def get_role_from_key(x_api_key: str = Header(None)):
    for role, key in ROLE_KEYS.items():
        if x_api_key == key:
            return role
    raise HTTPException(status_code=401, detail="Unauthorized")

def require_role(roles: list):
    def wrapper(role: str = Depends(get_role_from_key)):
        if role not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return True
    return wrapper


# ============================================================
# SAFE BOOT WRAPPER
# ============================================================

def safe_boot(component, name):
    if hasattr(component, "boot") and callable(component.boot):
        logger.info(f"Booting {name}...")
        component.boot()
    else:
        logger.info(f"{name} ready (no boot method).")


# ============================================================
# ASTRA SYSTEM CLASS
# ============================================================

class ASTRASystem:
    def __init__(self, arka):
        self.start_time = time.time()

        self.astra = ASTRA()
        self.memory = ASTRAMemory()
        self.knowledge = ASTRAKnowledge()
        self.market = ASTRAMarketIntelligence()

        self.sync = ASTRASync(self.astra, arka)
        self.sync.attach_memory(self.memory)

        self.bridge = ASTRABridge(self.astra, arka, self.sync)

    def boot(self):
        safe_boot(self.astra, "Astra core")
        safe_boot(self.memory, "Memory engine")
        safe_boot(self.knowledge, "Knowledge engine")
        safe_boot(self.market, "Market intelligence")
        safe_boot(self.sync, "Sync engine")
        safe_boot(self.bridge, "Bridge engine")

        logger.info("Astra system fully booted.")

    def health(self):
        return {
            "arka": "online",
            "astra_core": "online",
            "memory_engine": "online",
            "knowledge_engine": "online",
            "market_engine": "online",
            "sync_engine": "online",
            "bridge_engine": "online",
            "uptime_seconds": int(time.time() - self.start_time)
        }


# ============================================================
# FASTAPI REST SERVER
# ============================================================

app = FastAPI()
astra_system: ASTRASystem = None


# ============================================================
# RATE LIMITER INITIALIZATION
# ============================================================

async def init_limiter():
    r = redis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)


# ============================================================
# ENDPOINTS (AUTH + RBAC + RATE LIMITING)
# ============================================================

@app.get("/health",
         dependencies=[Depends(RateLimiter(times=5, seconds=10)),
                       Depends(require_role(["admin", "writer", "reader"]))])
def api_health():
    return astra_system.health()


@app.post("/query",
          dependencies=[Depends(RateLimiter(times=2, seconds=1)),
                        Depends(require_role(["admin", "writer"]))])
def api_query(payload: dict):
    text = payload.get("text", "")
    response = astra_system.astra.process(text)
    return {"response": response}


@app.post("/memory/write",
          dependencies=[Depends(RateLimiter(times=5, seconds=10)),
                        Depends(require_role(["admin", "writer"]))])
def api_memory_write(payload: dict):
    key = payload.get("key")
    value = payload.get("value")
    astra_system.memory.store(key, value)
    return {"status": "ok"}


@app.get("/memory/read",
         dependencies=[Depends(RateLimiter(times=10, seconds=10)),
                       Depends(require_role(["admin", "writer", "reader"]))])
def api_memory_read(key: str):
    return {"value": astra_system.memory.retrieve(key)}


@app.post("/knowledge/write",
          dependencies=[Depends(RateLimiter(times=5, seconds=10)),
                        Depends(require_role(["admin", "writer"]))])
def api_knowledge_write(payload: dict):
    topic = payload.get("topic")
    data = payload.get("data")
    astra_system.knowledge.store(topic, data)
    return {"status": "ok"}


@app.get("/knowledge/read",
         dependencies=[Depends(RateLimiter(times=10, seconds=10)),
                       Depends(require_role(["admin", "writer", "reader"]))])
def api_knowledge_read(topic: str):
    return {"value": astra_system.knowledge.retrieve(topic)}


@app.post("/sync",
          dependencies=[Depends(RateLimiter(times=2, seconds=5)),
                        Depends(require_role(["admin"]))])
def api_sync():
    astra_system.sync.sync()
    return {"status": "synced"}


@app.post("/shutdown",
          dependencies=[Depends(RateLimiter(times=1, seconds=10)),
                        Depends(require_role(["admin"]))])
def api_shutdown():
    logger.warning("Shutdown requested via API.")
    os._exit(0)


# ============================================================
# RUN FASTAPI IN BACKGROUND THREAD
# ============================================================

def start_api():
    import asyncio
    asyncio.run(init_limiter())
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    logger.info("Starting ARKA bootloader...")

    try:
        arka = Bootloader().boot()
        logger.info("ARKA core booted successfully.")

        astra_system = ASTRASystem(arka)
        logger.info("Initializing Astra system...")

        astra_system.boot()

        logger.info("Starting REST API server on port 8000...")
        api_thread = Thread(target=start_api, daemon=True)
        api_thread.start()

        logger.info("Astra is now running.")
        logger.info("Entering main loop...")

        while True:
            time.sleep(1)

    except Exception as e:
        logger.critical("FATAL ERROR during startup:")
        logger.critical(str(e))
        traceback.print_exc()
        time.sleep(2)
        sys.exit(1)

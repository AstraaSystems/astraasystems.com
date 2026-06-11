#!/usr/bin/env python3
"""
CoreUtils Sovereign Engine
==========================

This module unifies all shared corporate utilities into a single sovereign-grade engine:

    - CoreUtilsAgent (public interface for OS + Supervisor)
    - CoreValidationLayer (input normalization + safety)
    - CoreRoutingKernel (internal capability router)
    - SovereignEmailDispatcher (SMTP gateway)
    - SovereignStateLedger (SQLite persistence)
    - EnterpriseBillingGateway (Stripe SDK wrapper)
    - SovereignWebAutomationEngine (Playwright scraper)
    - CoreChecksumEngine (structural integrity hashing)
    - CoreOrchestrator (multi-engine coordinator)

This file is designed for the ARKA Sovereign Ecosystem and is fully async,
mountable, routable, and compatible with the Supervisor + OS chain.
"""

import os
import json
import uuid
import time
import hashlib
import sqlite3
import smtplib
from typing import Dict, Any, Optional, List
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import logging
logger = logging.getLogger("CoreUtilsEngine")

# ============================================================
#  VALIDATION LAYER
# ============================================================

class CoreValidationLayer:
    """Normalizes, sanitizes, and validates inbound payloads."""

    @staticmethod
    def normalize(payload: Any) -> str:
        if isinstance(payload, dict):
            return json.dumps(payload, sort_keys=True)
        if isinstance(payload, (int, float, bool)):
            return str(payload)
        if not isinstance(payload, str):
            raise ValueError("Payload must be a string, dict, or primitive.")
        return payload

    @staticmethod
    def checksum(payload: str) -> str:
        return hashlib.sha256(payload.encode()).hexdigest()


# ============================================================
#  EMAIL DISPATCHER
# ============================================================

class SovereignEmailDispatcher:
    """Secure SMTP wrapper for outbound corporate communication."""

    def __init__(self):
        self.smtp_server = os.getenv("SOVEREIGN_SMTP_SERVER", "smtp.yoursecuredomain.com")
        self.smtp_port = int(os.getenv("SOVEREIGN_SMTP_PORT", "587"))
        self.sender_email = os.getenv("SOVEREIGN_CORP_EMAIL", "dispatch@yoursecuredomain.com")
        self.sender_password = os.getenv("SOVEREIGN_CORP_PASS", "local_secure_secret")

    def dispatch_manifest_asset(self, recipient_email: str, subject_line: str,
                                html_body: str, attachment_path: Optional[str] = None) -> bool:

        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = recipient_email
        message["Subject"] = subject_line
        message.attach(MIMEText(html_body, "html"))

        if attachment_path and os.path.exists(attachment_path):
            try:
                with open(attachment_path, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition",
                                f"attachment; filename={os.path.basename(attachment_path)}")
                message.attach(part)
            except Exception as e:
                logger.error(f"Attachment error: {str(e)}")
                return False

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            return True
        except Exception as e:
            logger.error(f"SMTP error: {str(e)}")
            return False


# ============================================================
#  SQLITE LEDGER
# ============================================================

class SovereignStateLedger:
    """High-concurrency local SQLite ledger."""

    def __init__(self, db_name: str = "sovereign_operations.db"):
        self.db_path = os.path.join(os.getenv("SOVEREIGN_DATA_DIR", "./"), db_name)
        self._initialize_tables()

    def _initialize_tables(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS operation_logs (
                    session_id TEXT PRIMARY KEY,
                    client_id TEXT NOT NULL,
                    service_type TEXT NOT NULL,
                    execution_epoch REAL NOT NULL,
                    financial_yield_cad REAL DEFAULT 0.0,
                    telemetry_payload TEXT NOT NULL
                )
            """)
            conn.commit()

    def log_transaction_session(self, session_id: str, client_id: str,
                                service_type: str, revenue: float, payload: dict):

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO operation_logs VALUES (?, ?, ?, ?, ?, ?)",
                (session_id, client_id, service_type, time.time(), revenue, json.dumps(payload))
            )
            conn.commit()


# ============================================================
#  STRIPE BILLING GATEWAY
# ============================================================

try:
    import stripe
    stripe.api_version = "2026-05-27.dahlia"
except ImportError:
    stripe = None

class EnterpriseBillingGateway:
    """Stripe SDK wrapper for dunning + subscription workflows."""

    def __init__(self):
        if stripe:
            stripe.api_key = os.getenv("SOVEREIGN_STRIPE_SECRET_KEY", "sk_test_mock")
        self.is_active = stripe is not None

    def construct_dunning_resolution_link(self, customer_id: str,
                                          failed_invoice_id: str,
                                          amount_due: float) -> str:

        if not self.is_active:
            return f"https://checkout.sovereign.io/fallback_resolve?cust={customer_id}&inv={failed_invoice_id}"

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                mode="setup",
                customer=customer_id,
                success_url="https://yourbrand.io/payment-recovered",
                cancel_url="https://yourbrand.io/payment-failed",
            )
            return session.url
        except Exception as e:
            logger.error(f"Stripe error: {str(e)}")
            return f"https://yourbrand.io/manual-billing?amount={amount_due}"


# ============================================================
#  PLAYWRIGHT SCRAPER
# ============================================================

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

class SovereignWebAutomationEngine:
    """Headless browser worker for scraping + citation audits."""

    def __init__(self):
        self.enabled = HAS_PLAYWRIGHT

    def extract_clean_page_source(self, target_url: str) -> Optional[str]:
        if not self.enabled:
            logger.warning("Playwright missing. Run: pip install playwright")
            return None

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(
                    user_agent="Mozilla/5.0 (X11; Linux x86_64) ProductionCrawler/2.0"
                )
                page.goto(target_url, timeout=30000, wait_until="networkidle")
                html = page.content()
                browser.close()
                return html
        except Exception as e:
            logger.error(f"Scraper error: {str(e)}")
            return None


# ============================================================
#  CHECKSUM ENGINE
# ============================================================

class CoreChecksumEngine:
    @staticmethod
    def compute(payload: str) -> Dict[str, Any]:
        return {
            "sha256": hashlib.sha256(payload.encode()).hexdigest(),
            "sha1": hashlib.sha1(payload.encode()).hexdigest(),
            "md5": hashlib.md5(payload.encode()).hexdigest()
        }


# ============================================================
#  INTERNAL ROUTING KERNEL
# ============================================================

class CoreRoutingKernel:
    """Routes tasks to the correct internal engine."""

    def __init__(self):
        self.email = SovereignEmailDispatcher()
        self.ledger = SovereignStateLedger()
        self.billing = EnterpriseBillingGateway()
        self.scraper = SovereignWebAutomationEngine()

    async def route(self, task_type: str, payload: Any) -> Dict[str, Any]:

        if task_type == "send_email":
            ok = self.email.dispatch_manifest_asset(
                payload["recipient"],
                payload["subject"],
                payload["body"],
                payload.get("attachment")
            )
            return {"status": "ok" if ok else "error"}

        if task_type == "log_ledger":
            self.ledger.log_transaction_session(
                payload["session_id"],
                payload["client_id"],
                payload["service_type"],
                payload["revenue"],
                payload["payload"]
            )
            return {"status": "ok"}

        if task_type == "billing_link":
            url = self.billing.construct_dunning_resolution_link(
                payload["customer_id"],
                payload["invoice_id"],
                payload["amount_due"]
            )
            return {"status": "ok", "url": url}

        if task_type == "scrape":
            html = self.scraper.extract_clean_page_source(payload["url"])
            return {"status": "ok", "html": html}

        if task_type == "checksum":
            normalized = CoreValidationLayer.normalize(payload)
            return CoreChecksumEngine.compute(normalized)

        return {"status": "error", "reason": f"Unknown task '{task_type}'"}


# ============================================================
#  ORCHESTRATOR
# ============================================================

class CoreOrchestrator:
    """Coordinates multi-step workflows across utilities."""

    def __init__(self):
        self.kernel = CoreRoutingKernel()

    async def full_system_sweep(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        normalized = CoreValidationLayer.normalize(payload)
        checksum = CoreChecksumEngine.compute(normalized)

        return {
            "session_id": f"CORE-SWEEP-{uuid.uuid4().hex[:6].upper()}",
            "checksum": checksum,
            "timestamp": time.time()
        }


# ============================================================
#  PUBLIC CORE UTILS AGENT
# ============================================================

class CoreUtilsAgent:
    """Primary sovereign utilities engine for ARKA."""

    def __init__(self):
        self.version = "2.0-sovereign"
        self.validator = CoreValidationLayer()
        self.kernel = CoreRoutingKernel()
        self.orchestrator = CoreOrchestrator()
        logger.info("CoreUtilsAgent initialized (sovereign mode).")

    async def route(self, payload: Any) -> Dict[str, Any]:
        normalized = self.validator.normalize(payload)
        checksum = self.validator.checksum(normalized)
        return {"status": "ok", "checksum": checksum}

    async def send_email(self, payload: Dict[str, Any]):
        return await self.kernel.route("send_email", payload)

    async def log_ledger(self, payload: Dict[str, Any]):
        return await self.kernel.route("log_ledger", payload)

    async def billing_link(self, payload: Dict[str, Any]):
        return await self.kernel.route("billing_link", payload)

    async def scrape(self, payload: Dict[str, Any]):
        return await self.kernel.route("scrape", payload)

    async def full_system_sweep(self, payload: Dict[str, Any]):
        return await self.orchestrator.full_system_sweep(payload)

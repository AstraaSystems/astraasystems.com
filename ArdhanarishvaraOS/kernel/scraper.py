#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  Sovereign Scraper Engine — Autonomous GEO + Market Intelligence Harvester
#  File: scraper.py
#===============================================================================

import time
import json
import random
import asyncio
import aiohttp
import hashlib
from typing import Dict, Any, List, Optional

class SovereignScraper:
    """
    High‑resilience asynchronous scraper for GEO audits, citation checks,
    competitor mapping, and visibility scoring.
    """

    def __init__(self, concurrency: int = 8, timeout: int = 12):
        self.concurrency = concurrency
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None

    #---------------------------------------------------------------------------
    #  SESSION MANAGEMENT
    #---------------------------------------------------------------------------
    async def _ensure_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers={
                    "User-Agent": f"ARKA-SovereignScraper/{random.randint(1000,9999)}"
                }
            )

    #---------------------------------------------------------------------------
    #  HASHING FOR FINGERPRINTING
    #---------------------------------------------------------------------------
    def fingerprint(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    #---------------------------------------------------------------------------
    #  SINGLE PAGE FETCH
    #---------------------------------------------------------------------------
    async def fetch(self, url: str) -> Dict[str, Any]:
        await self._ensure_session()

        try:
            async with self._session.get(url) as resp:
                text = await resp.text()
                return {
                    "url": url,
                    "status": resp.status,
                    "content": text,
                    "fingerprint": self.fingerprint(text),
                    "timestamp": time.time()
                }
        except Exception as e:
            return {
                "url": url,
                "status": 0,
                "error": str(e),
                "timestamp": time.time()
            }

    #---------------------------------------------------------------------------
    #  BULK SCRAPE WITH CONCURRENCY
    #---------------------------------------------------------------------------
    async def scrape_bulk(self, urls: List[str]) -> List[Dict[str, Any]]:
        sem = asyncio.Semaphore(self.concurrency)

        async def bounded_fetch(u):
            async with sem:
                return await self.fetch(u)

        tasks = [bounded_fetch(u) for u in urls]
        return await asyncio.gather(*tasks)

    #---------------------------------------------------------------------------
    #  CITATION AUDIT
    #---------------------------------------------------------------------------
    async def citation_audit(self, business_name: str, urls: List[str]) -> Dict[str, Any]:
        results = await self.scrape_bulk(urls)

        score = 0
        total = len(results)

        for r in results:
            if r.get("content") and business_name.lower() in r["content"].lower():
                score += 1

        return {
            "business": business_name,
            "total_sources": total,
            "matching_sources": score,
            "visibility_score": (score / total) if total > 0 else 0.0,
            "timestamp": time.time()
        }

    #---------------------------------------------------------------------------
    #  COMPETITOR MAPPING
    #---------------------------------------------------------------------------
    async def competitor_map(self, keywords: List[str], urls: List[str]) -> Dict[str, Any]:
        results = await self.scrape_bulk(urls)

        competitors = {}

        for r in results:
            content = r.get("content", "").lower()
            for kw in keywords:
                if kw.lower() in content:
                    competitors.setdefault(kw, 0)
                    competitors[kw] += 1

        return {
            "keywords": keywords,
            "competitor_hits": competitors,
            "timestamp": time.time()
        }

    #---------------------------------------------------------------------------
    #  CLEANUP
    #---------------------------------------------------------------------------
    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

#===============================================================================
#  END OF FILE — scraper.py
#===============================================================================

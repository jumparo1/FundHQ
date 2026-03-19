"""
Phase 1: Data Infrastructure
=============================
Real-time data feeds, macro intelligence, on-chain expansion.
Collects market data from multiple sources and pushes to Firebase.
"""

import asyncio
import aiohttp
import time
from datetime import datetime, timezone
from typing import Optional
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.firebase import fb_write, fb_read, push_alert, now_iso
from shared.config import WATCH_COINS


# ===== COINGECKO =====

async def fetch_coingecko_prices(session: aiohttp.ClientSession, coins: list = None) -> dict:
    """Fetch current prices, 24h change, volume from CoinGecko."""
    coin_ids = {
        "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana",
        "HYPE": "hyperliquid", "DOGE": "dogecoin", "SUI": "sui",
        "AVAX": "avalanche-2", "LINK": "chainlink", "PEPE": "pepe",
        "WIF": "dogwifcoin", "TAO": "bittensor", "RENDER": "render-token",
        "FET": "artificial-superintelligence-alliance",
        "AAVE": "aave", "UNI": "uniswap", "GMX": "gmx",
        "PENDLE": "pendle", "ARB": "arbitrum", "OP": "optimism",
        "ONDO": "ondo-finance", "MKR": "maker",
    }
    symbols = coins or WATCH_COINS
    ids = [coin_ids.get(s, s.lower()) for s in symbols]
    ids_str = ",".join(ids)

    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={ids_str}&sparkline=false&price_change_percentage=1h,24h,7d"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status == 429:
                return {"error": "rate_limited"}
            data = await resp.json()
            result = {}
            for coin in data:
                symbol = coin.get("symbol", "").upper()
                result[symbol] = {
                    "price": coin.get("current_price"),
                    "market_cap": coin.get("market_cap"),
                    "volume_24h": coin.get("total_volume"),
                    "change_1h": coin.get("price_change_percentage_1h_in_currency"),
                    "change_24h": coin.get("price_change_percentage_24h"),
                    "change_7d": coin.get("price_change_percentage_7d_in_currency"),
                    "ath": coin.get("ath"),
                    "ath_change": coin.get("ath_change_percentage"),
                    "fdv": coin.get("fully_diluted_valuation"),
                    "circulating_supply": coin.get("circulating_supply"),
                    "total_supply": coin.get("total_supply"),
                    "updated": now_iso(),
                }
            return result
    except Exception as e:
        return {"error": str(e)}


async def fetch_coingecko_trending(session: aiohttp.ClientSession) -> list:
    """Fetch trending coins from CoinGecko."""
    url = "https://api.coingecko.com/api/v3/search/trending"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            data = await resp.json()
            trending = []
            for item in data.get("coins", [])[:15]:
                coin = item.get("item", {})
                trending.append({
                    "symbol": coin.get("symbol", "").upper(),
                    "name": coin.get("name"),
                    "market_cap_rank": coin.get("market_cap_rank"),
                    "price_btc": coin.get("price_btc"),
                    "score": coin.get("score"),
                })
            return trending
    except Exception as e:
        return []


# ===== BINANCE FUTURES =====

async def fetch_binance_funding(session: aiohttp.ClientSession, symbols: list = None) -> dict:
    """Fetch funding rates from Binance Futures."""
    url = "https://fapi.binance.com/fapi/v1/premiumIndex"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            data = await resp.json()
            result = {}
            watch = [f"{s}USDT" for s in (symbols or WATCH_COINS)]
            for item in data:
                sym = item.get("symbol", "")
                if sym in watch or not symbols:
                    base = sym.replace("USDT", "").replace("BUSD", "")
                    result[base] = {
                        "funding_rate": float(item.get("lastFundingRate", 0)),
                        "mark_price": float(item.get("markPrice", 0)),
                        "index_price": float(item.get("indexPrice", 0)),
                        "next_funding": item.get("nextFundingTime"),
                    }
            return result
    except Exception as e:
        return {"error": str(e)}


async def fetch_binance_oi(session: aiohttp.ClientSession, symbols: list = None) -> dict:
    """Fetch open interest from Binance Futures."""
    url = "https://fapi.binance.com/fapi/v1/openInterest"
    result = {}
    targets = [f"{s}USDT" for s in (symbols or ["BTC", "ETH", "SOL"])]
    for sym in targets:
        try:
            async with session.get(f"{url}?symbol={sym}", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                data = await resp.json()
                base = sym.replace("USDT", "")
                result[base] = {
                    "open_interest": float(data.get("openInterest", 0)),
                    "symbol": sym,
                }
        except:
            pass
    return result


# ===== MACRO INTELLIGENCE =====

async def fetch_fear_greed(session: aiohttp.ClientSession) -> dict:
    """Fetch Crypto Fear & Greed Index."""
    url = "https://api.alternative.me/fng/?limit=7"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            data = await resp.json()
            entries = data.get("data", [])
            if entries:
                latest = entries[0]
                return {
                    "value": int(latest.get("value", 50)),
                    "classification": latest.get("value_classification", "Neutral"),
                    "timestamp": latest.get("timestamp"),
                    "history": [{"value": int(e["value"]), "date": e.get("timestamp")} for e in entries[:7]],
                }
            return {"value": 50, "classification": "Neutral"}
    except Exception as e:
        return {"value": 50, "classification": "Unknown", "error": str(e)}


async def fetch_btc_dominance(session: aiohttp.ClientSession) -> dict:
    """Fetch BTC dominance from CoinGecko global data."""
    url = "https://api.coingecko.com/api/v3/global"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            data = await resp.json()
            gd = data.get("data", {})
            return {
                "btc_dominance": gd.get("market_cap_percentage", {}).get("btc", 0),
                "eth_dominance": gd.get("market_cap_percentage", {}).get("eth", 0),
                "total_market_cap": gd.get("total_market_cap", {}).get("usd", 0),
                "total_volume": gd.get("total_volume", {}).get("usd", 0),
                "active_cryptos": gd.get("active_cryptocurrencies", 0),
                "market_cap_change_24h": gd.get("market_cap_change_percentage_24h_usd", 0),
            }
    except Exception as e:
        return {"error": str(e)}


async def fetch_defi_tvl(session: aiohttp.ClientSession) -> dict:
    """Fetch DeFi TVL data from DefiLlama."""
    url = "https://api.llama.fi/v2/historicalChainTvl"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            data = await resp.json()
            if isinstance(data, list) and data:
                latest = data[-1]
                prev_week = data[-8] if len(data) > 7 else data[0]
                tvl_now = latest.get("tvl", 0)
                tvl_week = prev_week.get("tvl", 0)
                change = ((tvl_now - tvl_week) / tvl_week * 100) if tvl_week else 0
                return {
                    "total_tvl": tvl_now,
                    "tvl_change_7d": round(change, 2),
                    "updated": now_iso(),
                }
            return {}
    except Exception as e:
        return {"error": str(e)}


async def fetch_protocol_tvl(session: aiohttp.ClientSession, protocols: list = None) -> list:
    """Fetch TVL for specific protocols from DefiLlama."""
    url = "https://api.llama.fi/protocols"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            data = await resp.json()
            watch = set(p.lower() for p in (protocols or [
                "aave", "uniswap", "gmx", "pendle", "lido", "makerdao",
                "compound", "curve-dex", "pancakeswap", "raydium",
            ]))
            result = []
            for p in data:
                slug = p.get("slug", "").lower()
                name = p.get("name", "").lower()
                if slug in watch or name in watch:
                    result.append({
                        "name": p.get("name"),
                        "symbol": p.get("symbol"),
                        "tvl": p.get("tvl"),
                        "chain": p.get("chain"),
                        "chains": p.get("chains", []),
                        "category": p.get("category"),
                        "change_1d": p.get("change_1d"),
                        "change_7d": p.get("change_7d"),
                        "mcap": p.get("mcap"),
                        "fdv": p.get("fdv"),
                    })
            return result
    except Exception as e:
        return []


# ===== HYPERLIQUID EXPANDED =====

async def fetch_hl_market_data(session: aiohttp.ClientSession) -> dict:
    """Fetch Hyperliquid market-wide data."""
    url = "https://api.hyperliquid.xyz/info"
    try:
        payload = {"type": "metaAndAssetCtxs"}
        async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            data = await resp.json()
            if isinstance(data, list) and len(data) >= 2:
                meta = data[0]
                ctxs = data[1]
                universe = meta.get("universe", [])
                result = {}
                for i, asset in enumerate(universe):
                    if i < len(ctxs):
                        ctx = ctxs[i]
                        coin = asset.get("name", "")
                        result[coin] = {
                            "mark_price": float(ctx.get("markPx", 0)),
                            "funding": float(ctx.get("funding", 0)),
                            "open_interest": float(ctx.get("openInterest", 0)),
                            "volume_24h": float(ctx.get("dayNtlVlm", 0)),
                            "premium": float(ctx.get("premium", 0)),
                        }
                return result
            return {}
    except Exception as e:
        return {"error": str(e)}


# ===== DEXSCREENER =====

async def fetch_dex_trending(session: aiohttp.ClientSession) -> list:
    """Fetch trending pairs from Dexscreener."""
    url = "https://api.dexscreener.com/token-boosts/top/v1"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            data = await resp.json()
            if isinstance(data, list):
                return data[:20]
            return []
    except:
        return []


# ===== MASTER FEED RUNNER =====

class DataFeedManager:
    """Manages all data feeds and pushes to Firebase on schedule."""

    def __init__(self):
        self.prices = {}
        self.funding = {}
        self.macro = {}
        self.hl_data = {}
        self.last_update = {}

    async def run_full_update(self) -> dict:
        """Run all feeds and push to Firebase."""
        async with aiohttp.ClientSession() as session:
            # Parallel fetch all feeds
            results = await asyncio.gather(
                fetch_coingecko_prices(session),
                fetch_binance_funding(session),
                fetch_binance_oi(session),
                fetch_fear_greed(session),
                fetch_btc_dominance(session),
                fetch_defi_tvl(session),
                fetch_hl_market_data(session),
                fetch_coingecko_trending(session),
                return_exceptions=True,
            )

            prices, funding, oi, fng, dominance, tvl, hl_data, trending = results

            # Store locally
            if isinstance(prices, dict) and "error" not in prices:
                self.prices = prices
            if isinstance(funding, dict) and "error" not in funding:
                self.funding = funding

            # Build macro data
            self.macro = {
                "fear_greed": fng if isinstance(fng, dict) else {},
                "btc_dominance": dominance if isinstance(dominance, dict) else {},
                "defi_tvl": tvl if isinstance(tvl, dict) else {},
                "updated": now_iso(),
            }

            if isinstance(hl_data, dict) and "error" not in hl_data:
                self.hl_data = hl_data

            # Push to Firebase
            update = {
                "prices": self.prices,
                "funding": self.funding if isinstance(self.funding, dict) else {},
                "oi": oi if isinstance(oi, dict) else {},
                "macro": self.macro,
                "trending": trending if isinstance(trending, list) else [],
                "updated": now_iso(),
            }

            try:
                fb_write("/fundHQ/marketData", update)
            except Exception as e:
                print(f"[FEEDS] Firebase write error: {e}")

            self.last_update = {"time": now_iso(), "feeds": len([r for r in results if not isinstance(r, Exception)])}
            return update

    async def run_prices_only(self) -> dict:
        """Quick price-only update."""
        async with aiohttp.ClientSession() as session:
            prices = await fetch_coingecko_prices(session)
            if isinstance(prices, dict) and "error" not in prices:
                self.prices = prices
                try:
                    fb_write("/fundHQ/marketData/prices", prices)
                    fb_write("/fundHQ/marketData/updated", now_iso())
                except:
                    pass
            return prices

    async def get_macro_snapshot(self) -> dict:
        """Get current macro data."""
        async with aiohttp.ClientSession() as session:
            fng, dominance, tvl = await asyncio.gather(
                fetch_fear_greed(session),
                fetch_btc_dominance(session),
                fetch_defi_tvl(session),
                return_exceptions=True,
            )
            return {
                "fear_greed": fng if isinstance(fng, dict) else {},
                "btc_dominance": dominance if isinstance(dominance, dict) else {},
                "defi_tvl": tvl if isinstance(tvl, dict) else {},
                "updated": now_iso(),
            }

    def get_status(self) -> dict:
        return {
            "prices_count": len(self.prices),
            "funding_count": len(self.funding),
            "macro_available": bool(self.macro),
            "hl_coins": len(self.hl_data),
            "last_update": self.last_update,
        }

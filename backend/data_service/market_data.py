"""Market data provider - fetches K-line (OHLCV) data from external sources.

MVP uses AKShare for A-share data. Designed for easy extension to other sources
(Yahoo Finance, Tushare, etc.) via the MarketDataProvider protocol.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Protocol

logger = logging.getLogger(__name__)


@dataclass
class KLine:
    """Single K-line (candlestick) data point."""
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    turnover: float = 0.0


class MarketDataProvider(Protocol):
    """Protocol for market data sources."""

    def get_klines(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        period: str = "daily",
    ) -> list[KLine]: ...

    def get_index_klines(
        self,
        index_code: str,
        start_date: str,
        end_date: str,
    ) -> list[KLine]: ...


class AKShareProvider:
    """A-share market data via AKShare (free, no API key needed)."""

    def get_klines(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        period: str = "daily",
    ) -> list[KLine]:
        try:
            import akshare as ak

            symbol_clean = symbol.strip().upper()
            if len(symbol_clean) == 6 and symbol_clean.isdigit():
                df = ak.stock_zh_a_hist(
                    symbol=symbol_clean,
                    period=period,
                    start_date=start_date.replace("-", ""),
                    end_date=end_date.replace("-", ""),
                    adjust="qfq",
                )
                return [
                    KLine(
                        date=str(row["日期"]),
                        open=float(row["开盘"]),
                        high=float(row["最高"]),
                        low=float(row["最低"]),
                        close=float(row["收盘"]),
                        volume=float(row["成交量"]),
                        turnover=float(row.get("成交额", 0)),
                    )
                    for _, row in df.iterrows()
                ]
            return []
        except ImportError:
            logger.warning("akshare not installed, market data unavailable")
            return []
        except Exception as e:
            logger.error("AKShare fetch failed for %s: %s", symbol, e)
            return []

    def get_index_klines(
        self,
        index_code: str,
        start_date: str,
        end_date: str,
    ) -> list[KLine]:
        try:
            import akshare as ak

            df = ak.stock_zh_index_daily(symbol=index_code)
            df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
            return [
                KLine(
                    date=str(row["date"]),
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row.get("volume", 0)),
                )
                for _, row in df.iterrows()
            ]
        except ImportError:
            logger.warning("akshare not installed, index data unavailable")
            return []
        except Exception as e:
            logger.error("AKShare index fetch failed for %s: %s", index_code, e)
            return []


class NullProvider:
    """Fallback when no market data source is available."""

    def get_klines(self, symbol: str, start_date: str, end_date: str, period: str = "daily") -> list[KLine]:
        return []

    def get_index_klines(self, index_code: str, start_date: str, end_date: str) -> list[KLine]:
        return []


def get_provider() -> MarketDataProvider:
    """Get the best available market data provider."""
    try:
        import akshare  # noqa: F401
        return AKShareProvider()
    except ImportError:
        logger.info("akshare not available, using NullProvider")
        return NullProvider()

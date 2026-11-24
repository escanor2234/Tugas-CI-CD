import logging
from pathlib import Path

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

TICKERS = ("EXCL.JK", "ISAT.JK", "TLKM.JK")
TIMEZONE = "Asia/Jakarta"
OHLCV = ["Open", "High", "Low", "Close", "Volume"]
KEY = ["timestamp_wib", "ticker"]


def ambil_batch(output: Path) -> bool:
    mulai_batch = pd.Timestamp.now(tz=TIMEZONE)
    data = yf.download(
        list(TICKERS),
        period="5d",
        interval="2m",
        group_by="ticker",
        auto_adjust=False,
        ignore_tz=False,
        multi_level_index=True,
        progress=False,
        timeout=15,
    )

    frames = []
    for ticker in TICKERS:
        if data.empty or ticker not in data.columns.get_level_values(0):
            logger.warning("Tidak ada data untuk %s", ticker)
            continue

        frame = data[ticker][OHLCV].dropna().copy()
        frame.index = frame.index.tz_convert(TIMEZONE)
        # Jangan simpan candle yang belum berakhir saat permintaan dimulai.
        frame = frame.loc[frame.index + pd.Timedelta(minutes=2) <= mulai_batch]
        if frame.empty:
            logger.warning("Tidak ada candle yang sudah berakhir untuk %s", ticker)
            continue

        frame.columns = [kolom.lower() for kolom in OHLCV]
        frame.insert(0, "ticker", ticker)
        frame.insert(0, "timestamp_wib", frame.index.map(pd.Timestamp.isoformat))
        frames.append(frame)

    if not frames:
        return False

    batch = pd.concat(frames, ignore_index=True)
    if output.exists():
        lama = pd.read_csv(output)
        gabungan = pd.concat([lama, batch], ignore_index=True)
    else:
        gabungan = batch
    gabungan = gabungan.drop_duplicates(subset=KEY, keep="last").sort_values(KEY)

    output.parent.mkdir(parents=True, exist_ok=True)
    sementara = output.with_name(output.name + ".tmp")
    gabungan.to_csv(sementara, index=False)
    sementara.replace(output)
    logger.info("Batch: %d/%d ticker; CSV: %d candle (%s)",
                len(frames), len(TICKERS), len(gabungan), output)
    return len(frames) == len(TICKERS)

import argparse
import logging
import os
import time
from pathlib import Path

from .scraper import ambil_batch


BATCH_SECONDS = 120


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ambil candle saham 2 menit dari Yahoo Finance.")
    parser.add_argument("--once", action="store_true", help="Jalankan satu batch lalu keluar.")
    parser.add_argument(
        "--output", type=Path, default=os.environ.get("OUTPUT_CSV") or "data_saham_2menit.csv",
        help="Lokasi file CSV. Default dapat diatur dengan OUTPUT_CSV.",
    )
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    try:
        while True:
            mulai = time.monotonic()
            try:
                lengkap = ambil_batch(args.output)
            except Exception:
                logging.exception("Batch gagal")
                lengkap = False
            if args.once:
                return 0 if lengkap else 1
            time.sleep(max(0, BATCH_SECONDS - (time.monotonic() - mulai)))
    except KeyboardInterrupt:
        logging.info("Batch dihentikan.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())

# Batch saham Yahoo Finance

Skrip mengambil candle OHLCV 2 menit untuk XLSMART (`EXCL.JK`), Indosat (`ISAT.JK`), dan Telkom Indonesia (`TLKM.JK`).

## Jalankan dengan uv

```powershell
uv sync --locked
uv run --locked python -m src.main
```

Memerlukan [uv](https://docs.astral.sh/uv/getting-started/installation/) dan Python 3.12 atau lebih baru.

Batch pertama langsung berjalan, lalu skrip mengambil data lagi setiap 120 detik selama proses aktif. Hentikan dengan `Ctrl+C`. Untuk satu batch saja:

```powershell
uv run --locked python -m src.main --once
```

Hasil disimpan ke `data_saham_2menit.csv` (atau gunakan `--output` untuk mengganti lokasi), dengan kolom `timestamp_wib,ticker,open,high,low,close,volume`. Setiap batch meminta riwayat `5d` agar candle yang terlambat muncul masih bisa tersimpan. Baris dengan ticker dan waktu candle yang sama diperbarui, bukan digandakan. Jalankan hanya satu proses untuk setiap file CSV.

Waktu candle adalah waktu awal candle dalam WIB (UTC+7). Polling setiap dua menit bukan jaminan harga real-time: Yahoo Finance bisa menunda data dan saat bursa tutup tidak ada candle baru.

Opsi `--output` mengalahkan variabel lingkungan `OUTPUT_CSV`. Untuk memakai konfigurasi contoh, jalankan `uv run --locked --env-file .env.example python -m src.main --once`.

## Tes dan Docker

```powershell
uv run --locked pytest
docker build -t batch-saham .
docker run --rm -v "${PWD}:/app/data" batch-saham --once
```

Tes memakai respons Yahoo Finance tiruan, tanpa akses jaringan. Docker menyimpan CSV ke `/app/data`; contoh di atas memasang folder saat ini agar CSV tetap ada setelah container dihapus. Hilangkan `--once` untuk menjalankan batch berulang.

Workflow CI menjalankan tes serta memeriksa build dan CLI Docker. Workflow CD dijalankan manual dari cabang `main` lewat tab Actions dan memublikasikan image ke GitHub Container Registry dengan commit SHA sebagai tag. Workflow CD tidak menjalankan container di server.

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

## Otomatisasi GitHub Actions

Setelah CI sukses untuk push ke `main`, workflow CD memublikasikan image GHCR dengan tag commit SHA dan `main`. Workflow **Scraper** membuat Azure Container Instance sementara setelah CD sukses, setiap lima menit (`*/5 * * * *`), atau secara manual dari tab **Actions** pada branch `main`. Pemicu CD memakai tag commit; jadwal dan pemicu manual memakai tag `main`. Paket GHCR harus publik agar ACI bisa menariknya tanpa kredensial. GitHub Actions hanya memicu, memeriksa hasil, dan menghapus instance; kode scraper berjalan di Azure. Jadwal bisa terlambat dan baru aktif di default branch. Tidak menggunakan ACR atau Azure Container Apps Job.

Setiap eksekusi mengunduh CSV lama jika tersedia dan mengunggah hasil hanya jika batch sukses. File disimpan di Storage Account `tugastcbacicd`, container Blob `batch-saham`, dengan nama `data_saham_2menit.csv`. Eksekusi tidak berjalan bersamaan, dan perubahan dari klien lain dilindungi oleh ETag.

Pertahankan repository variables `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, dan `AZURE_SUBSCRIPTION_ID` untuk OIDC dari branch `main`. Aplikasi Entra untuk GitHub harus bisa membuat, membaca (termasuk log), dan menghapus grup ACI di `kelompok7`, serta memasang managed identity `saham-scraper-aci` (misalnya dengan **Managed Identity Operator** pada identity tersebut). Managed identity container, bukan aplikasi GitHub, membutuhkan **Storage Blob Data Contributor** pada container Blob `batch-saham`. Tunggu CD memublikasikan image baru sebelum menjalankan scraper manual.

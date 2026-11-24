import pandas as pd

from src import scraper


def test_batch_simpan_wib_dan_perbarui_tanpa_duplikat(monkeypatch, tmp_path):
    waktu = pd.DatetimeIndex(["2025-01-02 02:00:00", "2099-01-02 02:00:00"], tz="UTC")
    kolom = pd.MultiIndex.from_product([scraper.TICKERS, scraper.OHLCV])
    data = pd.DataFrame(100, index=waktu, columns=kolom)

    def download(tickers, **kwargs):
        assert tickers == list(scraper.TICKERS)
        assert kwargs["interval"] == "2m"
        return data

    monkeypatch.setattr(scraper.yf, "download", download)
    output = tmp_path / "data" / "saham.csv"
    assert scraper.ambil_batch(output)

    data.loc[waktu[0], ("EXCL.JK", "Close")] = 105
    assert scraper.ambil_batch(output)
    hasil = pd.read_csv(output)
    assert len(hasil) == len(scraper.TICKERS)
    assert set(hasil["ticker"]) == set(scraper.TICKERS)
    assert set(hasil["timestamp_wib"]) == {"2025-01-02T09:00:00+07:00"}
    assert hasil.loc[hasil["ticker"] == "EXCL.JK", "close"].item() == 105


def test_batch_kosong_tidak_membuat_csv(monkeypatch, tmp_path):
    monkeypatch.setattr(scraper.yf, "download", lambda *args, **kwargs: pd.DataFrame())
    output = tmp_path / "saham.csv"
    assert not scraper.ambil_batch(output)
    assert not output.exists()

from unittest.mock import Mock

import pytest

from src import main


@pytest.mark.parametrize(("lengkap", "exit_code"), [(True, 0), (False, 1)])
def test_once_jalankan_satu_batch(monkeypatch, tmp_path, lengkap, exit_code):
    output = tmp_path / "saham.csv"
    batch = Mock(return_value=lengkap)
    monkeypatch.setattr(main, "ambil_batch", batch)
    monkeypatch.setenv("OUTPUT_CSV", "diabaikan.csv")

    assert main.main(["--once", "--output", str(output)]) == exit_code
    batch.assert_called_once_with(output)


def test_loop_jeda_dikurangi_durasi_batch(monkeypatch, tmp_path):
    output = tmp_path / "saham.csv"
    batch = Mock(return_value=True)
    tidur = Mock(side_effect=KeyboardInterrupt)
    monkeypatch.setenv("OUTPUT_CSV", str(output))
    monkeypatch.setattr(main, "ambil_batch", batch)
    monkeypatch.setattr(main, "time", Mock(monotonic=Mock(side_effect=[10, 15]), sleep=tidur))

    assert main.main([]) == 0
    batch.assert_called_once_with(output)
    tidur.assert_called_once_with(115)

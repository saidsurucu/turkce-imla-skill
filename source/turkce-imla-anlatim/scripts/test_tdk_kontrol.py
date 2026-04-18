#!/usr/bin/env python3
"""
tdk_kontrol.py için temel testler.

Çalıştırmak için:
    python3 scripts/test_tdk_kontrol.py
    TDK_KONTROL_NO_CACHE=1 python3 scripts/test_tdk_kontrol.py  # cache'siz

TDK API'sine gerçek istek atar; ağ gereklidir.
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from tdk_kontrol import (
    _stem_candidates,
    yazim_kontrol,
    toplu_yazim_kontrol,
)


def test_stem_candidates():
    # Aşamalı sıyırma: halılarımızın → halı
    candidates = list(_stem_candidates("halılarımızın"))
    assert "halı" in candidates, f"'halı' beklendi, bulundu: {candidates}"

    # Tek ek: kitaplar → kitap
    candidates = list(_stem_candidates("kitaplar"))
    assert "kitap" in candidates, f"'kitap' beklendi, bulundu: {candidates}"

    # Kısa kelimede ek sıyırma yapmaz (minimum 3 karakter kök)
    candidates = list(_stem_candidates("al"))
    assert "al" not in candidates, "çok kısa kelime sıyrılmamalı"
    print("✓ test_stem_candidates")


def test_direct_lookup():
    # Düzeltme işareti tespiti
    r = yazim_kontrol("hikaye")
    assert r["bulundu"], "'hikaye' bulunmalı"
    assert any(s["dogru_yazim"] == "hikâye" for s in r["sonuclar"]), (
        "'hikâye' önerisi beklenir"
    )
    print("✓ test_direct_lookup")


def test_stemmer_fallback():
    # Çekimli biçim morfoloji fallback ile kökle eşleşmeli
    r = yazim_kontrol("halılarımızın")
    assert r["bulundu"], "morfoloji fallback 'halı' köküyle eşleşmeli"
    assert r.get("kok") == "halı", f"kök 'halı' bekleniyor, got: {r.get('kok')}"
    print("✓ test_stemmer_fallback")


def test_not_found_message():
    # Gerçekten Türkçede olmayan bir kelime
    r = yazim_kontrol("xylophonezzz")
    assert not r["bulundu"], "uydurma kelime bulunmamalı"
    assert "not_" in r, "açıklama mesajı beklenir"
    assert "sözlük maddesi" in r["not_"], "iyileştirilmiş mesaj formatı"
    print("✓ test_not_found_message")


def test_batch_parallel():
    # Toplu kontrol paralel çalışmalı, sıra korunmalı
    kelimeler = ["hikaye", "kağıt", "dükkan"]
    sonuclar = toplu_yazim_kontrol(kelimeler)
    assert len(sonuclar) == len(kelimeler)
    assert sonuclar[0]["kelime"] == "hikaye"
    assert sonuclar[1]["kelime"] == "kağıt"
    print("✓ test_batch_parallel")


def test_cache():
    # Cache dizininin oluşturulduğunu doğrula
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["TDK_KONTROL_CACHE_DIR"] = tmp
        yazim_kontrol("hikaye")
        cache_files = list(Path(tmp).glob("*.json"))
        assert len(cache_files) > 0, "cache dosyası oluşturulmalı"
    print("✓ test_cache")


if __name__ == "__main__":
    test_stem_candidates()
    test_direct_lookup()
    test_stemmer_fallback()
    test_not_found_message()
    test_batch_parallel()
    test_cache()
    print("\nTüm testler geçti.")

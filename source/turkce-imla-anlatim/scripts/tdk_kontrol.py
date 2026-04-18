#!/usr/bin/env python3
"""
TDK Sözlük API aracılığıyla kelime kontrolü.

Kullanım:
    python3 tdk_kontrol.py yazim <kelime>        # Yazım Kılavuzu kontrolü
    python3 tdk_kontrol.py anlam <kelime>         # Güncel Türkçe Sözlük (anlam)
    python3 tdk_kontrol.py deyim <kelime>         # Atasözleri ve Deyimler
    python3 tdk_kontrol.py kontrol <kelime1> <kelime2> ...  # Toplu yazım kontrolü

API Endpoints:
    - Yazım Kılavuzu:  https://sozluk.gov.tr/yazim?ara=KELIME
    - GTS (Anlam):      https://sozluk.gov.tr/gts?ara=KELIME
    - Atasözü/Deyim:    https://sozluk.gov.tr/atasozu?ara=KELIME

Ortam değişkenleri (opsiyonel):
    TDK_KONTROL_NO_CACHE=1   # Yerel cache'i devre dışı bırakır
    TDK_KONTROL_NO_STEM=1    # Morfoloji (kök çıkarma) geri dönüşünü kapatır
    TDK_KONTROL_CACHE_DIR    # Cache dizini (varsayılan: ~/.cache/tdk-kontrol)
    TDK_KONTROL_CACHE_TTL    # Cache süresi, saniye (varsayılan: 604800 = 7 gün)
"""

import json
import os
import sys
import time
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


BASE_URL = "https://sozluk.gov.tr"

# Ek listesi — uzunluktan kısaya, sıra önemli.
# Çekimli formları sözlük maddesine indirmek için kullanılır.
# TDK Yazım Kılavuzu'nda sözlük maddeleri kök/mastar biçimindedir;
# çekim ekleri alanlar "bulunamadı" döner. Bu listeyle aşamalı soyma yapılır.
_EKLER = [
    # Birleşik ekler (önce çok-ekli biçimler denenir)
    "lerinin",
    "larinin",
    "lerinde",
    "larinda",
    "lerinden",
    "larindan",
    "leriyle",
    "lariyla",
    "lerini",
    "larini",
    "imizin",
    "umuzun",
    "unuzun",
    "inizin",
    "lerdir",
    "lardir",
    "miştir",
    "mıştır",
    "muştur",
    "müştür",
    # Ek-fiil birleşikleri
    "iyorsa",
    "iyorduk",
    "iyordu",
    "iyormuş",
    "ecektir",
    "acaktir",
    "eceğim",
    "acağım",
    # Tek ekler (uzundan kısaya)
    "lerden",
    "lardan",
    "dirler",
    "durler",
    "dürler",
    "iniz",
    "ınız",
    "unuz",
    "ünüz",
    "leri",
    "ları",
    "imiz",
    "ımız",
    "umuz",
    "ümüz",
    "idir",
    "ıdır",
    "udur",
    "üdür",
    "dir",
    "dır",
    "dur",
    "dür",
    "tir",
    "tır",
    "tur",
    "tür",
    "yim",
    "yım",
    "yum",
    "yüm",
    "ydim",
    "ydım",
    "ydum",
    "ydüm",
    "ydi",
    "ydı",
    "ydu",
    "ydü",
    "miş",
    "mış",
    "muş",
    "müş",
    "nin",
    "nın",
    "nun",
    "nün",
    "yle",
    "yla",
    "ler",
    "lar",
    "den",
    "dan",
    "ten",
    "tan",
    "de",
    "da",
    "te",
    "ta",
    "im",
    "ım",
    "um",
    "üm",
    "in",
    "ın",
    "un",
    "ün",
    "si",
    "sı",
    "su",
    "sü",
    "ya",
    "ye",
    "le",
    "la",
    "ki",
    "ce",
    "ca",
    "e",
    "a",
    "i",
    "ı",
    "u",
    "ü",
    "y",
    # Fiil ekleri (-mak/-mek sonrası)
    "mek",
    "mak",
]


def _cache_enabled() -> bool:
    return os.environ.get("TDK_KONTROL_NO_CACHE") != "1"


def _stem_enabled() -> bool:
    return os.environ.get("TDK_KONTROL_NO_STEM") != "1"


def _cache_dir() -> Path:
    base = os.environ.get("TDK_KONTROL_CACHE_DIR") or "~/.cache/tdk-kontrol"
    return Path(base).expanduser()


def _cache_ttl() -> int:
    try:
        return int(os.environ.get("TDK_KONTROL_CACHE_TTL", "604800"))
    except ValueError:
        return 604800


def _cache_get(endpoint: str, kelime: str):
    if not _cache_enabled():
        return None
    cache_dir = _cache_dir()
    key = urllib.parse.quote(f"{endpoint}_{kelime}", safe="")
    path = cache_dir / f"{key}.json"
    if not path.exists():
        return None
    if time.time() - path.stat().st_mtime > _cache_ttl():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def _cache_set(endpoint: str, kelime: str, data) -> None:
    if not _cache_enabled():
        return
    cache_dir = _cache_dir()
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return
    key = urllib.parse.quote(f"{endpoint}_{kelime}", safe="")
    path = cache_dir / f"{key}.json"
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except OSError:
        pass


def tdk_fetch(endpoint: str, kelime: str):
    """TDK API'ye istek gönderir, sonucu cacheler."""
    cached = _cache_get(endpoint, kelime)
    if cached is not None:
        return None if cached == "_NOT_FOUND_" else cached

    encoded = urllib.parse.quote(kelime, safe="")
    url = f"{BASE_URL}/{endpoint}?ara={encoded}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8").strip())
            if isinstance(data, dict) and "error" in data:
                _cache_set(endpoint, kelime, "_NOT_FOUND_")
                return None
            _cache_set(endpoint, kelime, data)
            return data
    except Exception as e:
        print(f"HATA: {e}", file=sys.stderr)
        return None


def _stem_candidates(kelime: str):
    """
    Kelimeden ek soyarak aday kökleri üretir.
    Hem tek ek sıyrılarak hem de aşamalı (iteratif) sıyrılarak adaylar döndürülür.
    Örn: halılarımızın → halılarımız → halılar → halı
    """
    kelime_lower = kelime.lower()
    seen = set()
    # BFS benzeri: her turda her mevcut adaydan yeni kök türet
    frontier = [kelime_lower]
    for _ in range(4):  # en fazla 4 seviye ek sıyır
        new_frontier = []
        for w in frontier:
            for ek in _EKLER:
                if len(w) - len(ek) >= 3 and w.endswith(ek):
                    kok = w[: -len(ek)]
                    if kok not in seen:
                        seen.add(kok)
                        new_frontier.append(kok)
                        yield kok
        if not new_frontier:
            break
        frontier = new_frontier


def yazim_kontrol(kelime: str) -> dict:
    """
    Yazım Kılavuzu'nda kelimeyi arar. Bulamazsa ek soyarak yeniden dener.

    Döndürdüğü dict:
      - bulundu: bool
      - kelime: sorgulanan orijinal kelime
      - sonuclar: list[dict] (her biri: dogru_yazim, ekler)
      - kok: str (morfoloji fallback ile bulunduğunda, kökün kendisi)
      - not_: str (çekimli biçim açıklaması veya öneri metni)
    """
    result = tdk_fetch("yazim", kelime)
    if result:
        return {
            "bulundu": True,
            "kelime": kelime,
            "sonuclar": [
                {
                    "dogru_yazim": entry.get("sozu", "").strip(),
                    "ekler": entry.get("ekler", "").strip() or None,
                }
                for entry in result
            ],
        }

    # Morfoloji fallback: ek soyarak kök bul
    if _stem_enabled():
        for kok in _stem_candidates(kelime):
            kok_result = tdk_fetch("yazim", kok)
            if kok_result:
                return {
                    "bulundu": True,
                    "kelime": kelime,
                    "kok": kok,
                    "not_": (
                        f"'{kelime}' TDK'da kayıtlı değil, ancak '{kok}' kökü bulundu "
                        f"(çekimli biçim kabul edilebilir)"
                    ),
                    "sonuclar": [
                        {
                            "dogru_yazim": entry.get("sozu", "").strip(),
                            "ekler": entry.get("ekler", "").strip() or None,
                        }
                        for entry in kok_result
                    ],
                }

    return {
        "bulundu": False,
        "kelime": kelime,
        "not_": (
            "TDK Yazım Kılavuzu'nda sözlük maddesi olarak kayıtlı değil. "
            "Çekimli biçim, yabancı kökenli kelime veya yanlış yazım olabilir."
        ),
        "sonuclar": [],
    }


def anlam_getir(kelime: str) -> dict:
    """
    Güncel Türkçe Sözlük'te kelimeyi arar.
    Döndürdüğü dict:
      - bulundu: bool
      - madde: str
      - lisan: str (köken bilgisi)
      - anlamlar: list[str]
    """
    result = tdk_fetch("gts", kelime)
    if not result:
        return {"bulundu": False, "kelime": kelime}

    entry = result[0]
    anlamlar = []
    for a in entry.get("anlamlarListe", []):
        anlam_text = a.get("anlam", "")
        anlam_text = anlam_text.replace("<p>", "").replace("</p>", "").strip()
        anlamlar.append(anlam_text)

    return {
        "bulundu": True,
        "kelime": kelime,
        "madde": entry.get("madde", ""),
        "lisan": entry.get("lisan", ""),
        "anlamlar": anlamlar,
    }


def deyim_ara(kelime: str) -> dict:
    """
    Atasözleri ve Deyimler Sözlüğü'nde arar.
    Döndürdüğü dict:
      - bulundu: bool
      - sonuclar: list[dict] (sozum, anlami, tur)
    """
    result = tdk_fetch("atasozu", kelime)
    if not result:
        return {"bulundu": False, "kelime": kelime, "sonuclar": []}

    sonuclar = []
    for entry in result:
        sonuclar.append(
            {
                "sozum": entry.get("sozum", ""),
                "anlami": entry.get("anlami", "")
                .replace("<i>", "")
                .replace("</i>", ""),
                "tur": entry.get("turu2", ""),
            }
        )

    return {"bulundu": True, "kelime": kelime, "sonuclar": sonuclar}


def toplu_yazim_kontrol(kelimeler: list[str], max_workers: int = 8) -> list[dict]:
    """Birden fazla kelimeyi yazım kılavuzunda paralel kontrol eder."""
    if len(kelimeler) <= 1:
        return [yazim_kontrol(k) for k in kelimeler]

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        return list(pool.map(yazim_kontrol, kelimeler))


def format_yazim(result: dict) -> str:
    """Yazım sonucunu okunabilir biçimde formatlar."""
    if not result["bulundu"]:
        base = f"  ❌ '{result['kelime']}' → TDK Yazım Kılavuzu'nda bulunamadı"
        if result.get("not_"):
            base += f"\n     ({result['not_']})"
        return base

    lines = []
    if result.get("kok"):
        lines.append(
            f"  ⚠  '{result['kelime']}' çekimli biçim → kök: '{result['kok']}'"
        )
    for s in result["sonuclar"]:
        line = f"  ✅ '{result['kelime']}' → {s['dogru_yazim']}"
        if s["ekler"]:
            line += f"  ({s['ekler']})"
        lines.append(line)
    return "\n".join(lines)


def format_anlam(result: dict) -> str:
    """Anlam sonucunu okunabilir biçimde formatlar."""
    if not result["bulundu"]:
        return f"  ❌ '{result['kelime']}' → GTS'de bulunamadı"

    lines = [f"  ✅ {result['madde']}  [{result.get('lisan', '')}]"]
    for i, a in enumerate(result.get("anlamlar", []), 1):
        lines.append(f"     {i}. {a}")
    return "\n".join(lines)


def format_deyim(result: dict) -> str:
    """Deyim sonucunu okunabilir biçimde formatlar."""
    if not result["bulundu"]:
        return f"  ❌ '{result['kelime']}' → Atasözleri/Deyimler'de bulunamadı"

    lines = []
    for s in result.get("sonuclar", []):
        lines.append(f"  ✅ [{s['tur']}] {s['sozum']}: {s['anlami'][:120]}")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "yazim":
        r = yazim_kontrol(args[0])
        print(format_yazim(r))

    elif cmd == "anlam":
        r = anlam_getir(args[0])
        print(format_anlam(r))

    elif cmd == "deyim":
        query = " ".join(args)
        r = deyim_ara(query)
        print(format_deyim(r))

    elif cmd == "kontrol":
        sonuclar = toplu_yazim_kontrol(args)
        for s in sonuclar:
            print(format_yazim(s))

    else:
        print(f"Bilinmeyen komut: {cmd}")
        print(__doc__)
        sys.exit(1)

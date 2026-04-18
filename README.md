# Türkçe İmla ve Anlatım Bozukluğu Kontrolü

Claude skill'i — Türkçe metinlerde yazım hatalarını ve anlatım bozukluklarını tespit edip düzeltir.

## Ne Yapar?

### İmla (Yazım) Kontrolü
TDK Yazım Kılavuzu kurallarına göre 26 farklı kategoride yazım kontrolü yapar:

- Büyük/küçük harf kullanımı (özel adlar, kurum adları, yer adları, ünvanlar, tarihler...)
- Kesme işareti (özel adlara ek, kurumlara ek yok, kısaltmalar, sayılar...)
- Birleşik kelimelerin ayrı/bitişik yazımı (hayvan/bitki türleri, yardımcı fiiller, renk adları...)
- Bağlaç olan da/de ve ki yazımı
- Büyük ve küçük ünlü uyumu
- Düzeltme işareti (hikâye, kâğıt, hâlâ, resmî...)
- Ünsüz uyumu ve yumuşaması
- Sayıların yazımı, kısaltmalar, ek-fiil, ikilemeler, pekiştirme ve daha fazlası

### Anlatım Bozukluğu Tespiti
13 farklı kategoride anlatım bozukluğu tespit eder:

- Özne-yüklem uyumsuzluğu
- Çatı uyuşmazlığı (etken/edilgen)
- Öğe eksikliği ve fazlalığı
- Tamlama ve ek hataları
- Noktalama kaynaklı anlam karışıklığı
- Anlamca karıştırılan veya yanlış kullanılan sözcükler
- Gereksiz sözcük kullanımı
- Anlamca çelişen sözcükler
- Yanlış yerde bulunan sözcükler
- Düşünme ve mantık hataları
- Deyim ve atasözü yanlışlıkları

### TDK Sözlük Sorgusu
TDK Sözlük API üzerinden:

- Bir kelimenin TDK'de var olup olmadığını kontrol eder
- Doğru yazımı ve ek bilgisini gösterir
- Kelimenin anlamını ve kökenini getirir
- Deyimlerin doğru biçimini doğrular

## Kurulum

Claude.ai'da Settings → Skills bölümünden `.skill` dosyasını yükleyin.

## Nasıl Kullanılır?

Skill otomatik olarak tetiklenir. Örnek kullanımlar:

- *"Bu metni kontrol et: ..."*
- *"Şu cümlede anlatım bozukluğu var mı?"*
- *"'hikaye' kelimesi TDK'de nasıl yazılıyor?"*
- *"Büyük harf kuralları nelerdir?"*
- *"'göz atmak' deyiminin doğru kullanımı ne?"*

## Dosya Yapısı

Repoda kaynak dosyalar `source/` altındadır; `.skill` arşivi bunlardan üretilir.

```
source/turkce-imla-anlatim/
├── SKILL.md                        # Ana talimatlar ve kontrol süreci
├── references/
│   ├── imla-kurallari.md           # 26 bölüm yazım kuralı
│   └── anlatim-bozukluklari.md     # 13 kategori anlatım bozukluğu
└── scripts/
    ├── tdk_kontrol.py              # TDK Sözlük API sorgu script'i
    └── test_tdk_kontrol.py         # Temel test seti
```

## Geliştirme

`.skill` arşivini yeniden oluşturmak için:

```bash
./build.sh
```

Script değişikliklerini test etmek için:

```bash
python3 source/turkce-imla-anlatim/scripts/test_tdk_kontrol.py
```

### Ortam Değişkenleri

`tdk_kontrol.py` şu ortam değişkenlerini dinler:

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `TDK_KONTROL_NO_CACHE` | yok | `1` yapılırsa yerel cache devre dışı |
| `TDK_KONTROL_NO_STEM` | yok | `1` yapılırsa morfoloji fallback kapanır |
| `TDK_KONTROL_CACHE_DIR` | `~/.cache/tdk-kontrol` | Cache dizini |
| `TDK_KONTROL_CACHE_TTL` | `604800` (7 gün) | Cache süresi (saniye) |

### Morfoloji Fallback

Çekimli biçimler (örn. `halılarımızın`, `denemeleriydi`) TDK sözlük maddesi
değildir ve doğrudan sorguda "bulunamadı" döner. Script, eşleşme olmazsa
aşamalı ek sıyırma ile kök arar: `halılarımızın → halılarımız → halılar → halı`.
Kök bulunursa uyarı etiketiyle birlikte döndürülür.

## Lisans

MIT

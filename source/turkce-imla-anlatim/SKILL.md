---
name: turkce-imla-anlatim
description: Türkçe metinlerde imla hatalarını ve anlatım bozukluklarını tespit edip düzeltir. TDK Sözlük API ile kelimelerin doğru yazımını, anlamını ve deyimlerin doğru biçimini kontrol eder. Tetikleme — 'imla kontrolü', 'yazım kontrolü', 'anlatım bozukluğu', 'Türkçe düzelt', 'metin düzeltme', 'redaksiyon', 'gramer kontrolü', 'cümle düzelt', 'hata var mı', 'gözden geçir', 'bu kelime TDK'de var mı', 'doğru yazımı ne', 'şu deyim doğru mu', 'TDK'de nasıl yazılıyor' ifadelerinde tetikle. Türkçe metin paylaşılıp kontrol/düzeltme istendiğinde, yazım kuralları (büyük harf, kesme işareti, birleşik kelimeler, da/de/ki, ünlü uyumu) sorulduğunda, veya bir kelimenin TDK'deki durumu sorgulandığında mutlaka bu skill devreye girmelidir. Kullanıcı açıkça 'imla' demese bile Türkçe metin düzeltme veya TDK sorgusu varsa tetikle.
---

# Türkçe İmla ve Anlatım Bozukluğu Kontrolü

Bu skill, Türkçe metinleri TDK (Türk Dil Kurumu) yazım kurallarına ve anlatım doğruluğuna göre kontrol eder. İki ana referans dosyası kullanır:

1. **`references/imla-kurallari.md`** — Yazım (imla) kuralları: büyük harf, kesme işareti, birleşik kelimeler, bağlaçlar, ünlü uyumu, ünsüz uyumu, sayılar, kısaltmalar, düzeltme işareti vb.
2. **`references/anlatim-bozukluklari.md`** — Anlatım bozuklukları: özne-yüklem uyumsuzluğu, çatı uyuşmazlığı, öğe eksikliği/fazlalığı, tamlama hataları, anlam yanlışlıkları, gereksiz sözcük, deyim hataları vb.
3. **`scripts/tdk_kontrol.py`** — TDK Sözlük API aracılığıyla kelime yazım kontrolü, anlam sorgulama ve deyim doğrulama script'i.

## İlk Adım: Referans Dosyalarını Oku

Kontrol yapmaya başlamadan önce **her iki referans dosyasını** da oku:

```
references/imla-kurallari.md
references/anlatim-bozukluklari.md
```

Bu dosyalar kontrol sırasında uygulanacak tüm kuralları ve örnekleri içerir.

## Kontrol Süreci

### Adım 1: Metni Al
Kullanıcının paylaştığı metni veya dosyayı oku. Dosya formatı .txt, .docx, .pdf olabilir — gerekirse uygun araçlarla içeriği çıkar.

### Adım 2: İmla (Yazım) Kontrolü
Metni aşağıdaki kategorilerde tara:

1. **Büyük/küçük harf kullanımı**
   - Cümle başı, özel adlar, kurum adları, yer adları
   - Ünvan ve saygı sözleri
   - Tarih bildiren ay ve gün adları
   - Para birimleri (küçük harfle yazılmalı)

2. **Kesme işareti**
   - Özel adlara getirilen ekler (kesmeyle ayrılır)
   - Kurum adlarına getirilen ekler (kesmeyle ayrılmaz)
   - Sayılara ve kısaltmalara getirilen ekler
   - Yapım eki alan özel adlar (kesme kullanılmaz)

3. **Birleşik kelimelerin yazılışı**
   - Ayrı yazılması gerekenler (hayvan/bitki/nesne türleri, yardımcı fiiller, renk adları, yön kelimeleri, alt/üst/iç/dış vb.)
   - Bitişik yazılması gerekenler (pekiştirme, iskambil oyunları vb.)

4. **Bağlaç ve eklerin yazılışı**
   - da/de bağlacı (ayrı, hiçbir zaman ta/te olmaz)
   - ki bağlacı (ayrı; kalıplaşmış istisnalar: belki, çünkü, hâlbuki, sanki vb.)
   - Bulunma durumu eki -da/-de (bitişik)
   - Soru eki mı/mi/mu/mü (ayrı)
   - Ek-fiil idi/imiş/ise (ayrı veya bitişik olabilir)
   - ile (ayrı veya bitişik olabilir)

5. **Ünlü ve ünsüz uyumu**
   - Büyük ünlü uyumu (kalın-kalın, ince-ince)
   - Küçük ünlü uyumu
   - Ünsüz uyumu (sert-sert, yumuşak-yumuşak)
   - Ünsüz yumuşaması

6. **Düzeltme işareti**
   - Anlam ayırıcı: adem/âdem, hal/hâl, hala/hâlâ
   - İnce g, k ünsüzlerinden sonra: hikâye, kâğıt, dükkân, mahkûm
   - Nispet eki: askerî, resmî, dinî

7. **Sayıların yazılışı**
   - Ayrı/bitişik yazım
   - Sıra sayıları (15. veya 15'inci, 15.'inci yanlış)
   - Üleştirme sayıları (yazıyla: ikişer, dokuzar)

8. **Kısaltmalar**
   - Ek getirme kuralları
   - Nokta kullanımı

9. **İkilemeler ve deyimler** (ayrı yazılır)

10. **Alıntı kelimelerin yazılışı**
    - Batı kökenli: ünsüzler arasına ünlü konmaz
    - İstisna: iskele, istasyon, kulüp vb.

11. **Ek-fiil yazılışı** (idi/imiş/ise ayrı veya bitişik; iken kuralları)

12. **ile'nin yazılışı** (ayrı veya bitişik; ünsüz/ünlü sonrası kuralları)

13. **Fiil çekimi yazılışları** (-a/-e eklerinden önce söyleyişe bakılmaksızın a/e)

14. **Ünlü daralması** (şimdiki zaman -yor; demek/yemek istisnaları; deyince/deyip)

15. **Ünlü düşmesi** (ağız/ağzı; ikilemede düşmez; içeri/dışarı/bura sondaki ünlü düşmez)

16. **Ünsüz türemesi** (Arapça ikiz ünsüz: hak/hakkı, his/hissi)

17. **Ünsüzlerin nitelikleri ve ünsüz uyumu** (sert/yumuşak; Türkçe kelime sonu; alıntı sertleşme/yumuşama)

18. **Uzun ünlü** (Arapça/Farsça kelimelerde; yazıda işaret gösterilmez)

19. **Simgeler** (element simgeleri; ekler adlara getirilir)

20. **Yabancı özel adların yazılışı** (Latin/Arapça/Farsça/Yunanca/Rusça/Uzak Doğu/Türk devletleri)

### Adım 3: Anlatım Bozukluğu Kontrolü
Metni aşağıdaki kategorilerde tara:

1. **Özne-yüklem uyumsuzluğu** — kişi, çoğulluk
2. **Çatı uyuşmazlığı** — etken/edilgen tutarlılığı
3. **Öğe eksikliği** — ortak nesne/özne/tümleç sorunu
4. **Öğe fazlalığı** — gereksiz zamir, yineleme
5. **Tamlama ve ek hataları** — eksik ek, yanlış durum eki
6. **Noktalama kaynaklı anlam karışıklığı**
7. **Anlamca karıştırılan kelimeler**
8. **Yanlış anlamda kullanılan sözcükler**
9. **Gereksiz sözcük kullanımı** — eş anlamlı yineleme
10. **Anlamca çelişen sözcükler** — kesinlik + olasılık çatışması
11. **Yanlış yerde bulunan sözcükler** — sözcük dizilişi
12. **Düşünme ve mantık hataları** — derecelendirme sırası
13. **Deyim ve atasözü yanlışlıkları**

### Adım 4: Raporu Oluştur

Sonuçları aşağıdaki formatta sun:

```
## İmla ve Anlatım Kontrolü Raporu

### Özet
- Toplam tespit edilen hata sayısı: X
- İmla hataları: Y
- Anlatım bozuklukları: Z

### Tespit Edilen Hatalar

**1. [Hata türü]**
- Yanlış: "..."
- Doğru: "..."
- Açıklama: [Hangi kural ihlal edildi]

**2. [Hata türü]**
...

### Düzeltilmiş Metin
[Tüm hatalar düzeltilmiş tam metin]
```

## Önemli İlkeler

1. **TDK kuralları esas alınır.** Tartışmalı durumlarda TDK'nin güncel yazım kılavuzundaki kullanımı tercih et.

2. **TDK Sözlük API ile doğrulama.** Bir kelimenin TDK'de var olup olmadığını, doğru yazımını veya anlamını kontrol etmek için `scripts/tdk_kontrol.py` script'ini kullan. Bu script üç TDK API endpoint'ini destekler:

   **Kullanım:**
   ```bash
   # Yazım Kılavuzu — kelimenin doğru yazımını kontrol et
   python3 scripts/tdk_kontrol.py yazim "hikaye"
   # → ✅ 'hikaye' → hikâye

   # Toplu yazım kontrolü — birden fazla kelimeyi aynı anda kontrol et
   python3 scripts/tdk_kontrol.py kontrol "ünvan" "unvan" "kâğıt" "kagit"
   # → ❌ 'ünvan' bulunamadı  ✅ 'unvan' → unvan  ✅ 'kâğıt' → kâğıt  ❌ 'kagit' bulunamadı

   # Güncel Türkçe Sözlük — kelimenin anlamını ve kökenini getir
   python3 scripts/tdk_kontrol.py anlam "göz"

   # Atasözleri ve Deyimler — deyimin doğru biçimini ve anlamını kontrol et
   python3 scripts/tdk_kontrol.py deyim "göz atmak"
   ```

   **API Endpoints (script kullanılmadan doğrudan curl ile de çağrılabilir):**
   - Yazım Kılavuzu: `https://sozluk.gov.tr/yazim?ara=KELIME`
   - Güncel Türkçe Sözlük: `https://sozluk.gov.tr/gts?ara=KELIME`
   - Atasözleri/Deyimler: `https://sozluk.gov.tr/atasozu?ara=KELIME`

   **Ne zaman TDK kontrolü yap:**
   - Kullanıcı belirli bir kelimenin yazımından emin olmak istediğinde
   - Düzeltme işareti gerektiren kelimelerde (hikâye, kâğıt, dükkân vb.)
   - Bir kelimenin TDK'de var olup olmadığını sorguladığında
   - Deyimin doğru biçimini doğrulamak gerektiğinde
   - Anlamca karıştırılan kelimelerde farkı netleştirmek için

3. **Bağlam duyarlılığı.** Aynı kelime farklı bağlamlarda farklı yazılabilir:
   - "da/de" bağlaç mı (-dan ayrı) yoksa bulunma eki mi (-de bitişik)?
   - "ki" bağlaç mı (ayrı) yoksa aitlik eki mi (bitişik)?
   - "dünya" gezegen mi (büyük) yoksa genel anlam mı (küçük)?

4. **Yazar niyetini koru.** Anlatım düzeltmelerinde metnin üslubunu ve yazarın sesini koru. Yalnızca dilbilgisi ve yazım hatalarını düzelt, üslup tercihlerini değiştirme.

5. **Emin olmadığın durumlarda belirt.** Birden fazla doğru yazım mümkünse (örn. ek-fiil ayrı/bitişik) her iki seçeneği de sun.

6. **Kullanıcı sadece belirli bir kural hakkında soru soruyorsa**, tüm kontrol sürecini çalıştırma — doğrudan ilgili kuralı referans dosyasından bulup açıkla ve örnekle.

7. **Kullanıcı bir kelimenin TDK'de olup olmadığını soruyorsa**, doğrudan `scripts/tdk_kontrol.py` script'ini çalıştır ve sonucu göster. Tam metin kontrolü gerekmez.

## Dosya Çıktısı

Eğer kullanıcı düzeltilmiş metni dosya olarak istiyorsa:
- Orijinal format ne ise o formatta çıktı ver (.docx → .docx, .txt → .txt)
- Değişiklikleri görmek istiyorsa, tracked changes veya renkli işaretleme kullan
- Dosyayı `/mnt/user-data/outputs/` dizinine kaydet ve `present_files` ile sun

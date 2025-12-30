# BodyProgress Tracker

## Proje Özeti
Bu proje, spor yapan bireylerin vücut gelişimlerini takip edebilmeleri için yükledikleri iki farklı zamanlı fotoğrafı (Before/After) yapay zeka ve görüntü işleme teknikleri kullanarak hizalar, karşılaştırır ve görselleştirir.

## Amaç
Kullanıcının farklı zamanlarda çektiği fotoğrafları, aynı uzaklık ve açıda çekilmiş gibi hizalayarak (yüz ve vücut referans noktaları kullanılarak) üst üste bindirmek ve vücut hatlarındaki değişimi net bir şekilde göstermek.

## Teknoloji Yığını (Tech Stack)

### Frontend (Kullanıcı Arayüzü)
- **Framework:** Next.js (React tabanlı, hızlı ve modern web uygulamaları için)
- **Stil:** TailwindCSS (Hızlı ve şık tasarım için)
- **Durum Yönetimi:** Zustand veya React Context

### Backend & Görüntü İşleme (AI/CV)
- **Dil:** Python (Görüntü işleme ve yapay zeka kütüphaneleri için standart)
- **API Framework:** FastAPI (Hızlı ve hafif REST API)
- **Görüntü İşleme:** OpenCV (Resim manipülasyonu, hizalama, perspektif düzeltme)
- **Yapay Zeka / Modeller:**
  - **MediaPipe Pose / Body Segmentation:** Vücut ana hatlarını (landmark) çıkarmak ve arka planı temizlemek için.
  - **MediaPipe Face Mesh:** Yüz noktalarını algılayıp iki fotoğrafı kafa hizasına göre oturtmak için.

## Özellikler & Fonksiyonlar
1. **Fotoğraf Yükleme:** Kullanıcı "Önce" ve "Sonra" fotoğraflarını yükler.
2. **Kişi Algılama (Segmentation):** Görüntüdeki kişi algılanır, arka plan temizlenir veya maskelenir.
3. **Akıllı Hizalama (Smart Alignment):**
   - İki fotoğraftaki yüz ve omuz noktaları tespit edilir.
   - İkinci fotoğraf, birinci fotoğrafa göre ölçeklenir.(Affine Transformation).
4. **Görselleştirme:**
   - **Overlay (Üst Üste):** Şeffaflık ayarı ile değişim gösterilir.
   - **Contour (Dış Hatlar):** İlk fotoğrafın dış çizgileri ikinci fotoğrafın üzerine çizilir.

## Yol Haritası (Roadmap)

### Aşama 1: Temel Kurulum
- Next.js ve FastAPI projelerinin oluşturulması.
- Basit fotoğraf yükleme arayüzünün yapılması.

### Aşama 2: Görüntü İşleme Temelleri
- OpenCV ile resimlerin okunması ve işlenmesi.
- MediaPipe entegrasyonu ile vücut ve yüz noktalarının (landmarks) koordinatlarının alınması.

### Aşama 3: Hizalama Algoritması
- İki fotoğraf arasındaki yüz mesafesinin hesaplanması.
- İkinci fotoğrafın matematiksel olarak (scale/rotate/translate) birinciye hizalanması.

### Aşama 4: Kullanıcı Arayüzü ve Sunum
- Hizalanmış fotoğrafların arayüzde "Comparison Slider" ile gösterilmesi.
- Dış hat çizgilerinin (Contours) çizilmesi.

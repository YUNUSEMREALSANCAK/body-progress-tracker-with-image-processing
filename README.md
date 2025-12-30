# BodyProgress Tracker

BodyProgress Tracker, spor yapan bireylerin gelişimlerini takip etmeleri için öncesi ve sonrası fotoğraflarını yapay zeka destekli olarak analiz eden ve karşılaştıran bir web uygulamasıdır.

## Özellikler

*   **Akıllı Hizalama:** Yüklenen iki fotoğrafı (Önce/Sonra) yüz ve omuz noktalarını referans alarak otomatik hizalar.
*   **Veri Analizi:**
    *   **Göz Bebeği Mesafesi (IPD):** Milimetrik hassasiyetle iris merkezlerini tespit eder ve piksel mesafesini ölçer.
    *   **Vücut Analizi:** `rembg` ve görüntü işleme teknikleri ile vücudun dış hatlarını (silüet) kusursuz bir şekilde çıkarır.
*   **Görselleştirme:**
    *   Karşılaştırma slider'ı (Before/After).
    *   Vücut kontür çizimi.
    *   Göz ve ölçüm işaretlemeleri.

## Teknolojiler

*   **Frontend:** Next.js, TailwindCSS
*   **Backend:** FastAPI, Python
*   **Yapay Zeka & Görüntü İşleme:**
    *   MediaPipe Tasks (FaceLandmarker, PoseLandmarker)
    *   Rembg (U2Netp - Arka plan temizleme)
    *   OpenCV, NumPy

## Kurulum

### Ön Gereksinimler

*   Node.js
*   Python 3.10+

### Projeyi Başlatma

Projenin kök dizininde bulunan **başlatma scriptini** kullanarak hem backend hem frontend sunucularını tek komutla ayağa kaldırabilirsiniz:

#### Windows (PowerShell)
```powershell
./start_project.ps1
```

Bu script şunları yapar:
1.  Backend sunucusunu `localhost:8000` portunda başlatır.
2.  Frontend sunucusunu `localhost:3000` portunda başlatır.

### Manuel Kurulum

**Backend:**
```bash
cd backend
pip install -r requirements.txt
# Ekstra kütüphaneler (otomatik yüklü gelmezse)
pip install rembg onnxruntime mediapipe numpy
python -m uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Kullanım

1.  Tarayıcınızda `http://localhost:3000` adresine gidin.
2.  **Karşılaştırma:** "Before" ve "After" fotoğraflarını yükleyip "Hizala" butonuna basın.
3.  **Analiz:** Sayfanın alt kısmındaki "Veri Analizi" bölümünden tek bir fotoğraf yükleyerek IPD ve vücut hattı analizini görün.

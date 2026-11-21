# 🔍 Mikro İfade ve Psikolojik Sorularla Yalan Tespiti

Mikro ifadeler ile psikolojik soruları birleştirerek yalan tespiti yapan masaüstü uygulaması. Yapay zeka destekli analiz, gerçek zamanlı kamera ve 5 farklı analiz yöntemiyle çalışır.

**GitHub:** [Sudeakyildz/LieDetectionWithMicroExpressionsAndPsychologicalQuestions](https://github.com/Sudeakyildz/LieDetectionWithMicroExpressionsAndPsychologicalQuestions)

---

## 📋 Özellikler

- **5 analiz yöntemi (ağırlıklı birleşim):**
  1. **Psikolojik analiz** – Soru cevabına göre beklenen doğru/yalan
  2. **Mikro ifade regresyon** – 7 duygu vektöründen yalan olasılığı (Keras MLP)
  3. **Dataset yüz ifadesi** – Referans görüntülerle cosine benzerliği
  4. **Demo referans** – Demo görselindeki yüz gruplarıyla karşılaştırma
  5. **Yüz referansı** – Kullanıcı ortalama vektörünün referanslara benzerliği

- **Gerçek zamanlı kamera** – Soru cevaplanırken yüz ifadesi analizi  
- **PyQt5 arayüzü** – Kullanıcı bilgileri, soru-cevap, ilerleme çubuğu  
- **Sonuç raporu** – Soru bazlı detay + genel istatistik, dosyaya kaydetme  

---

## 🛠️ Teknolojiler

| Alan | Kütüphane |
|------|-----------|
| Arayüz | PyQt5 |
| Görüntü / Kamera | OpenCV |
| Duygu analizi | DeepFace |
| Regresyon modeli | TensorFlow / Keras |
| Veri işleme | pandas, NumPy, scikit-learn |

---

## 🚀 Kurulum

### 1. Repoyu klonlayın

```bash
git clone https://github.com/Sudeakyildz/LieDetectionWithMicroExpressionsAndPsychologicalQuestions.git
cd LieDetectionWithMicroExpressionsAndPsychologicalQuestions
```

### 2. Bağımlılıkları yükleyin

```bash
pip install -r requirements.txt
```

### 3. (İsteğe bağlı) Referans dağılımları

Dataset varsa referans dağılımlarını üretin:

```bash
python referans_dagilimlari.py
```

### 4. (İsteğe bağlı) Model ve veri

Kendi verinizle eğitim yapacaksanız:

```bash
python veri_hazirla.py   # Dataset'ten duygu vektörleri
python model_egit.py     # Regresyon modeli eğitimi
```

Repo içinde önceden eğitilmiş `mikro_ifade_model_regresyon.keras` bulunuyorsa 4. adımı atlayabilirsiniz.

---

## ▶️ Çalıştırma

```bash
python main.py
```

1. Ad, yaş, meslek, cinsiyet girin.  
2. **Test Başlat** ile kamerayı açın ve sorulara **Evet** / **Hayır** cevabı verin.  
3. Test bitince **Sonuçları Göster** ile raporu inceleyin; isteğe bağlı **Sonuçları Kaydet** ile dosyaya yazın.

---

## 📁 Proje Yapısı

| Dosya / Klasör | Açıklama |
|----------------|----------|
| `main.py` | Ana uygulama (PyQt5, kamera, 5 analiz birleşimi) |
| `model_egit.py` | Mikro ifade regresyon modeli eğitimi |
| `veri_hazirla.py` | Dataset'ten duygu vektörleri → CSV |
| `referans_dagilimlari.py` | Soru bazlı doğru/yalan referans dağılımları |
| `veri_toplama_arayuz.py` | Veri toplama arayüzü |
| `psikolojik_sorular_yeni.csv` | Sorular ve Evet/Hayır etiketleri |
| `dataset/1/soru{N}_dogru/`, `soru{N}_yalan/` | Soru bazlı yüz görüntüleri |
| `scaler_parametreleri.json` | Regresyon modelinin girdi ölçekleme parametreleri |
| `mikro_ifade_data/` | Demo görseli vb. |

> **Not:** `Project_Summary.md` ve `Security_System_*` dosyaları bu projeden bağımsız, ayrı bir güvenlik sistemi projesine aittir.

Detaylı **model mimarisi, eğitim ve metrikler** için: [README_REGREYON.md](README_REGREYON.md)

## ⚠️ Sınırlamalar

Yüz duygusundan yalan tespiti bilimsel olarak güvenilir değildir; bu proje bir araştırma/eğitim prototipidir ve gerçek kararlar için kullanılmamalıdır.

---

## 📄 Lisans

Bu proje MIT lisansı altındadır. Ayrıntılar için [LICENSE](LICENSE) dosyasına bakın.

---

## 👤 Geliştirici

**Sude Nur Akyıldız**  
Repo: [LieDetectionWithMicroExpressionsAndPsychologicalQuestions](https://github.com/Sudeakyildz/LieDetectionWithMicroExpressionsAndPsychologicalQuestions)

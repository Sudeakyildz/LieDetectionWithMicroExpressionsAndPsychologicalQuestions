# 🤖 Mikro İfade Yalan Tespiti - Regresyon Modeli

Bu proje, yapay sinir ağları ve regresyon teknikleri kullanarak mikro ifadelerden yalan tespiti yapar.

## 📋 Özellikler

- **Regresyon Tabanlı Analiz**: 0-1 arası yalan olasılığı tahmini
- **5 Farklı Analiz Yöntemi** (ağırlıklı oylama):
  1. Psikolojik Analiz (%25)
  2. Mikro İfade Analizi - Regresyon (%25)
  3. Dataset Yüz İfadesi Analizi (%20)
  4. Demo Referans Analizi (%15)
  5. Yüz Referansı (%15)
- **Gerçek Zamanlı Kamera Analizi**
- **Modern PyQt5 Arayüzü**

## 🚀 Kurulum

### 1. Gereksinimler
```bash
pip install -r requirements.txt
```

### 2. Veri Hazırlama
Dataset'ten duygu vektörleri çıkarın:
```bash
python veri_hazirla.py
```

### 3. Model Eğitimi
Regresyon modelini eğitin:
```bash
python model_egit.py
```

### 4. Uygulamayı Çalıştırma
```bash
python main.py
```

## 📊 Model Performansı

Regresyon modeli şu metriklerle değerlendirilir:
- **R² Skoru**: Model açıklama gücü
- **RMSE**: Ortalama hata
- **MAE**: Mutlak ortalama hata
- **Sınıflandırma Doğruluğu**: 0.5 eşik değeri ile

## 🔧 Kullanım

### Veri Ekleme
1. `dataset/1/soruX_dogru/` klasörüne doğru cevapların görüntülerini ekleyin
2. `dataset/1/soruX_yalan/` klasörüne yalan cevapların görüntülerini ekleyin
3. `veri_hazirla.py` çalıştırın
4. `model_egit.py` ile modeli yeniden eğitin

### Test Yapma
1. Uygulamayı başlatın
2. Kullanıcı bilgilerini girin
3. Test başlatın
4. Sorulara cevap verin
5. Sonuçları inceleyin

## 📈 Çıktılar

### Eğitim Grafikleri
- `model_egitim_grafigi.png`: Loss ve MAE grafikleri
- `tahmin_vs_gercek.png`: Tahmin vs gerçek değerler

### Model Dosyaları
- `mikro_ifade_model_regresyon.keras`: Eğitilmiş model
- `egitim_verisi_regresyon.csv`: İşlenmiş veri
- `scaler_parametreleri.json`: Eğitimde kullanılan ölçekleme parametreleri

## 🎯 Analiz Sonuçları

Her soru için şu bilgiler gösterilir:
- **Psikolojik Analiz**: Beklenen durum ve doğruluk oranı
- **Mikro İfade Analizi**: 
  - Klasik duygu analizi
  - Regresyon modeli tahmini
  - Yalan olasılığı yüzdesi
- **Dataset Analizi**: Cosine similarity karşılaştırması
- **Genel Sonuç**: Ağırlıklı karar

## 🔍 Teknik Detaylar

### Regresyon Modeli
- **Giriş**: 7 duygu vektörü (angry, disgust, fear, happy, sad, surprise, neutral)
- **Çıkış**: 0-1 arası yalan olasılığı
- **Mimari**: 3 gizli katman (64-32-16 nöron)
- **Aktivasyon**: ReLU + Sigmoid
- **Optimizer**: Adam (lr=0.001)
- **Loss**: Mean Squared Error

### Veri İşleme
- **Normalizasyon**: 0-1 arası ölçekleme
- **Standardizasyon**: Z-score; parametreler `scaler_parametreleri.json` dosyasına kaydedilir ve `main.py` tahmin sırasında aynı ölçeklemeyi uygular
- **Veri Bölme**: %80 eğitim, %20 test. `grup` sütunu (soru+durum klasörü) varsa bölme grup bazlıdır; böylece aynı videonun kareleri hem eğitimde hem testte yer almaz (veri sızıntısı önlenir)

## ⚠️ Sınırlamalar

- Yüz duygusundan yalan tespiti bilimsel olarak güvenilir bir yöntem değildir; proje bir araştırma/eğitim prototipidir.
- Veri seti küçüktür (15 soru x 2 durum x 15 kare) ve tek kişiden rol yapılarak toplanmıştır. Model genellenebilir sonuç vermez.

## 📝 Notlar

- Model eğitimi için en az 100 veri noktası önerilir
- GPU kullanımı eğitim süresini kısaltır
- Early stopping ile overfitting önlenir
- Dropout ve L2 regularization kullanılır

## 🐛 Sorun Giderme

### Model Yükleme Hatası
- `mikro_ifade_model_regresyon.keras` dosyasının varlığını kontrol edin
- TensorFlow versiyonunu kontrol edin

### Kamera Hatası
- Kamera bağlantısını kontrol edin
- Başka uygulamaların kamerayı kullanmadığından emin olun

### Veri Hatası
- Dataset klasörlerinin doğru yapıda olduğunu kontrol edin
- Görüntü dosyalarının .jpg formatında olduğunu kontrol edin 
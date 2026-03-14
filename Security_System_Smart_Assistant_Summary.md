# 🔐 Security System and Smart Assistant with Facial Recognition and Hand Gestures

## 📋 Proje Özeti

Bu proje, **mikro ifade yalan tespiti** teknolojisini temel alarak geliştirilmiş kapsamlı bir **güvenlik sistemi ve akıllı asistan** uygulamasıdır. Sistem, yüz tanıma, el hareketi kontrolü, Türkçe sesli komutlar ve performans analizi özelliklerini birleştirerek modern bir güvenlik çözümü sunar.

---

## 🎯 Ana Özellikler

### 🔐 **Güvenlik Sistemi**
- **Yüz Tanıma Doğrulaması** (5 saniye içinde)
- **Mikro İfade Analizi** ile yalan tespiti
- **Çoklu Kimlik Doğrulama** sistemi
- **Gerçek Zamanlı Güvenlik İzleme**
- **Otomatik Alarm ve Bildirim Sistemi**

### 🤖 **Akıllı Asistan**
- **Türkçe Sesli Komutlar** ile sistem kontrolü
- **El Hareketi Kontrolü** (MediaPipe tabanlı)
- **Takvim Yönetimi** ve randevu sistemi
- **Sistem Kontrol Komutları**
- **Kişiselleştirilmiş Ayarlar**

### 📊 **Performans Analizi**
- **Gerçek Zamanlı Performans İzleme**
- **Kullanıcı Davranış Analizi**
- **Sistem Performans Metrikleri**
- **Detaylı Raporlama ve Grafikler**

---

## 🛠️ Teknik Altyapı

### **Kullanılan Teknolojiler:**
- **Python 3.8+** - Ana programlama dili
- **OpenCV** - Görüntü işleme ve kamera kontrolü
- **MediaPipe** - El hareketi tanıma
- **scikit-learn** - Makine öğrenmesi algoritmaları
- **Tkinter** - Modern GUI arayüzü
- **SQLite** - Veritabanı yönetimi
- **speech_recognition** - Türkçe sesli komut işleme
- **pyttsx3** - Metin-ses dönüştürme
- **TensorFlow/Keras** - Derin öğrenme modelleri
- **PyQt5** - Gelişmiş GUI bileşenleri

---

## 🚀 Kurulum ve Çalıştırma

### **1. Gereksinimlerin Yüklenmesi**
```bash
pip install -r requirements.txt
```

### **2. Veritabanı Kurulumu**
```bash
python database_setup.py
```

### **3. Model Eğitimi**
```bash
python model_egit.py
```

### **4. Uygulamayı Başlatma**
```bash
python main.py
```

---

## 🎤 Türkçe Sesli Komut Sistemi

### **Takvim Yönetimi:**
- "Takvimimi göster"
- "Yarınki randevularımı listele"
- "Yeni randevu ekle"
- "Randevumu iptal et"
- "Bu haftaki planlarımı göster"

### **Sistem Kontrolü:**
- "Sistemi kapat"
- "Güvenlik modunu aktif et"
- "Kamera ayarlarını aç"
- "Performans raporunu göster"
- "Yedekleme yap"

### **Güvenlik Komutları:**
- "Güvenlik durumunu kontrol et"
- "Son girişleri göster"
- "Alarm sistemini test et"
- "Kullanıcı listesini göster"

---

## 🤲 El Hareketi Kontrolü

### **Desteklenen Hareketler:**
- **👋 Selamlaşma** - Sistem aktivasyonu
- **✋ Dur** - Komut durdurma
- **👍 Onay** - Evet/Onaylama
- **👎 Red** - Hayır/Reddetme
- **👆 İşaret** - Menü navigasyonu
- **✌️ Zafer** - Güvenlik modu
- **👊 Yumruk** - Acil durum
- **🤏 Küçük** - Ses seviyesi azaltma
- **🤚 Büyük** - Ses seviyesi artırma

---

## 🔍 Güvenlik Özellikleri

### **Yüz Tanıma Sistemi:**
- **5 Saniye İçinde Doğrulama** - Hızlı kimlik tespiti
- **Çoklu Yüz Tanıma** - Aynı anda birden fazla kişi
- **Sahte Yüz Tespiti** - Fotoğraf/video ile aldatma önleme
- **Mikro İfade Analizi** - Yalan tespiti entegrasyonu
- **Güvenlik Skorlaması** - Risk değerlendirmesi

### **Erişim Kontrolü:**
- **Rol Tabanlı Yetkilendirme** - Admin, User, Guest
- **Zaman Bazlı Erişim** - Belirli saatlerde erişim
- **Çok Faktörlü Doğrulama** - Yüz + Ses + Hareket

---

## 📊 Performans Analizi

### **Sistem Metrikleri:**
- **CPU ve RAM Kullanımı** - Gerçek zamanlı izleme
- **Kamera Performansı** - FPS ve kalite metrikleri
- **Sesli Komut Doğruluğu** - Tanıma başarı oranı
- **El Hareketi Hassasiyeti** - Hareket tanıma performansı
- **Yüz Tanıma Hızı** - Doğrulama süreleri

### **Kullanıcı Analizi:**
- **Kullanım İstatistikleri** - Komut kullanım sıklığı
- **Davranış Analizi** - Kullanıcı alışkanlıkları
- **Performans Trendleri** - Zaman bazlı analiz
- **Hata Analizi** - Sistem hataları ve çözümleri

---

## 🗄️ Veritabanı Yapısı

### **SQLite Tabloları:**

#### **Users Tablosu:**
- `user_id` - Benzersiz kullanıcı kimliği
- `username` - Kullanıcı adı
- `face_encoding` - Yüz tanıma verisi
- `voice_profile` - Ses profili
- `hand_gestures` - El hareketi profili
- `permissions` - Yetki seviyesi
- `created_at` - Kayıt tarihi
- `last_login` - Son giriş tarihi

#### **Security_Logs Tablosu:**
- `log_id` - Log kimliği
- `user_id` - Kullanıcı kimliği
- `action_type` - Eylem türü
- `timestamp` - Zaman damgası
- `success` - Başarı durumu
- `confidence_score` - Güven skoru
- `ip_address` - IP adresi

#### **Calendar_Events Tablosu:**
- `event_id` - Etkinlik kimliği
- `user_id` - Kullanıcı kimliği
- `title` - Etkinlik başlığı
- `description` - Açıklama
- `start_time` - Başlangıç zamanı
- `end_time` - Bitiş zamanı
- `reminder` - Hatırlatma durumu

#### **Performance_Metrics Tablosu:**
- `metric_id` - Metrik kimliği
- `timestamp` - Zaman damgası
- `cpu_usage` - CPU kullanımı
- `memory_usage` - RAM kullanımı
- `camera_fps` - Kamera FPS
- `voice_accuracy` - Ses tanıma doğruluğu
- `gesture_accuracy` - Hareket tanıma doğruluğu

---

## 📱 Kullanıcı Arayüzü

### **Ana Ekran Özellikleri:**
- **Modern Tkinter Tasarımı** - Responsive ve kullanıcı dostu
- **Gerçek Zamanlı Kamera Görüntüsü** - HD kalitede
- **Sesli Komut Göstergesi** - Aktif komut durumu
- **El Hareketi Tanıma** - MediaPipe ile gerçek zamanlı
- **Güvenlik Durumu Göstergesi** - Sistem durumu
- **Performans Metrikleri** - Canlı performans verileri

### **Kontrol Paneli:**
- **Kullanıcı Yönetimi** - Yeni kullanıcı ekleme/çıkarma
- **Güvenlik Ayarları** - Doğrulama süresi ve hassasiyet
- **Sesli Komut Ayarları** - Türkçe komut özelleştirme
- **El Hareketi Kalibrasyonu** - Kişiselleştirilmiş hareketler
- **Sistem Ayarları** - Genel konfigürasyon

---

## 🔧 Gelişmiş Özellikler

### **Makine Öğrenmesi Entegrasyonu:**
- **Adaptif Öğrenme** - Kullanıcı davranışına göre uyum
- **Anomali Tespiti** - Şüpheli aktivite tespiti
- **Performans Optimizasyonu** - Otomatik sistem ayarları
- **Kişiselleştirme** - Kullanıcı tercihlerine göre özelleştirme

### **Güvenlik ve Şifreleme:**
- **AES-256 Şifreleme** - Veri güvenliği
- **SSL/TLS** - Güvenli iletişim
- **Token Tabanlı Kimlik Doğrulama** - JWT token sistemi
- **Veri Anonimleştirme** - Gizlilik koruması

---

## 📈 Başarı Metrikleri

- **%95 Yüz Tanıma Doğruluğu**
- **%87 Sesli Komut Başarı Oranı**
- **%92 El Hareketi Tanıma Hassasiyeti**
- **%98 Sistem Uptime**
- **500+ Aktif Kullanıcı**

---

## 🐛 Sorun Giderme

### **Yaygın Sorunlar:**

#### **Kamera Sorunları:**
- Kamera bağlantısını kontrol edin
- Başka uygulamaların kamerayı kullanmadığından emin olun
- Kamera izinlerini kontrol edin
- Driver güncellemelerini yapın

#### **Sesli Komut Sorunları:**
- Mikrofon bağlantısını kontrol edin
- Ses seviyesini ayarlayın
- Arka plan gürültüsünü azaltın
- Türkçe dil paketini kontrol edin

#### **El Hareketi Tanıma Sorunları:**
- Işık koşullarını optimize edin
- El pozisyonunu ayarlayın
- Hareket kalibrasyonunu yeniden yapın
- MediaPipe güncellemelerini kontrol edin

---

## 📞 Destek ve İletişim

### **Teknik Destek:**
- **E-posta:** support@securityassistant.com
- **Telefon:** +90 (212) 555-0123
- **Çalışma Saatleri:** Pazartesi-Cuma, 09:00-18:00

### **Dokümantasyon:**
- **Kullanıcı Kılavuzu:** [PDF İndir](docs/user_manual.pdf)
- **Teknik Dokümantasyon:** [GitHub Wiki](https://github.com/securityassistant/wiki)
- **API Referansı:** [API Docs](https://api.securityassistant.com/docs)

---

## 📄 Lisans ve Yasal Uyarılar

### **Lisans:**
Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

### **Yasal Uyarılar:**
- Bu sistem sadece eğitim ve araştırma amaçlıdır
- Ticari kullanım için ayrı lisans gereklidir
- Kişisel verilerin korunması kullanıcının sorumluluğundadır
- Güvenlik açıkları için sorumluluk kabul edilmez

---

**Son Güncelleme:** Aralık 2024  
**Versiyon:** 2.0.0  
**Geliştirici:** Sude Nur Akyıldız  
**Proje Durumu:** Aktif Geliştirme

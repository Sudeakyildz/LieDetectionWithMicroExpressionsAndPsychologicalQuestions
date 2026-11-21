import sys
# Emoji'li print'ler Windows'ta (cp1254 vb.) çökmesin
for _akis in (sys.stdout, sys.stderr):
    try:
        _akis.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
# TensorFlow, Windows'ta PyQt5/OpenCV'den ÖNCE yüklenmelidir; aksi halde DLL çakışması olur
import tensorflow as tf
# Standalone Keras 3, deepface import edilmeden ÖNCE yüklenmeli (deepface TF_USE_LEGACY_KERAS=1 ayarlıyor
# ve bu, Keras 3 ile kaydedilmiş .keras modelinin yüklenmesini bozuyor)
import keras
import cv2
import tema
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from deepface import DeepFace
from datetime import datetime
import os
from collections import Counter
import json
import warnings

# Uyarıları bastır
warnings.filterwarnings('ignore')

# OpenCV uyarılarını bastır
os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'
os.environ['OPENCV_VIDEOIO_DEBUG'] = '0'

def gecerli_soru_nolarini_bul():
    """Dataset'teki mevcut soru numaralarını bulur"""
    dataset_path = "dataset/1"
    if not os.path.exists(dataset_path):
        return {str(i) for i in range(1, 16)}  # Varsayılan
    
    mevcut_sorular = set()
    for item in os.listdir(dataset_path):
        if item.startswith("soru") and ("_dogru" in item or "_yalan" in item):
            soru_no = item.split("_")[0].replace("soru", "")
            mevcut_sorular.add(soru_no)
    
    if not mevcut_sorular:
        return {str(i) for i in range(1, 16)}  # Varsayılan
    
    return mevcut_sorular

# Dinamik olarak geçerli soru numaralarını bul
GEÇERLİ_SORU_NOLARI = gecerli_soru_nolarini_bul()

class YalanTespitSistemi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mikro İfade Yalan Tespit Sistemi")
        self.setGeometry(100, 100, 1280, 840)
        self.setMinimumSize(1100, 720)
        self.setStyleSheet(tema.tema_qss())

        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(18)
        main_layout.setContentsMargins(28, 22, 28, 24)

        # Üst başlık alanı
        ust_layout = QHBoxLayout()
        baslik_kutu = QVBoxLayout()
        baslik_kutu.setSpacing(2)
        title = QLabel("🔍 Mikro İfade Yalan Tespit Sistemi")
        title.setObjectName("baslik")
        baslik_kutu.addWidget(title)
        subtitle = QLabel("Yapay zeka destekli analiz  •  Mikro ifadeler + psikolojik sorular")
        subtitle.setObjectName("altBaslik")
        baslik_kutu.addWidget(subtitle)
        ust_layout.addLayout(baslik_kutu)
        ust_layout.addStretch()
        rozet = QLabel("Araştırma prototipi")
        rozet.setObjectName("rozet")
        rozet.setToolTip("Yüz ifadesinden yalan tespiti bilimsel olarak kesin değildir.")
        ust_layout.addWidget(rozet, 0, Qt.AlignVCenter)
        main_layout.addLayout(ust_layout)

        # Ana içerik alanı
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Sol panel - Kullanıcı bilgileri ve kontroller
        left_panel = QWidget()
        left_panel.setFixedWidth(340)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(14)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Kullanıcı bilgileri
        self.user_info_group = QGroupBox("KULLANICI BİLGİLERİ")
        user_layout = QFormLayout()
        user_layout.setSpacing(12)
        user_layout.setLabelAlignment(Qt.AlignLeft)
        user_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.ad_soyad = QLineEdit()
        self.ad_soyad.setPlaceholderText("Adınız ve soyadınız")
        user_layout.addRow("Ad Soyad", self.ad_soyad)

        self.yas = QSpinBox()
        self.yas.setRange(18, 100)
        self.yas.setValue(25)
        self.yas.setButtonSymbols(QAbstractSpinBox.NoButtons)
        user_layout.addRow("Yaş", self.yas)

        self.meslek = QLineEdit()
        self.meslek.setPlaceholderText("Mesleğiniz")
        user_layout.addRow("Meslek", self.meslek)

        self.cinsiyet = QComboBox()
        self.cinsiyet.addItems(["Erkek", "Kadın"])
        user_layout.addRow("Cinsiyet", self.cinsiyet)

        for alan in (self.ad_soyad, self.yas, self.meslek, self.cinsiyet):
            alan.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.user_info_group.setLayout(user_layout)
        left_layout.addWidget(self.user_info_group)

        # Test başlat butonu
        self.test_baslat = QPushButton("🚀  Testi Başlat")
        self.test_baslat.setMinimumHeight(48)
        self.test_baslat.setCursor(Qt.PointingHandCursor)
        self.test_baslat.clicked.connect(self.test_baslat_clicked)
        left_layout.addWidget(self.test_baslat)

        # Durum göstergesi
        self.status_label = QLabel("✅ Sistem hazır. Test başlatmak için bilgileri doldurun.")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.status_label)

        # Test kontrol butonları
        self.control_group = QGroupBox("TEST KONTROLLERİ")
        control_layout = QVBoxLayout()
        control_layout.setSpacing(10)

        self.test_durdur_btn = QPushButton("⏸️  Testi Durdur")
        self.test_durdur_btn.setObjectName("ikincil")
        self.test_durdur_btn.setMinimumHeight(42)
        self.test_durdur_btn.clicked.connect(self.test_durdur)
        self.test_durdur_btn.hide()
        control_layout.addWidget(self.test_durdur_btn)

        self.devam_et_btn = QPushButton("▶️  Devam Et")
        self.devam_et_btn.setMinimumHeight(42)
        self.devam_et_btn.clicked.connect(self.test_devam_et)
        self.devam_et_btn.hide()
        control_layout.addWidget(self.devam_et_btn)

        self.sonuc_buton = QPushButton("📊  Sonuçları Göster")
        self.sonuc_buton.setObjectName("basari")
        self.sonuc_buton.setMinimumHeight(44)
        self.sonuc_buton.clicked.connect(self.sonuc_goster)
        self.sonuc_buton.hide()
        control_layout.addWidget(self.sonuc_buton)

        self.yeni_test_btn = QPushButton("🔄  Aynı Kişi – Yeni Test")
        self.yeni_test_btn.setObjectName("ikincil")
        self.yeni_test_btn.setMinimumHeight(42)
        self.yeni_test_btn.clicked.connect(self.yeni_test_baslat)
        self.yeni_test_btn.hide()
        control_layout.addWidget(self.yeni_test_btn)

        self.yeni_kayit_btn = QPushButton("👤  Yeni Kişi – Yeni Kayıt")
        self.yeni_kayit_btn.setObjectName("ikincil")
        self.yeni_kayit_btn.setMinimumHeight(42)
        self.yeni_kayit_btn.clicked.connect(self.yeni_kayit_baslat)
        self.yeni_kayit_btn.hide()
        control_layout.addWidget(self.yeni_kayit_btn)

        self.control_group.setLayout(control_layout)
        self.control_group.hide()  # Test başlayınca gösterilir
        left_layout.addWidget(self.control_group)

        # İlerleme çubuğu
        self.progress_group = QGroupBox("TEST İLERLEMESİ")
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(8)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 15)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("0 / 15 soru tamamlandı")
        self.progress_label.setObjectName("ilerlemeYazi")
        self.progress_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.progress_label)

        self.progress_group.setLayout(progress_layout)
        left_layout.addWidget(self.progress_group)
        left_layout.addStretch()

        # Sol paneli ana layout'a ekle
        content_layout.addWidget(left_panel)

        # Sağ panel - Kamera ve soru alanı
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(16)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Kamera görüntüsü (pencereyle birlikte büyür, görüntü ortalanır)
        camera_group = QGroupBox("CANLI KAMERA")
        camera_layout = QVBoxLayout()
        camera_layout.setContentsMargins(0, 4, 0, 0)

        self.kamera_label = QLabel()
        self.kamera_label.setObjectName("cameraFrame")
        self.kamera_label.setMinimumSize(480, 320)
        self.kamera_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.kamera_label.setAlignment(Qt.AlignCenter)
        self.kamera_label.setText("📹  Kamera, test başladığında açılacak")
        camera_layout.addWidget(self.kamera_label)

        camera_group.setLayout(camera_layout)
        right_layout.addWidget(camera_group, 1)

        # Soru grubu
        self.soru_group = QGroupBox("SORU")
        soru_layout = QVBoxLayout()
        soru_layout.setSpacing(10)

        self.soru_no_label = QLabel("SORU 1 / 15")
        self.soru_no_label.setObjectName("soruNo")
        soru_layout.addWidget(self.soru_no_label, 0, Qt.AlignLeft)

        self.soru_label = QLabel()
        self.soru_label.setObjectName("questionLabel")
        self.soru_label.setWordWrap(True)
        self.soru_label.setMinimumHeight(60)
        soru_layout.addWidget(self.soru_label)

        # Cevap butonları
        cevap_layout = QHBoxLayout()
        cevap_layout.setSpacing(16)

        self.evet_buton = QPushButton("✓  Evet")
        self.evet_buton.setObjectName("evet")
        self.evet_buton.setMinimumHeight(54)
        self.evet_buton.setCursor(Qt.PointingHandCursor)
        self.evet_buton.setShortcut("E")
        self.evet_buton.setToolTip("Kısayol: E")
        self.evet_buton.clicked.connect(lambda: self.cevap_ver("Evet"))
        cevap_layout.addWidget(self.evet_buton)

        self.hayir_buton = QPushButton("✕  Hayır")
        self.hayir_buton.setObjectName("hayir")
        self.hayir_buton.setMinimumHeight(54)
        self.hayir_buton.setCursor(Qt.PointingHandCursor)
        self.hayir_buton.setShortcut("H")
        self.hayir_buton.setToolTip("Kısayol: H")
        self.hayir_buton.clicked.connect(lambda: self.cevap_ver("Hayır"))
        cevap_layout.addWidget(self.hayir_buton)

        soru_layout.addLayout(cevap_layout)
        self.soru_group.setLayout(soru_layout)
        self.soru_group.hide()
        right_layout.addWidget(self.soru_group)

        # Sağ paneli ana layout'a ekle
        content_layout.addWidget(right_panel, 1)

        # Ana içerik alanını ana layout'a ekle
        main_layout.addWidget(content_widget, 1)
        
        # Değişkenler
        self.kamera = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.kamera_guncelle)
        self.secili_sorular = []
        self.test_basladi = False
        self.test_durduruldu = False
        self.soru_index = 0
        self.cevaplar = []
        self.mikro_ifade_sonuclari = [[] for _ in range(15)]  # Her soru için boş liste
        self.aktif_soru_index = None
        
        # Thread değişkenleri
        self.kamera_kayit_aktif = False
        self.kayit_durduruldu = False
        self.kamera_thread = None
        self.kayit_thread = None
        
        # Kullanıcı bilgilerini saklamak için değişkenler
        self.saklanan_ad_soyad = ""
        self.saklanan_yas = 25
        self.saklanan_meslek = ""
        self.saklanan_cinsiyet = 0
        
        # Analiz veri setleri
        self.psikolojik_sorular_df = None
        self.referans_dagilimlari = {}
        
        # Veri setlerini yükle
        self.veri_setlerini_yukle()

    def veri_setlerini_yukle(self):
        """Gerekli veri setlerini yükler"""
        try:
            # 1. Psikolojik sorular veri seti - yeni CSV dosyasını kullan
            try:
                self.psikolojik_sorular_df = pd.read_csv('psikolojik_sorular_yeni.csv')
                print("✅ Psikolojik sorular veri seti yüklendi")
            except FileNotFoundError:
                print("⚠️ Psikolojik sorular CSV dosyası bulunamadı")
                self.psikolojik_sorular_df = None
            
            # 2. Mikro ifade regresyon modeli ve scaler yükle
            try:
                self.mikro_ifade_model = keras.models.load_model('mikro_ifade_model_regresyon.keras')
                print("✅ Regresyon modeli yüklendi")
            except Exception as e:
                print(f"⚠️ Regresyon modeli yüklenemedi: {e}")
                self.mikro_ifade_model = None
            # Eğitimde kullanılan StandardScaler parametreleri (model_egit.py üretir)
            self.scaler_ort = None
            self.scaler_std = None
            try:
                with open('scaler_parametreleri.json', 'r', encoding='utf-8') as f:
                    sp = json.load(f)
                self.scaler_ort = np.array(sp['mean'], dtype=np.float32)
                self.scaler_std = np.array(sp['scale'], dtype=np.float32)
                print("✅ Scaler parametreleri yüklendi")
            except Exception as e:
                print(f"⚠️ Scaler parametreleri yüklenemedi (ham vektör kullanılacak): {e}")
            # Dataset referans duygu dağılımları için önbellek (soru_no -> sonuç)
            self._dataset_ref_cache = {}
            
            # 3. Referans dağılımları
            try:
                with open('referans_dagilimlari.json', 'r', encoding='utf-8') as f:
                    self.referans_dagilimlari = json.load(f)
                print("✅ Referans dağılımları yüklendi")
            except Exception as e:
                print(f"⚠️ Referans dağılımları yüklenemedi: {e}")
                self.referans_dagilimlari = {}
            
            # 4. Soruları yükle
            self.sorulari_yukle()
            
        except Exception as e:
            print(f"❌ Veri setleri yüklenirken hata: {e}")

    def psikolojik_analiz_yap(self, soru_no, cevap):
        """Psikolojik sorular veri setine göre analiz yapar"""
        try:
            if self.psikolojik_sorular_df is None:
                return None
            
            # Soru numarasını kontrol et
            if soru_no > len(self.psikolojik_sorular_df):
                return None
            
            soru_data = self.psikolojik_sorular_df.iloc[soru_no - 1]
            
            # Cevaba göre beklenen durumu al
            if cevap == "Evet":
                beklenen_durum = soru_data['evet_durumu']
            else:  # Hayır
                beklenen_durum = soru_data['hayir_durumu']

            # CSV'deki "dogru"/"yalan" etiketini uygulama içi "doru"/"yalan" etiketine çevir
            beklenen_durum = str(beklenen_durum).strip().lower()
            if beklenen_durum in ("dogru", "doğru", "doru"):
                beklenen_durum = "doru"
            else:
                beklenen_durum = "yalan"

            # Doğruluk oranı hesapla (basit mantık)
            if beklenen_durum == "doru":
                dogruluk_orani = 0.85  # %85 doğru olma ihtimali
            else:  # yalan
                dogruluk_orani = 0.75  # %75 yalan olma ihtimali
            
            return {
                'beklenen_durum': beklenen_durum,
                'dogruluk_orani': dogruluk_orani,
                'analiz_tipi': 'Psikolojik Soru Analizi'
            }
            
        except Exception as e:
            print(f"Psikolojik analiz hatası: {e}")
            return None

    def mikro_ifade_analiz_yap(self, soru_no, duygu_vektorleri):
        """Mikro ifade analizi yapar (Regresyon modeli ile)"""
        try:
            if not duygu_vektorleri or len(duygu_vektorleri) < 3:
                return None
            
            # Duygu etiketleri
            duygu_etiketleri = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
            
            # Her frame için dominant duyguyu bul
            dominant_duygular = []
            for vektor in duygu_vektorleri:
                max_index = np.argmax(vektor)
                dominant_duygular.append(duygu_etiketleri[max_index])
            
            # Duygu dağılımını hesapla
            duygu_dagilimi = Counter(dominant_duygular)
            
            # Yalan tespiti için duygu analizi (klasik yöntem)
            yalan_duygular = ['fear', 'sad', 'angry', 'disgust']
            dogru_duygular = ['happy', 'neutral', 'surprise']
            
            yalan_sayisi = sum(duygu_dagilimi.get(duygu, 0) for duygu in yalan_duygular)
            dogru_sayisi = sum(duygu_dagilimi.get(duygu, 0) for duygu in dogru_duygular)
            toplam_analiz = len(dominant_duygular)
            
            # Oranları hesapla
            yalan_orani = yalan_sayisi / toplam_analiz if toplam_analiz > 0 else 0
            dogru_orani = dogru_sayisi / toplam_analiz if toplam_analiz > 0 else 0
            
            # Regresyon modeli ile tahmin
            regresyon_kullanildi = False
            regresyon_tahmin = None
            regresyon_güven = 0
            regresyon_yuzde = 0
            if self.mikro_ifade_model is not None:
                # Ortalama duygu vektörünü al
                ort_vektor = np.mean(np.array(duygu_vektorleri), axis=0).reshape(1, -1)
                # Eğitimdeki ölçeklemeyi uygula
                if self.scaler_ort is not None and self.scaler_std is not None:
                    ort_vektor = (ort_vektor - self.scaler_ort) / self.scaler_std
                yalan_olasiligi = float(self.mikro_ifade_model.predict(ort_vektor, verbose=0)[0][0])
                regresyon_yuzde = yalan_olasiligi * 100
                regresyon_kullanildi = True
                if yalan_olasiligi > 0.5:
                    regresyon_tahmin = "yalan"
                    regresyon_güven = yalan_olasiligi
                else:
                    regresyon_tahmin = "doru"
                    regresyon_güven = 1 - yalan_olasiligi
            
            # Genel tahmin (klasik yöntem)
            if yalan_orani > dogru_orani:
                tahmin = "yalan"
                güven_orani = yalan_orani
            else:
                tahmin = "doru"
                güven_orani = dogru_orani
            
            return {
                'tahmin': tahmin,
                'güven_orani': güven_orani,
                'yalan_orani': yalan_orani,
                'dogru_orani': dogru_orani,
                'toplam_analiz': toplam_analiz,
                'duygu_dagilimi': duygu_dagilimi,
                'regresyon_kullanildi': regresyon_kullanildi,
                'regresyon_tahmin': regresyon_tahmin,
                'regresyon_güven': regresyon_güven,
                'regresyon_yuzde': regresyon_yuzde,
                'analiz_tipi': 'Mikro İfade Analizi (Regresyon)'
            }
            
        except Exception as e:
            print(f"Mikro ifade analiz hatası: {e}")
            return None

    def dataset_analiz_yap(self, soru_no, duygu_vektorleri):
        """Dataset klasörlerine göre analiz yapar"""
        try:
            if not self.referans_dagilimlari or not duygu_vektorleri:
                return None
            
            soru_str = str(soru_no)
            if soru_str not in self.referans_dagilimlari:
                return None
            
            # Test dağılımını hesapla
            duygu_etiketleri = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
            test_duygular = []
            
            for vektor in duygu_vektorleri:
                max_index = np.argmax(vektor)
                test_duygular.append(duygu_etiketleri[max_index])
            
            test_counter = Counter(test_duygular)
            test_dagilim = []
            for duygu in duygu_etiketleri:
                oran = test_counter.get(duygu, 0) / len(test_duygular)
                test_dagilim.append(oran)
            
            # Referans dağılımlarla karşılaştır
            ref_data = self.referans_dagilimlari[soru_str]
            dogru_dagilim = ref_data['dogru_dagilim']
            yalan_dagilim = ref_data['yalan_dagilim']
            
            # Cosine similarity hesapla
            dogru_benzerlik = self.dagilim_benzerligi_hesapla(test_dagilim, dogru_dagilim)
            yalan_benzerlik = self.dagilim_benzerligi_hesapla(test_dagilim, yalan_dagilim)
            
            # Hangi etikete daha yakın
            if dogru_benzerlik > yalan_benzerlik:
                tahmin = "doru"
                benzerlik_orani = dogru_benzerlik
            else:
                tahmin = "yalan"
                benzerlik_orani = yalan_benzerlik
            
            # Güven oranını artır (daha fazla veri varsa)
            if len(test_duygular) > 3:
                benzerlik_orani = min(benzerlik_orani * 1.1, 1.0)  # %10 artır ama 1'i geçme
            
            return {
                'tahmin': tahmin,
                'benzerlik_orani': benzerlik_orani,
                'dogru_benzerlik': dogru_benzerlik,
                'yalan_benzerlik': yalan_benzerlik,
                'test_dagilim': test_dagilim,
                'test_duygu_sayisi': len(test_duygular),
                'analiz_tipi': 'Dataset Karşılaştırması'
            }
            
        except Exception as e:
            print(f"Dataset analiz hatası: {e}")
            return None

    def dataset_yuz_ifade_analiz_yap(self, soru_no, duygu_vektorleri):
        """Dataset'teki yüz ifadelerine göre doğruluk/yalan yüzdesi hesaplar"""
        try:
            if not duygu_vektorleri:
                return None
            
            soru_str = str(soru_no)
            dataset_path = f"dataset/1/soru{soru_str}"
            
            # Doğru ve yalan klasörlerini kontrol et
            dogru_path = f"{dataset_path}_dogru"
            yalan_path = f"{dataset_path}_yalan"
            
            if not os.path.exists(dogru_path) or not os.path.exists(yalan_path):
                return None
            
            # Test kullanıcısının duygu dağılımını hesapla
            duygu_etiketleri = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
            test_duygular = []
            
            for vektor in duygu_vektorleri:
                max_index = np.argmax(vektor)
                test_duygular.append(duygu_etiketleri[max_index])
            
            test_counter = Counter(test_duygular)
            test_dagilim = []
            for duygu in duygu_etiketleri:
                oran = test_counter.get(duygu, 0) / len(test_duygular)
                test_dagilim.append(oran)
            
            # Dataset referans dağılımları soru başına bir kez hesaplanıp önbelleğe alınır
            # (her cevapta DeepFace'i tekrar çalıştırmak çok yavaştı)
            if soru_str not in self._dataset_ref_cache:
                def klasor_duygulari(klasor):
                    duygular = []
                    dosyalar = sorted(f for f in os.listdir(klasor) if f.endswith('.jpg'))
                    for file in dosyalar[:5]:  # İlk 5 görüntüyü al
                        try:
                            result = DeepFace.analyze(os.path.join(klasor, file), actions=['emotion'], enforce_detection=False)
                            if isinstance(result, list):
                                result = result[0]
                            duygular.append(result['dominant_emotion'])
                        except Exception:
                            continue
                    return duygular

                dogru_duygular = klasor_duygulari(dogru_path)
                yalan_duygular = klasor_duygulari(yalan_path)
                if not dogru_duygular or not yalan_duygular:
                    self._dataset_ref_cache[soru_str] = None
                else:
                    dogru_counter = Counter(dogru_duygular)
                    yalan_counter = Counter(yalan_duygular)
                    self._dataset_ref_cache[soru_str] = (
                        [dogru_counter.get(d, 0) / len(dogru_duygular) for d in duygu_etiketleri],
                        [yalan_counter.get(d, 0) / len(yalan_duygular) for d in duygu_etiketleri],
                    )

            if self._dataset_ref_cache[soru_str] is None:
                return None
            dogru_dataset_dagilim, yalan_dataset_dagilim = self._dataset_ref_cache[soru_str]

            # Test dağılımı ile karşılaştır
            dogru_benzerlik = self.dagilim_benzerligi_hesapla(test_dagilim, dogru_dataset_dagilim)
            yalan_benzerlik = self.dagilim_benzerligi_hesapla(test_dagilim, yalan_dataset_dagilim)
            
            # Hangi etikete daha yakın
            if dogru_benzerlik > yalan_benzerlik:
                tahmin = "doru"
                benzerlik_orani = dogru_benzerlik
                dogruluk_yuzdesi = dogru_benzerlik * 100
                yalan_yuzdesi = (1 - dogru_benzerlik) * 100
            else:
                tahmin = "yalan"
                benzerlik_orani = yalan_benzerlik
                yalan_yuzdesi = yalan_benzerlik * 100
                dogruluk_yuzdesi = (1 - yalan_benzerlik) * 100
            
            return {
                'tahmin': tahmin,
                'benzerlik_orani': benzerlik_orani,
                'dogru_benzerlik': dogru_benzerlik,
                'yalan_benzerlik': yalan_benzerlik,
                'dogruluk_yuzdesi': round(dogruluk_yuzdesi, 2),
                'yalan_yuzdesi': round(yalan_yuzdesi, 2),
                'test_dagilim': test_dagilim,
                'dogru_dataset_dagilim': dogru_dataset_dagilim,
                'yalan_dataset_dagilim': yalan_dataset_dagilim,
                'test_duygu_sayisi': len(test_duygular),
                'analiz_tipi': 'Dataset Yüz İfadesi Analizi'
            }
            
        except Exception as e:
            print(f"Dataset yüz ifadesi analiz hatası: {e}")
            return None

    def genel_sonuc_hesapla(self, psikolojik_sonuc, mikro_ifade_sonuc, dataset_yuz_sonuc, demo_referans=None, yuz_referans=None):
        """5 farklı analiz sonucunu birleştirerek genel sonuç hesaplar (demo referansı ve yüz referansı dahil)"""
        try:
            sonuclar = []
            agirliklar = []
            if psikolojik_sonuc:
                sonuclar.append(psikolojik_sonuc['beklenen_durum'])
                agirliklar.append(0.25)
            if mikro_ifade_sonuc:
                sonuclar.append(mikro_ifade_sonuc['tahmin'])
                agirliklar.append(0.25)
            if dataset_yuz_sonuc:
                sonuclar.append(dataset_yuz_sonuc['tahmin'])
                agirliklar.append(0.2)
            if demo_referans:
                sonuclar.append(demo_referans)
                agirliklar.append(0.15)
            if yuz_referans:
                sonuclar.append(yuz_referans)
                agirliklar.append(0.15)
            if not sonuclar:
                return None
            doru_puani = 0
            yalan_puani = 0
            for sonuc, agirlik in zip(sonuclar, agirliklar):
                if sonuc == "doru":
                    doru_puani += agirlik
                else:
                    yalan_puani += agirlik
            if doru_puani > yalan_puani:
                genel_tahmin = "doru"
                genel_güven = doru_puani
            else:
                genel_tahmin = "yalan"
                genel_güven = yalan_puani
            return {
                'genel_tahmin': genel_tahmin,
                'genel_güven': genel_güven,
                'doru_puani': doru_puani,
                'yalan_puani': yalan_puani,
                'analiz_sayisi': len(sonuclar)
            }
        except Exception as e:
            print(f"Genel sonuç hesaplama hatası: {e}")
            return None

    def closeEvent(self, event):
        """Pencere kapatılırken kamera kaynaklarını temizle"""
        self.kamera_temizle()
        event.accept()

    def kamera_temizle(self):
        """Kamera kaynaklarını güvenli şekilde temizler"""
        try:
            # Kamera kaydını durdur
            self.kamera_kayit_aktif = False
            
            # Timer'ları durdur
            if hasattr(self, 'timer') and self.timer.isActive():
                self.timer.stop()
                print("✅ Kamera timer durduruldu")
            
            if hasattr(self, 'kamera_timer') and self.kamera_timer.isActive():
                self.kamera_timer.stop()
                print("✅ Kamera timer durduruldu")
            
            if hasattr(self, 'kayit_timer') and self.kayit_timer.isActive():
                self.kayit_timer.stop()
                print("✅ Kayıt timer durduruldu")
            
            # Kamera nesnesini kapat
            if hasattr(self, 'cap') and self.cap is not None:
                if self.cap.isOpened():
                    self.cap.release()
                    print("✅ Kamera kapatıldı")
                self.cap = None
            
            # Tüm kamera kaynaklarını temizle
            # (OpenCV "headless" sürümünde bu çağrı desteklenmez; arayüz Qt olduğundan önemsiz)
            try:
                cv2.destroyAllWindows()
            except cv2.error:
                pass

            print("✅ Kamera kaynakları temizlendi")
            
        except Exception as e:
            print(f"⚠️ Kamera temizleme hatası: {e}")
        
        finally:
            # Durum mesajını güncelle
            if hasattr(self, 'status_label'):
                self.status_label.setText("Kamera kaynakları temizlendi")

    def sorulari_yukle(self):
        """CSV dosyasından soruları yükler"""
        try:
            df = pd.read_csv('psikolojik_sorular_yeni.csv')
            self.secili_sorular = df['soru'].tolist()
        except FileNotFoundError:
            print("CSV dosyası bulunamadı. Varsayılan sorular kullanılıyor.")
            self.secili_sorular = [
                "Hiç birini kırdığın için kendini suçlu hissettin mi?",
                "Kendini olduğundan daha iyi göstermeye çalıştığın olur mu?",
                "Kimseyle paylaşamadığın bir sırrın var mı?",
                "En yakınlarına bile yalan söylediğin oldu mu?",
                "Zaman zaman kendinden nefret ettiğin oldu mu?",
                "Yalnız kalmaktan korkar mısın?",
                "Hiç insanların seni anlamadığını düşündün mü?",
                "Hep pozitif biri misindir?",
                "İnsanlara kolay güvenirsin diyebilir misin?",
                "Hiç maskeyle yaşadığını düşündün mü?",
                "Başkalarının onayını almak seni mutlu eder mi?",
                "Hiç güçlü görünmeye çalıştığın ama aslında kırıldığın oldu mu?",
                "Hayatında hiç kimseye gerçekten açıldın mı?",
                "Kendini olduğundan daha kötü göstermeye çalıştığın oldu mu?",
                "Hiç kimseye güvenmediğin oldu mu?"
            ]

    def test_baslat_clicked(self):
        if not self.ad_soyad.text().strip() or not self.meslek.text().strip():
            QMessageBox.warning(self, "Uyarı", "Lütfen ad soyad ve meslek alanlarını doldurun!")
            return
        
        # Kullanıcı bilgilerini sakla
        self.saklanan_ad_soyad = self.ad_soyad.text().strip()
        self.saklanan_yas = self.yas.value()
        self.saklanan_meslek = self.meslek.text().strip()
        self.saklanan_cinsiyet = self.cinsiyet.currentIndex()
        
        # Kamera başlat - farklı kamera indekslerini dene
        self.cap = None
        kamera_bulundu = False
        
        # Önce varsayılan kamerayı dene
        for kamera_index in [0, 1, 2]:
            try:
                self.cap = cv2.VideoCapture(kamera_index, cv2.CAP_DSHOW)  # DirectShow backend kullan
                if self.cap.isOpened():
                    # Test frame'i al
                    ret, frame = self.cap.read()
                    if ret and frame is not None:
                        kamera_bulundu = True
                        print(f"Kamera {kamera_index} başarıyla başlatıldı")
                        break
                    else:
                        self.cap.release()
                        self.cap = None
                else:
                    if self.cap:
                        self.cap.release()
                        self.cap = None
            except Exception as e:
                print(f"Kamera {kamera_index} başlatılırken hata: {e}")
                if self.cap:
                    self.cap.release()
                    self.cap = None
        
        if not kamera_bulundu:
            QMessageBox.critical(self, "Kamera Hatası", 
                               "Kamera başlatılamadı!\n\n"
                               "Lütfen şunları kontrol edin:\n"
                               "• Kameranızın bağlı olduğundan emin olun\n"
                               "• Başka bir uygulama kamerayı kullanmıyor olmalı\n"
                               "• Kamera izinlerini kontrol edin\n"
                               "• Kameranızın çalışır durumda olduğundan emin olun")
            return
        
        # Kamera ayarlarını optimize et
        try:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception as e:
            print(f"Kamera ayarları yapılırken hata: {e}")
        
        # Test durumunu başlat
        self.test_basladi = True
        self.test_durduruldu = False
        self.soru_index = 0
        self.cevaplar = []
        toplam_soru = len(self.secili_sorular)
        self.mikro_ifade_sonuclari = [[] for _ in range(toplam_soru)]  # Her soru için boş liste
        self.aktif_soru_index = 0  # Aktif soru indeksini başlat
        
        # UI güncelle
        self.user_info_group.hide()
        self.test_baslat.hide()
        self.soru_group.show()
        self.test_durdur_btn.show()
        self.yeni_test_btn.hide()
        self.yeni_kayit_btn.hide()
        self.control_group.show()
        
        # İlerleme çubuğunu güncelle
        self.progress_bar.setMaximum(toplam_soru)
        self.progress_bar.setValue(0)
        self.progress_label.setText(f"0 / {toplam_soru} soru tamamlandı")
        
        # Durum mesajını güncelle
        self.status_label.setText("Test başlatıldı. İlk soru gösteriliyor...")
        
        # İlk soruyu göster
        self.soru_goster()
        
        # Kamera timer'ını başlat
        self.timer.start(30)  # 30ms = yaklaşık 30 FPS
        
        # Kamera kaydını başlat
        self.kamera_kayit_baslat()

    def kamera_guncelle(self):
        if self.cap and self.cap.isOpened():
            try:
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    # Görüntüyü QT formatına çevir
                    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb_image.shape
                    bytes_per_line = ch * w
                    qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(qt_image)
                    scaled_pixmap = pixmap.scaled(self.kamera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.kamera_label.setPixmap(scaled_pixmap)
                else:
                    # Frame alınamadıysa uyarı göster
                    self.kamera_label.setText("Kamera görüntüsü alınamıyor...")
            except Exception as e:
                print(f"Kamera güncelleme hatası: {e}")
                self.kamera_label.setText("Kamera hatası oluştu...")

    def duygu_vektor(self, duygular):
        """Duygu vektörünü normalize et"""
        duygu_etiketleri = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        vektor = []
        for duygu in duygu_etiketleri:
            vektor.append(duygular.get(duygu, 0))
        return np.array(vektor)

    def soru_goster(self):
        if self.soru_index < len(self.secili_sorular):
            soru = self.secili_sorular[self.soru_index]
            self.soru_label.setText(soru)
            self.soru_no_label.setText(f"SORU {self.soru_index + 1} / {len(self.secili_sorular)}")
            self.soru_group.show()
            
            # İlerleme çubuğunu güncelle
            toplam_soru = len(self.secili_sorular)
            self.progress_bar.setValue(self.soru_index)
            self.progress_label.setText(f"{self.soru_index} / {toplam_soru} soru tamamlandı")
            
            # Durum mesajını güncelle
            self.status_label.setText(f"Soru {self.soru_index + 1} gösteriliyor. Cevabınızı verin...")
            
            # Kamera kaydını başlat
            if not self.kamera_kayit_aktif:
                self.kamera_kayit_baslat()
            
            # Aktif soruyu thread için güncelle
            self.aktif_soru_index = self.soru_index
        else:
            # Test bitti
            self.test_bitir()

    def test_durdur(self):
        if self.test_basladi and not self.test_durduruldu:
            self.test_durduruldu = True
            self.kayit_durduruldu = True
            
            # Butonları güncelle
            self.test_durdur_btn.hide()
            self.devam_et_btn.show()
            self.yeni_test_btn.show()
            self.yeni_kayit_btn.show()
            
            # Durum mesajını güncelle
            self.status_label.setText("Test durduruldu. Devam etmek için 'Devam Et' butonuna basın.")
            
            # Kamera kaydını durdur
            self.kamera_kayit_durdur()
            
            QMessageBox.information(self, "Test Durduruldu", 
                                  "Test durduruldu. Devam etmek için 'Devam Et' butonuna basın.")

    def test_devam_et(self):
        if self.test_durduruldu:
            self.test_durduruldu = False
            self.kayit_durduruldu = False
            
            # Butonları güncelle
            self.devam_et_btn.hide()
            self.test_durdur_btn.show()
            self.yeni_test_btn.hide()
            self.yeni_kayit_btn.hide()
            
            # Durum mesajını güncelle
            self.status_label.setText("Test kaldığı yerden devam ediyor...")
            
            # Kamera kaydını başlat
            self.kamera_kayit_baslat()
            
            QMessageBox.information(self, "Test Devam Ediyor", 
                                  "Test kaldığı yerden devam ediyor.")

    def yeni_test_baslat(self):
        # Test durumunu sıfırla
        self.test_basladi = False
        self.test_durduruldu = False
        self.soru_index = 0
        self.cevaplar = []
        self.mikro_ifade_sonuclari = []
        self.kamera_kayit_aktif = False
        self.aktif_soru_index = None
        
        # Kamera kaynaklarını temizle
        self.kamera_temizle()
        
        # Arayüzü sıfırla
        self.user_info_group.show()
        self.soru_group.hide()
        self.sonuc_buton.hide()
        self.test_durdur_btn.hide()
        self.yeni_test_btn.hide()
        self.yeni_kayit_btn.hide()
        self.control_group.hide()
        self.test_baslat.show()  # Test başlat butonunu göster
        
        # Kullanıcı bilgilerini geri yükle (saklanan bilgileri koru)
        self.ad_soyad.setText(self.saklanan_ad_soyad)
        self.yas.setValue(self.saklanan_yas)
        self.meslek.setText(self.saklanan_meslek)
        self.cinsiyet.setCurrentIndex(self.saklanan_cinsiyet)
        
        # İlerleme çubuğunu sıfırla
        self.progress_bar.setValue(0)
        self.progress_label.setText("0 / 0 soru tamamlandı")
        
        # Durum mesajını güncelle
        self.status_label.setText("Sistem hazır. Test başlatmak için bilgileri doldurun.")
        
        # Kamera frame'ini temizle
        if hasattr(self, 'kamera_label'):
            self.kamera_label.clear()
            self.kamera_label.setText("📹 Kamera kapalı")
        
        print("✅ Yeni test başlatma tamamlandı - kullanıcı bilgileri korundu")

    def yeni_kayit_baslat(self):
        # Kullanıcı bilgilerini sıfırla
        self.ad_soyad.clear()
        self.meslek.clear()
        self.yas.setValue(25)
        self.cinsiyet.setCurrentIndex(0)
        
        # Saklanan bilgileri de sıfırla
        self.saklanan_ad_soyad = ""
        self.saklanan_yas = 25
        self.saklanan_meslek = ""
        self.saklanan_cinsiyet = 0
        
        # Test durumunu sıfırla
        self.test_basladi = False
        self.test_durduruldu = False
        self.soru_index = 0
        self.cevaplar = []
        self.mikro_ifade_sonuclari = []
        self.kamera_kayit_aktif = False
        self.aktif_soru_index = None
        
        # Kamera kaynaklarını temizle
        self.kamera_temizle()
        
        # Arayüzü sıfırla
        self.yeni_test_btn.hide()
        self.yeni_kayit_btn.hide()
        self.sonuc_buton.hide()
        self.test_baslat.show()
        self.user_info_group.show()
        self.soru_group.hide()
        self.test_durdur_btn.hide()
        self.devam_et_btn.hide()
        
        # İlerleme çubuğunu sıfırla
        toplam_soru = len(self.secili_sorular)
        self.progress_bar.setMaximum(toplam_soru)
        self.progress_bar.setValue(0)
        self.progress_label.setText(f"0 / {toplam_soru} soru tamamlandı")
        
        # Durum mesajını güncelle
        self.status_label.setText("Sistem hazır. Yeni kayıt için bilgileri doldurun.")
        
        print("✅ Yeni kayıt başlatma tamamlandı - tüm bilgiler sıfırlandı")

    def cevap_ver(self, cevap):
        if self.test_basladi and not self.test_durduruldu:
            self.cevaplar.append(cevap)
            
            # İlerleme çubuğunu güncelle
            toplam_soru = len(self.secili_sorular)
            self.progress_bar.setValue(self.soru_index + 1)
            self.progress_label.setText(f"{self.soru_index + 1} / {toplam_soru} soru tamamlandı")
            
            # Durum mesajını güncelle
            self.status_label.setText(f"Cevap kaydedildi: {cevap}")
            
            # Bir sonraki soruya geç
            self.soru_index += 1
            if self.soru_index < len(self.secili_sorular):
                self.soru_goster()
            else:
                self.test_bitir()

    def test_bitir(self):
        self.test_basladi = False
        self.test_durduruldu = True
        self.kamera_kayit_aktif = False
        
        # İlerleme çubuğunu tamamla
        toplam_soru = len(self.secili_sorular)
        self.progress_bar.setValue(toplam_soru)
        self.progress_label.setText(f"{toplam_soru} / {toplam_soru} soru tamamlandı")
        
        # Durum mesajını güncelle
        self.status_label.setText("Test tamamlandı! Sonuçları görmek için 'Sonuçları Göster' butonuna basın.")
        
        # Sonuç butonunu göster
        self.sonuc_buton.show()
        self.soru_group.hide()
        self.test_durdur_btn.hide()
        self.yeni_test_btn.show()
        self.yeni_kayit_btn.show()
        
        # Kamera kaydını durdur
        self.kamera_kayit_durdur()

    def dagilim_benzerligi_hesapla(self, test_dagilim, referans_dagilim):
        """İki dağılım arasındaki benzerliği hesaplar (cosine similarity)"""
        test_array = np.array(test_dagilim)
        ref_array = np.array(referans_dagilim)
        
        # Cosine similarity
        dot_product = np.dot(test_array, ref_array)
        norm_test = np.linalg.norm(test_array)
        norm_ref = np.linalg.norm(ref_array)
        
        if norm_test == 0 or norm_ref == 0:
            return 0
        
        similarity = dot_product / (norm_test * norm_ref)
        return similarity

    @staticmethod
    def duygu_ozeti(duygular, adet=3):
        """Duygu sözlüğünü en baskın birkaç duyguyla okunaklı bir özete çevirir."""
        ceviri = {'angry': 'kızgın', 'disgust': 'iğrenme', 'fear': 'korku', 'happy': 'mutlu',
                  'sad': 'üzgün', 'surprise': 'şaşkın', 'neutral': 'nötr'}
        try:
            sirali = sorted(duygular.items(), key=lambda kv: kv[1], reverse=True)[:adet]
            return ", ".join(f"{ceviri.get(ad, ad)} %{deger:.1f}" for ad, deger in sirali if deger >= 0.05) or "—"
        except Exception:
            return str(duygular)

    def demo_gorsel_analiz(self):
        """Demo.png'deki yüzleri analiz eder ve sonuçları döndürür."""
        try:
            demo_path = os.path.join('mikro_ifade_data', 'Demo.png')
            if not os.path.exists(demo_path):
                return None
            # DeepFace ile yüzleri tespit et ve analiz et
            results = DeepFace.analyze(demo_path, actions=['emotion'], enforce_detection=False)
            # Eğer birden fazla yüz varsa liste döner
            if not isinstance(results, list):
                results = [results]
            analizler = []
            for idx, res in enumerate(results):
                duygular = res['emotion']
                vektor = self.duygu_vektor(duygular)
                # Klasik ve regresyon analizini uygula
                mikro_sonuc = self.mikro_ifade_analiz_yap(0, [vektor])
                analizler.append({
                    'yuz_no': idx+1,
                    'duygular': duygular,
                    'vektor': vektor,
                    'mikro_sonuc': mikro_sonuc
                })
            return analizler
        except Exception as e:
            print(f"Demo görsel analiz hatası: {e}")
            return None

    def kullanici_ortalama_vektor(self):
        """Kullanıcının tüm sorulardaki frame'lerinden ortalama duygu vektörünü döndürür."""
        tum_vektorler = []
        for vektorler in self.mikro_ifade_sonuclari:
            tum_vektorler.extend(vektorler)
        if not tum_vektorler:
            return None
        return np.mean(np.array(tum_vektorler), axis=0)

    def sonuc_goster(self):
        if not self.cevaplar:
            QMessageBox.warning(self, "Uyarı", "Henüz test tamamlanmamış!")
            return
        try:
            mesaj = "🔍 <b>KAPSAMLI YALAN TESPİT ANALİZİ</b>\n"
            mesaj += "="*70 + "\n\n"
            # --- DEMO GÖRSELİ ANALİZİ ---
            demo_analizler = self.demo_gorsel_analiz()
            kullanici_ort_vektor = self.kullanici_ortalama_vektor()
            mesaj += "🖼️ <b>DEMO GÖRSELİ ANALİZİ:</b>\n"
            demo_karsilastirma_sonuclari = []
            if demo_analizler:
                for analiz in demo_analizler:
                    mesaj += f"   👤 Yüz {analiz['yuz_no']}:\n"
                    mesaj += f"      Duygular: {self.duygu_ozeti(analiz['duygular'])}\n"
                    mikro = analiz['mikro_sonuc']
                    if mikro:
                        mesaj += f"      Klasik Tahmin: <b>{mikro['tahmin'].upper()}</b> (%{mikro['güven_orani']*100:.1f})\n"
                        mesaj += f"      Yalan Oranı (Klasik): %{mikro['yalan_orani']*100:.1f} | Doğru Oranı: %{mikro['dogru_orani']*100:.1f}\n"
                        if mikro['regresyon_kullanildi']:
                            mesaj += f"      🤖 Regresyon Tahmin: <b>{mikro['regresyon_tahmin'].upper()}</b> (Yalan Olasılığı: %{mikro['regresyon_yuzde']:.1f}) | Güven: %{mikro['regresyon_güven']*100:.1f}\n"
                    if kullanici_ort_vektor is not None:
                        demo_vektor = analiz['vektor']
                        similarity = self.dagilim_benzerligi_hesapla(kullanici_ort_vektor, demo_vektor)
                        demo_yuz_etiket = None
                        demo_yuz_yuzde = None
                        if mikro and mikro['regresyon_kullanildi']:
                            demo_yuz_etiket = mikro['regresyon_tahmin']
                            demo_yuz_yuzde = mikro['regresyon_yuzde']
                        elif mikro:
                            demo_yuz_etiket = mikro['tahmin']
                            demo_yuz_yuzde = mikro['güven_orani']*100
                        if demo_yuz_etiket:
                            mesaj += f"      Kullanıcı ile Benzerlik (Cosine): %{similarity*100:.1f} | Demo Yüz: <b>{demo_yuz_etiket.upper()}</b> (%{demo_yuz_yuzde:.1f})\n"
                        else:
                            mesaj += f"      Kullanıcı ile Benzerlik (Cosine): %{similarity*100:.1f}\n"
                        referans = None
                        if mikro and mikro['regresyon_kullanildi']:
                            referans = mikro['regresyon_tahmin']
                        elif mikro:
                            referans = mikro['tahmin']
                        if referans:
                            demo_karsilastirma_sonuclari.append((similarity, referans))
                    mesaj += "\n"
                mesaj += "\n"
            else:
                mesaj += "   Demo görseli bulunamadı veya analiz edilemedi.\n\n"
            # --- YÜZ İFADESİ REFERANSINA GÖRE ---
            ref_analiz = self.demo_referans_grup_analiz()
            mesaj += "🔬 <b>YÜZ İFADESİ REFERANSINA GÖRE:</b>\n"
            if ref_analiz:
                mesaj += f"   Yalan Referans Benzerliği: %{ref_analiz['yalan_benzerlik']*100:.1f}\n"
                mesaj += f"   Doğru Referans Benzerliği: %{ref_analiz['doru_benzerlik']*100:.1f}\n"
                mesaj += f"   Sonuç: <b>{ref_analiz['referans_etiket'].upper()}</b> söylüyorsunuz (Benzerlik: %{ref_analiz['referans_oran']*100:.1f})\n"
            else:
                mesaj += "   Referans analizi yapılamadı.\n"
            mesaj += "─"*50 + "\n\n"

            # Demo referans kararını ve yüz referansını başta tanımla
            demo_referans_karar = None
            if demo_karsilastirma_sonuclari:
                best = max(demo_karsilastirma_sonuclari, key=lambda x: x[0])
                demo_referans_karar = best[1]
            yuz_referans = ref_analiz['referans_etiket'] if ref_analiz else None

            toplam_soru = len(self.cevaplar)
            genel_sonuclar = []
            for i in range(toplam_soru):
                soru_no = i + 1
                cevap = self.cevaplar[i]
                duygu_vektorleri = self.mikro_ifade_sonuclari[i] if i < len(self.mikro_ifade_sonuclari) else []
                mesaj += f"🔹 <b>SORU {soru_no}:</b>\n"
                mesaj += f"   📝 Verilen Cevap: <b>{cevap}</b>\n\n"
                psikolojik_sonuc = self.psikolojik_analiz_yap(soru_no, cevap)
                if psikolojik_sonuc:
                    mesaj += f"   🧠 <b>Psikolojik Analiz:</b>\n"
                    mesaj += f"      Beklenen Durum: <b>{psikolojik_sonuc['beklenen_durum'].upper()}</b>\n"
                    mesaj += f"      Doğruluk Oranı: <b>%{psikolojik_sonuc['dogruluk_orani']*100:.1f}</b>\n\n"
                else:
                    mesaj += f"   🧠 <b>Psikolojik Analiz:</b> Veri bulunamadı\n\n"
                mikro_ifade_sonuc = self.mikro_ifade_analiz_yap(soru_no, duygu_vektorleri)
                if mikro_ifade_sonuc:
                    mesaj += f"   😊 <b>Mikro İfade Analizi (Regresyon):</b>\n"
                    mesaj += f"      Tahmin: <b>{mikro_ifade_sonuc['tahmin'].upper()}</b>\n"
                    mesaj += f"      Güven Oranı: <b>%{mikro_ifade_sonuc['güven_orani']*100:.1f}</b>\n"
                    mesaj += f"      Yalan Oranı: %{mikro_ifade_sonuc['yalan_orani']*100:.1f}\n"
                    mesaj += f"      Doğru Oranı: %{mikro_ifade_sonuc['dogru_orani']*100:.1f}\n"
                    mesaj += f"      Toplam Analiz: {mikro_ifade_sonuc['toplam_analiz']} frame\n"
                    if mikro_ifade_sonuc['regresyon_kullanildi']:
                        mesaj += f"      🤖 <b>Regresyon Modeli:</b>\n"
                        mesaj += f"         Tahmin: {mikro_ifade_sonuc['regresyon_tahmin'].upper()}\n"
                        mesaj += f"         Yalan Olasılığı: <b>%{mikro_ifade_sonuc['regresyon_yuzde']:.1f}</b>\n"
                        mesaj += f"         Güven: %{mikro_ifade_sonuc['regresyon_güven']*100:.1f}\n"
                    mesaj += f"      Duygu Dağılımı: {dict(mikro_ifade_sonuc['duygu_dagilimi'])}\n\n"
                else:
                    mesaj += f"   😊 <b>Mikro İfade Analizi:</b> Yeterli veri yok\n\n"
                dataset_yuz_sonuc = self.dataset_yuz_ifade_analiz_yap(soru_no, duygu_vektorleri)
                if dataset_yuz_sonuc:
                    mesaj += f"   🖼️ <b>Dataset Yüz İfadesi Analizi:</b>\n"
                    mesaj += f"      Tahmin: <b>{dataset_yuz_sonuc['tahmin'].upper()}</b>\n"
                    mesaj += f"      Doğruluk Yüzdesi: <b>%{dataset_yuz_sonuc['dogruluk_yuzdesi']}</b>\n"
                    mesaj += f"      Yalan Yüzdesi: <b>%{dataset_yuz_sonuc['yalan_yuzdesi']}</b>\n"
                    mesaj += f"      Benzerlik Oranı: %{dataset_yuz_sonuc['benzerlik_orani']*100:.1f}\n"
                    mesaj += f"      Doğru Benzerliği: %{dataset_yuz_sonuc['dogru_benzerlik']*100:.1f}\n"
                    mesaj += f"      Yalan Benzerliği: %{dataset_yuz_sonuc['yalan_benzerlik']*100:.1f}\n"
                    mesaj += f"      Test Veri Sayısı: {dataset_yuz_sonuc['test_duygu_sayisi']} frame\n\n"
                else:
                    mesaj += f"   🖼️ <b>Dataset Yüz İfadesi Analizi:</b> Dataset görüntüleri bulunamadı\n\n"
                genel_sonuc = self.genel_sonuc_hesapla(psikolojik_sonuc, mikro_ifade_sonuc, dataset_yuz_sonuc, demo_referans_karar, yuz_referans)
                if genel_sonuc:
                    mesaj += f"   🎯 <b>GENEL SONUÇ:</b>\n"
                    mesaj += f"      Tahmin: <b>{genel_sonuc['genel_tahmin'].upper()}</b>\n"
                    mesaj += f"      Güven Oranı: <b>%{genel_sonuc['genel_güven']*100:.1f}</b>\n"
                    mesaj += f"      Doğru Puanı: {genel_sonuc['doru_puani']:.2f}\n"
                    mesaj += f"      Yalan Puanı: {genel_sonuc['yalan_puani']:.2f}\n"
                    mesaj += f"      Kullanılan Analiz: {genel_sonuc['analiz_sayisi']}/5 (Demo ve Yüz referansı dahil)\n\n"
                    genel_sonuclar.append(genel_sonuc)
                else:
                    mesaj += f"   🎯 <b>GENEL SONUÇ:</b> Yeterli veri yok\n\n"
                mesaj += "─"*50 + "\n\n"
            # Genel İstatistikler
            if genel_sonuclar:
                doru_sayisi = sum(1 for sonuc in genel_sonuclar if sonuc['genel_tahmin'] == 'doru')
                yalan_sayisi = sum(1 for sonuc in genel_sonuclar if sonuc['genel_tahmin'] == 'yalan')
                ortalama_güven = sum(sonuc['genel_güven'] for sonuc in genel_sonuclar) / len(genel_sonuclar)
                mesaj += f"🏆 <b>GENEL İSTATİSTİKLER:</b>\n"
                mesaj += "="*50 + "\n"
                mesaj += f"📊 Toplam Soru: {toplam_soru}\n"
                mesaj += f"✅ Doğru Tahmin: {doru_sayisi}\n"
                mesaj += f"❌ Yalan Tahmin: {yalan_sayisi}\n"
                mesaj += f"📈 Ortalama Güven Oranı: %{ortalama_güven*100:.1f}\n"
                if doru_sayisi > yalan_sayisi:
                    mesaj += f"🎯 <b>GENEL KARAR: DOĞRU SÖYLÜYORSUNUZ</b>\n"
                else:
                    mesaj += f"🎯 <b>GENEL KARAR: YALAN SÖYLÜYORSUNUZ</b>\n"
            # Sonuçları ayrı bir pencerede göster
            self.sonuc_penceresi_goster(mesaj, genel_sonuclar)
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Sonuçlar hesaplanırken bir hata oluştu: {str(e)}")

    def sonuc_penceresi_goster(self, mesaj, genel_sonuclar):
        """Analiz raporunu özet kartları ve okunaklı rapor ile ayrı bir pencerede gösterir."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Analiz Sonuçları")
        dlg.resize(1100, 860)

        layout = QVBoxLayout(dlg)
        layout.setSpacing(16)
        layout.setContentsMargins(28, 24, 28, 24)

        # Başlık + kullanıcı özeti
        baslik = QLabel("📊 Analiz Sonuçları")
        baslik.setObjectName("baslik")
        layout.addWidget(baslik)
        cinsiyet = ['Erkek', 'Kadın'][self.saklanan_cinsiyet] if self.saklanan_cinsiyet in (0, 1) else ''
        alt = QLabel(f"{self.saklanan_ad_soyad}  •  {self.saklanan_yas} yaş  •  {self.saklanan_meslek}  •  {cinsiyet}"
                     f"  •  {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        alt.setObjectName("altBaslik")
        layout.addWidget(alt)

        # Genel karar ve özet kartları
        if genel_sonuclar:
            doru_sayisi = sum(1 for s in genel_sonuclar if s['genel_tahmin'] == 'doru')
            yalan_sayisi = sum(1 for s in genel_sonuclar if s['genel_tahmin'] == 'yalan')
            ort_guven = sum(s['genel_güven'] for s in genel_sonuclar) / len(genel_sonuclar)
            doru_kazandi = doru_sayisi > yalan_sayisi
            if doru_kazandi:
                renk, metin_renk, arka = tema.YESIL, "#4ade80", "rgba(34, 197, 94, 0.14)"
                karar_metni = "✅  GENEL KARAR: DOĞRU SÖYLÜYORSUNUZ"
            else:
                renk, metin_renk, arka = tema.KIRMIZI, "#f87171", "rgba(239, 68, 68, 0.14)"
                karar_metni = "⚠️  GENEL KARAR: YALAN SÖYLÜYORSUNUZ"
            karar = QLabel(karar_metni)
            karar.setObjectName("karar")
            karar.setAlignment(Qt.AlignCenter)
            karar.setStyleSheet(f"background: {arka}; border: 1px solid {renk}; color: {metin_renk}; "
                                f"font-size: 22px; font-weight: 700;")
            layout.addWidget(karar)

            kartlar = QHBoxLayout()
            kartlar.setSpacing(14)
            for etiket, deger, renk_k in [
                ("TOPLAM SORU", str(len(genel_sonuclar)), tema.METIN),
                ("DOĞRU", str(doru_sayisi), "#4ade80"),
                ("YALAN", str(yalan_sayisi), "#f87171"),
                ("ORT. GÜVEN", f"%{ort_guven * 100:.0f}", tema.TURKUAZ),
            ]:
                kart = QLabel(f"<div style='color:{tema.SOLUK}; font-size:11px; font-weight:700; "
                              f"letter-spacing:1px;'>{etiket}</div>"
                              f"<div style='color:{renk_k}; font-size:28px; font-weight:700;'>{deger}</div>")
                kart.setObjectName("istatKart")
                kartlar.addWidget(kart, 1)
            layout.addLayout(kartlar)

        # Ayrıntılı rapor
        text_edit = QTextEdit()
        text_edit.setHtml(tema.rapor_html(mesaj))
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit, 1)

        uyari = QLabel("Not: Yüz ifadesinden yalan tespiti bilimsel olarak kesin değildir; "
                       "sonuçlar yalnızca bir araştırma prototipinin çıktısıdır.")
        uyari.setObjectName("uyari")
        uyari.setWordWrap(True)
        layout.addWidget(uyari)

        # Butonlar
        buton_layout = QHBoxLayout()
        buton_layout.setSpacing(12)
        buton_layout.addStretch()
        kapat = QPushButton("Kapat")
        kapat.setObjectName("ikincil")
        kapat.setMinimumWidth(130)
        kapat.clicked.connect(dlg.accept)
        buton_layout.addWidget(kapat)
        kaydet = QPushButton("💾  Sonuçları Kaydet")
        kaydet.setObjectName("basari")
        kaydet.setMinimumWidth(190)
        kaydet.clicked.connect(lambda: self.sonuclari_kaydet(mesaj))
        buton_layout.addWidget(kaydet)
        layout.addLayout(buton_layout)

        dlg.exec_()

    def sonuclari_kaydet(self, mesaj):
        """Analiz sonuçlarını dosyaya kaydeder"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"yalan_tespit_sonuclari_{timestamp}.txt"
            
            # HTML etiketlerini temizle
            import re
            clean_text = re.sub(r'<[^>]+>', '', mesaj)
            clean_text = clean_text.replace('&nbsp;', ' ')
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("KAPSAMLI YALAN TESPİT ANALİZİ\n")
                f.write("="*50 + "\n\n")
                f.write(f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
                f.write(f"Kullanıcı: {self.saklanan_ad_soyad}\n")
                f.write(f"Yaş: {self.saklanan_yas}\n")
                f.write(f"Meslek: {self.saklanan_meslek}\n")
                f.write(f"Cinsiyet: {['Erkek', 'Kadın'][self.saklanan_cinsiyet]}\n\n")
                f.write(clean_text)
            
            QMessageBox.information(self, "Başarılı", f"Sonuçlar '{filename}' dosyasına kaydedildi!")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Sonuçlar kaydedilirken hata oluştu: {str(e)}")

    def kamera_kayit_baslat(self):
        if not self.kamera_kayit_aktif and not self.kayit_durduruldu:
            self.kamera_kayit_aktif = True
            self.kayit_durduruldu = False
            
            # Kamera thread'ini başlat
            self.kamera_thread = QThread()
            self.kamera_thread.run = self.kamera_dongusu
            self.kamera_thread.start()
            
            # Kayıt thread'ini başlat
            self.kayit_thread = QThread()
            self.kayit_thread.run = self.kayit_dongusu
            self.kayit_thread.start()

    def kamera_dongusu(self):
        try:
            # Mevcut kamera nesnesini kullan
            if not hasattr(self, 'cap') or self.cap is None:
                self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # DirectShow backend kullan
                if not self.cap.isOpened():
                    # Alternatif kamera indekslerini dene
                    for i in [1, 2]:
                        self.cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                        if self.cap.isOpened():
                            break
            
            if not self.cap.isOpened():
                print("Hiçbir kamera bulunamadı!")
                return
            
            # Kamera ayarlarını optimize et
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            frame_count = 0
            while self.kamera_kayit_aktif and not self.kayit_durduruldu:
                try:
                    ret, frame = self.cap.read()
                    if ret and frame is not None:
                        # Görüntüyü işle ve göster
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        h, w, ch = rgb_frame.shape
                        bytes_per_line = ch * w
                        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                        pixmap = QPixmap.fromImage(qt_image)
                        scaled_pixmap = pixmap.scaled(self.kamera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.kamera_label.setPixmap(scaled_pixmap)
                        
                        # Her 3 frame'de bir mikro ifade analizi yap (performans için)
                        frame_count += 1
                        if frame_count % 3 == 0:
                            try:
                                sonuc = DeepFace.analyze(rgb_frame, actions=['emotion'], enforce_detection=False)
                                if sonuc and len(sonuc) > 0:
                                    duygu_vektor = self.duygu_vektor(sonuc[0]['emotion'])
                                    if hasattr(self, 'aktif_soru_index') and self.aktif_soru_index is not None:
                                        if self.aktif_soru_index < len(self.mikro_ifade_sonuclari):
                                            self.mikro_ifade_sonuclari[self.aktif_soru_index].append(duygu_vektor)
                            except Exception as e:
                                # DeepFace hatalarını sessizce geç
                                pass
                    else:
                        # Frame alınamadıysa kısa bekle
                        QThread.msleep(50)
                        
                except Exception as e:
                    print(f"Kamera döngüsü hatası: {e}")
                    QThread.msleep(100)
                
                QThread.msleep(30)  # 30ms bekle (yaklaşık 30 FPS)
            
        except Exception as e:
            print(f"Kamera thread başlatma hatası: {e}")
        finally:
            # Kamera nesnesini kapatma - ana fonksiyonda yapılacak
            pass

    def kayit_dongusu(self):
        while self.kamera_kayit_aktif:
            if self.test_basladi and not self.test_durduruldu and self.aktif_soru_index is not None:
                try:
                    if self.cap and self.cap.isOpened():
                        ret, frame = self.cap.read()
                        if ret and frame is not None:
                            analiz = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                            if analiz and len(analiz) > 0:
                                duygu_vektor = self.duygu_vektor(analiz[0]['emotion'])
                                self.mikro_ifade_sonuclari[self.aktif_soru_index].append(duygu_vektor)
                except Exception as e:
                    # DeepFace hatalarını sessizce geç
                    pass
            QThread.msleep(100)  # 100ms bekle

    def kamera_kayit_durdur(self):
        """Kamera kaydını güvenli şekilde durdur"""
        try:
            self.kamera_kayit_aktif = False
            self.kayit_durduruldu = True
            
            # Thread'leri bekle
            if self.kamera_thread and self.kamera_thread.isRunning():
                self.kamera_thread.wait(2000)  # 2 saniye bekle
            
            if self.kayit_thread and self.kayit_thread.isRunning():
                self.kayit_thread.wait(2000)  # 2 saniye bekle
                
        except Exception as e:
            print(f"Kamera kayıt durdurma hatası: {e}")

    def demo_referans_grup_analiz(self):
        """Demo.png'deki yüzleri 8'erli gruplara ayırıp, yalan/doru referans vektörleri oluşturur ve kullanıcıya en yakın olanı bulur."""
        demo_analizler = self.demo_gorsel_analiz()
        if not demo_analizler:
            return None
        # 8'erli gruplara ayır
        gruplar = [demo_analizler[i:i+8] for i in range(0, len(demo_analizler), 8)]
        # Etiketler: 0,1,2,6 -> yalan; 3,4,5 -> doru
        yalan_vektorler = []
        doru_vektorler = []
        for idx, grup in enumerate(gruplar):
            for analiz in grup:
                vektor = analiz['vektor']
                if idx in [0,1,2,6]:
                    yalan_vektorler.append(vektor)
                elif idx in [3,4,5]:
                    doru_vektorler.append(vektor)
        if not yalan_vektorler or not doru_vektorler:
            return None
        yalan_ref = np.mean(np.array(yalan_vektorler), axis=0)
        doru_ref = np.mean(np.array(doru_vektorler), axis=0)
        kullanici_ort_vektor = self.kullanici_ortalama_vektor()
        if kullanici_ort_vektor is None:
            return None
        yalan_benzerlik = self.dagilim_benzerligi_hesapla(kullanici_ort_vektor, yalan_ref)
        doru_benzerlik = self.dagilim_benzerligi_hesapla(kullanici_ort_vektor, doru_ref)
        if yalan_benzerlik > doru_benzerlik:
            etik = 'yalan'
            oran = yalan_benzerlik
        else:
            etik = 'doru'
            oran = doru_benzerlik
        return {
            'yalan_benzerlik': yalan_benzerlik,
            'doru_benzerlik': doru_benzerlik,
            'referans_etiket': etik,
            'referans_oran': oran
        }

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern görünüm için
    window = YalanTespitSistemi()
    window.show()
    sys.exit(app.exec_()) 
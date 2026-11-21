import os
import numpy as np
import pandas as pd
from deepface import DeepFace
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

print("🔍 Dataset'ten duygu vektörleri çıkarılıyor...")

duygu_etiketleri = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
veriler = []
etiketler = []
gruplar = []  # Her karenin geldiği klasör (grup bazlı train/test bölmesi için)

# Dataset klasörlerini dinamik olarak bul
dataset_path = "dataset/1"
if not os.path.exists(dataset_path):
    print(f"❌ Dataset klasörü bulunamadı: {dataset_path}")
    exit()

# Mevcut soruları bul
mevcut_sorular = set()
for item in os.listdir(dataset_path):
    if item.startswith("soru") and ("_dogru" in item or "_yalan" in item):
        soru_no = item.split("_")[0].replace("soru", "")
        mevcut_sorular.add(int(soru_no))

if not mevcut_sorular:
    print("❌ Hiç soru klasörü bulunamadı!")
    exit()

print(f"📊 Bulunan sorular: {sorted(mevcut_sorular)}")

# Her soru için doğru ve yalan klasörlerini tara
for soru_no in sorted(mevcut_sorular):
    print(f"\n📊 Soru {soru_no} işleniyor...")
    
    for durum, label in [('dogru', 0.0), ('yalan', 1.0)]:
        klasor = f'dataset/1/soru{soru_no}_{durum}'
        
        if not os.path.exists(klasor):
            print(f"   ⚠️ Klasör bulunamadı: {klasor}")
            continue
            
        print(f"   📁 {klasor} analiz ediliyor...")
        dosyalar = [f for f in os.listdir(klasor) if f.endswith('.jpg')]
        
        if not dosyalar:
            print(f"   ⚠️ Hiç görüntü dosyası bulunamadı: {klasor}")
            continue
        
        for dosya in tqdm(dosyalar, desc=f"   {durum}"):
            img_path = os.path.join(klasor, dosya)
            try:
                # DeepFace ile duygu analizi
                result = DeepFace.analyze(img_path, actions=['emotion'], enforce_detection=False)
                
                if isinstance(result, list):
                    emotion_scores = result[0]['emotion']
                else:
                    emotion_scores = result['emotion']
                
                # Duygu vektörünü oluştur
                vektor = [emotion_scores.get(e, 0) for e in duygu_etiketleri]
                
                # Veriyi normalize et (0-1 arası)
                vektor = np.array(vektor) / 100.0
                
                veriler.append(vektor)
                etiketler.append(label)
                gruplar.append(f"soru{soru_no}_{durum}")
                
            except Exception as e:
                print(f"   ❌ Hata: {img_path} - {e}")
                continue

print(f"\n✅ Toplam {len(veriler)} veri noktası toplandı!")

if len(veriler) == 0:
    print("❌ Hiç veri toplanamadı!")
    exit()

# DataFrame oluştur
df = pd.DataFrame(veriler, columns=duygu_etiketleri)
df['yalan_orani'] = etiketler
df['grup'] = gruplar

# İstatistikler
print(f"\n📈 Veri Dağılımı:")
print(f"   Doğru söyleyenler: {sum(1 for x in etiketler if x == 0.0)}")
print(f"   Yalan söyleyenler: {sum(1 for x in etiketler if x == 1.0)}")
print(f"   Toplam soru sayısı: {len(mevcut_sorular)}")

# Veriyi kaydet
df.to_csv('egitim_verisi_regresyon.csv', index=False)
print(f"\n💾 Veri kaydedildi: egitim_verisi_regresyon.csv")

# Veri önizleme
print(f"\n🔍 Veri Önizleme:")
print(df.head())
print(f"\n📊 Veri Şekli: {df.shape}")
print(f"📊 Yalan Oranı Ortalaması: {df['yalan_orani'].mean():.3f}")

# Soru bazında istatistikler
print(f"\n📊 Soru Bazında Veri Dağılımı:")
for soru_no in sorted(mevcut_sorular):
    dogru_klasor = f'dataset/1/soru{soru_no}_dogru'
    yalan_klasor = f'dataset/1/soru{soru_no}_yalan'
    
    dogru_sayisi = len([f for f in os.listdir(dogru_klasor) if f.endswith('.jpg')]) if os.path.exists(dogru_klasor) else 0
    yalan_sayisi = len([f for f in os.listdir(yalan_klasor) if f.endswith('.jpg')]) if os.path.exists(yalan_klasor) else 0
    
    print(f"   Soru {soru_no}: {dogru_sayisi} doğru, {yalan_sayisi} yalan") 
import json
from database import Session, Kelime

def json_dan_yukle(dosya_adi='kelimeler.json'):
    """JSON dosyasından kelimeleri veritabanına yükler"""
    session = Session()
    
    try:
        with open(dosya_adi, 'r', encoding='utf-8') as file:
            kelimeler = json.load(file)
        
        # Mevcut kelimeleri kontrol et
        mevcut_kelimeler = set((k.turkce, k.ingilizce) for k in session.query(Kelime).all())
        
        eklenen = 0
        for kelime in kelimeler:
            # JSON formatını kontrol et
            if not all(key in kelime for key in ['turkce', 'ingilizce', 'zorluk']):
                print(f"Hatalı kelime formatı: {kelime}")
                continue
                
            # Kelime zaten var mı kontrol et
            if (kelime['turkce'], kelime['ingilizce']) not in mevcut_kelimeler:
                yeni_kelime = Kelime(
                    turkce=kelime['turkce'],
                    ingilizce=kelime['ingilizce'],
                    zorluk=int(kelime['zorluk'])
                )
                session.add(yeni_kelime)
                eklenen += 1
        
        session.commit()
        print(f"Toplam {eklenen} yeni kelime eklendi.")
        
    except FileNotFoundError:
        print(f"'{dosya_adi}' dosyası bulunamadı!")
    except json.JSONDecodeError:
        print("JSON dosyası hatalı!")
    except Exception as e:
        print(f"Bir hata oluştu: {str(e)}")
    finally:
        session.close()

def kelimeleri_jsona_aktar(dosya_adi='kelimeler.json'):
    """Veritabanındaki kelimeleri JSON dosyasına aktarır"""
    session = Session()
    
    try:
        kelimeler = session.query(Kelime).all()
        
        kelime_listesi = [
            {
                'turkce': kelime.turkce,
                'ingilizce': kelime.ingilizce,
                'zorluk': kelime.zorluk
            }
            for kelime in kelimeler
        ]
        
        with open(dosya_adi, 'w', encoding='utf-8') as file:
            json.dump(kelime_listesi, file, ensure_ascii=False, indent=2)
            
        print(f"Toplam {len(kelime_listesi)} kelime JSON dosyasına aktarıldı.")
        
    except Exception as e:
        print(f"Bir hata oluştu: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    # Örnek kullanım
    json_dan_yukle()
    # veya
    # kelimeleri_jsona_aktar() 
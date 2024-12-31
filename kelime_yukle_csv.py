import csv
from database import Session, Kelime

def csv_den_yukle(dosya_adi='kelimeler.csv'):
    session = Session()
    
    with open(dosya_adi, 'r', encoding='utf-8') as file:
        csv_okuyucu = csv.reader(file)
        next(csv_okuyucu)  # başlık satırını atla
        
        for row in csv_okuyucu:
            turkce, ingilizce, zorluk = row
            yeni_kelime = Kelime(
                turkce=turkce,
                ingilizce=ingilizce,
                zorluk=int(zorluk)
            )
            session.add(yeni_kelime)
    
    session.commit()
    session.close()
    print("CSV'den kelimeler yüklendi!") 

    
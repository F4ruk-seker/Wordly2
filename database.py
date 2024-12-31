from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class Kelime(Base):
    __tablename__ = 'kelimeler'
    
    id = Column(Integer, primary_key=True)
    turkce = Column(String(100), nullable=False)
    ingilizce = Column(String(100), nullable=False)
    zorluk = Column(Integer, nullable=False)  # 1-9 arası zorluk seviyeleri
    
    def __repr__(self):
        return f"<Kelime(turkce='{self.turkce}', ingilizce='{self.ingilizce}', zorluk={self.zorluk})>"

# Veritabanı bağlantısını oluştur
engine = create_engine('sqlite:///kelime_oyunu.db', echo=False)

# Tabloları oluştur
Base.metadata.create_all(engine)

# Session oluşturucu
Session = sessionmaker(bind=engine)

# Örnek kullanım fonksiyonları
def kelime_ekle(turkce, ingilizce, zorluk) -> None:
    session = Session()
    yeni_kelime = Kelime(turkce=turkce, ingilizce=ingilizce, zorluk=zorluk)
    session.add(yeni_kelime)
    session.commit()
    session.close()

def zorluk_seviyesine_gore_getir(zorluk) -> list[Kelime]:
    session = Session()
    kelimeler = session.query(Kelime).filter(Kelime.zorluk == zorluk).all()
    session.close()
    return kelimeler

def tum_kelimeleri_getir() -> list[Kelime]:
    session = Session()
    kelimeler = session.query(Kelime).all()
    session.close()
    return kelimeler 

def rastgele_kelime_getir(zorluk) -> Kelime:
    """Belirli zorluk seviyesinden rastgele bir kelime getirir"""
    session = Session()
    kelime = session.query(Kelime)\
        .filter(Kelime.zorluk == zorluk)\
        .order_by(func.random())\
        .first()
    session.close()
    return kelime

def rastgele_kelimeler_getir(zorluk, adet=5) -> list[Kelime]:
    """Belirli zorluk seviyesinden belirtilen sayıda rastgele kelime getirir"""
    session = Session()
    kelimeler = session.query(Kelime)\
        .filter(Kelime.zorluk == zorluk)\
        .order_by(func.random())\
        .limit(adet)\
        .all()
    session.close()
    return kelimeler 

def rastgele_siklar_getir(dogru_kelime, zorluk, sik_sayisi=4) -> dict:
    """Doğru cevap dışında rastgele şıklar getirir"""
    session = Session()
    
    # Doğru cevap dışındaki tüm kelimeleri al
    yanlis_kelimeler = session.query(Kelime.ingilizce)\
        .filter(Kelime.id != dogru_kelime.id)\
        .order_by(func.random())\
        .limit(sik_sayisi)\
        .all()
    
    session.close()
    
    # Şıkları liste olarak hazırla
    siklar = [kelime[0] for kelime in yanlis_kelimeler]
    
    # Doğru cevabı rastgele bir konuma yerleştir
    from random import randint
    dogru_cevap_konumu = randint(0, sik_sayisi)
    siklar.insert(dogru_cevap_konumu, dogru_kelime.ingilizce)
    
    return {
        'siklar': siklar,
        'dogru_cevap_index': dogru_cevap_konumu
    }

def soru_olustur(zorluk) -> dict:
    """Belirli zorlukta bir soru oluşturur"""
    # Önce rastgele bir kelime seç
    dogru_kelime = rastgele_kelime_getir(zorluk)
    if not dogru_kelime:
        return None
    
    # Şıkları oluştur
    sik_bilgileri = rastgele_siklar_getir(dogru_kelime, zorluk)
    
    return {
        'soru': dogru_kelime.turkce,
        'dogru_cevap': dogru_kelime.ingilizce,
        'siklar': sik_bilgileri['siklar'],
        'dogru_cevap_index': sik_bilgileri['dogru_cevap_index']
    } 
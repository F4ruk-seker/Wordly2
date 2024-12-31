import pygame
import random
import time
import os
from database import Session, Kelime, kelime_ekle, rastgele_kelimeler_getir, soru_olustur

# Pygame'i başlat
pygame.init()
pygame.mixer.init()  # Ses sistemini başlat

ASSETS_DIR = "assets"


# Ekran ayarları - Tam ekran
ekran_bilgisi = pygame.display.Info()
GENISLIK = ekran_bilgisi.current_w
YUKSEKLIK = ekran_bilgisi.current_h
ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK), pygame.FULLSCREEN)
pygame.display.set_caption("Kelime Ezberleme Oyunu")

# # Arka plan resmini yükle
# bg_path = os.path.join(ASSETS_DIR, "bg.png")
# bg_image = pygame.image.load(bg_path)
# bg_image = pygame.transform.scale(bg_image, (GENISLIK, YUKSEKLIK))  # Ekran boyutuna ölçekle

# Renkler
BEYAZ = (255, 255, 255)
SIYAH = (0, 0, 0)
MAVI = (0, 0, 255)

# Yazı tipi
font = pygame.font.Font(None, 48)
soru_font = pygame.font.Font(None, 72)

# # Kelime listesi
# kelimeler = [
#     ("apple", "elma"),
#     ("book", "kitap"),
#     ("house", "ev"),
#     ("car", "araba"),
#     ("sun", "güneş"),
#     # Daha fazla kelime ekleyebilirsiniz
# ]

# Buton ayarları ekleyelim
BUTON_GENISLIK = 500
BUTON_YUKSEKLIK = 60
BUTON_BOSLUK = 20
BUTON_RENK = (220, 220, 220)
BUTON_SECILI_RENK = (180, 180, 180)

# Mevcut sabitlere eklenecek yeni sabitler
AYARLAR_BUTON_BOYUT = 40
AYARLAR_MENU_GENISLIK = 550
AYARLAR_MENU_YUKSEKLIK = 500
SLIDER_GENISLIK = 300
SLIDER_YUKSEKLIK = 20
SLIDER_RENK = (180, 180, 180)
SLIDER_AKTIF_RENK = (100, 100, 255)
ARKAPLAN_ONIZLEME_BOYUT = 100  # Yeni eklenen sabit

# Buton sabitlerine ekle
TAMAM_BUTON_GENISLIK = 120
TAMAM_BUTON_YUKSEKLIK = 40

# Global değişkenler
zorluk_seviyesi = 5  # 1-9 arası
ses_seviyesi = 0.1   # 0.0-1.0 arası
ayarlar_acik = False

# Global değişkenlere ekle
ARKAPLAN_LISTESI = ["bg1", "bg2", "bg3", "bg4"]
secili_arkaplan = random.choice(ARKAPLAN_LISTESI)  # Rastgele bir arka plan seç

# Arka plan yükleme fonksiyonu ekle
def arkaplan_yukle(bg_name):
    bg_path = os.path.join(ASSETS_DIR, f"{bg_name}.png")
    original_image = pygame.image.load(bg_path)
    
    # Orijinal resmin ve ekranın en-boy oranlarını hesapla
    image_ratio = original_image.get_width() / original_image.get_height()
    screen_ratio = GENISLIK / YUKSEKLIK
    
    if screen_ratio > image_ratio:  # Ekran daha geniş
        yeni_genislik = GENISLIK
        yeni_yukseklik = int(GENISLIK / image_ratio)
        y_offset = (yeni_yukseklik - YUKSEKLIK) // 2
        x_offset = 0
    else:  # Ekran daha dar veya eşit
        yeni_yukseklik = YUKSEKLIK
        yeni_genislik = int(YUKSEKLIK * image_ratio)
        x_offset = (yeni_genislik - GENISLIK) // 2
        y_offset = 0
    
    # Resmi yeni boyutlara ölçekle
    scaled_image = pygame.transform.scale(original_image, (yeni_genislik, yeni_yukseklik))
    
    # Yeni bir yüzey oluştur ve ölçeklenmiş resmi ortala
    final_surface = pygame.Surface((GENISLIK, YUKSEKLIK))
    final_surface.blit(scaled_image, (-x_offset, -y_offset))
    
    return final_surface

# Müzik dosyasını yükle ve çal
muzik_yolu = os.path.join(ASSETS_DIR, "bg_music.mp3")
pygame.mixer.music.load(muzik_yolu)
pygame.mixer.music.play(-1)  # -1 parametresi sonsuz döngü için
pygame.mixer.music.set_volume(ses_seviyesi)


def metin_wrap(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        test_surface = font.render(test_line, True, SIYAH)
        
        if test_surface.get_width() <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def buton_ciz(ekran, text, x, y, width, height, harf, secili=False):
    # Buton arka planı
    renk = BUTON_SECILI_RENK if secili else BUTON_RENK
    pygame.draw.rect(ekran, renk, (x, y, width, height), border_radius=10)
    pygame.draw.rect(ekran, SIYAH, (x, y, width, height), 2, border_radius=10)
    
    # Metni satırlara böl
    metin_satirlar = metin_wrap(f"{harf}) {text}", font, width - 20)
    
    # Her satırı ayrı ayrı çiz
    toplam_yukseklik = len(metin_satirlar) * font.get_linesize()
    baslangic_y = y + (height - toplam_yukseklik) // 2
    
    for i, satir in enumerate(metin_satirlar):
        text_surface = font.render(satir, True, SIYAH)
        text_rect = text_surface.get_rect(
            left=x + 10,
            top=baslangic_y + (i * font.get_linesize())
        )
        ekran.blit(text_surface, text_rect)
    
    return pygame.Rect(x, y, width, height)

def kelime_goster(kelime, puan, secenekler=None):
    # Arka plan resmini çiz
    ekran.blit(bg_image, (0, 0))
    
    # Kelimeyi göster
    kelime_yazisi = soru_font.render(kelime, True, SIYAH)
    kelime_rect = kelime_yazisi.get_rect(center=(GENISLIK/2, YUKSEKLIK/4))
    
    # Kelime için beyaz arka plan ekle
    pygame.draw.rect(ekran, BEYAZ, 
                    (kelime_rect.x - 20, kelime_rect.y - 10, 
                     kelime_rect.width + 40, kelime_rect.height + 20))
    ekran.blit(kelime_yazisi, kelime_rect)
    
    # Puanı göster
    puan_yazisi = font.render(f"Puan: {puan}", True, MAVI)
    puan_rect = puan_yazisi.get_rect(topleft=(10, 10))
    
    # Puan için beyaz arka plan ekle
    pygame.draw.rect(ekran, BEYAZ, 
                    (puan_rect.x - 5, puan_rect.y - 5, 
                     puan_rect.width + 10, puan_rect.height + 10))
    ekran.blit(puan_yazisi, puan_rect)
    
    # Şıkları buton olarak göster
    buton_rects = []
    if secenekler:
        for i, secenek in enumerate(secenekler):
            x = (GENISLIK - BUTON_GENISLIK) // 2
            y = (YUKSEKLIK//2 - 50) + (BUTON_YUKSEKLIK + BUTON_BOSLUK) * i
            buton_rect = buton_ciz(ekran, secenek, x, y, BUTON_GENISLIK, BUTON_YUKSEKLIK, chr(65+i))
            buton_rects.append(buton_rect)
    
    # Ayarlar butonunu çiz
    ayarlar_rect = ayarlar_buton_ciz(ekran)
    
    pygame.display.flip()
    return buton_rects, ayarlar_rect

def karistir_secenekler(dogru_cevap, kelimeler):
    # Doğru cevap dışındaki kelimelerin Türkçelerini al
    diger_kelimeler = [kelime[1] for kelime in kelimeler if kelime[1] != dogru_cevap]
    # Rastgele 3 yanlış şık seç
    yanlis_siklar = random.sample(diger_kelimeler, 3)
    # Tüm şıkları birleştir ve karıştır
    tum_siklar = [dogru_cevap] + yanlis_siklar
    random.shuffle(tum_siklar)
    return tum_siklar

def ayarlar_buton_ciz(ekran):
    # Sağ üst köşeye dişli çark ikonu çiz
    ayarlar_rect = pygame.Rect(
        GENISLIK - AYARLAR_BUTON_BOYUT - 10,
        10,
        AYARLAR_BUTON_BOYUT,
        AYARLAR_BUTON_BOYUT
    )
    pygame.draw.rect(ekran, BUTON_RENK, ayarlar_rect, border_radius=5)
    pygame.draw.rect(ekran, SIYAH, ayarlar_rect, 2, border_radius=5)
    
    # Dişli çark simgesi için basit bir metin kullan
    ayarlar_font = pygame.font.Font(None, 30)
    ayarlar_text = ayarlar_font.render("⚙", True, SIYAH)
    text_rect = ayarlar_text.get_rect(center=ayarlar_rect.center)
    ekran.blit(ayarlar_text, text_rect)
    
    return ayarlar_rect

def slider_ciz(ekran, x, y, width, deger, min_deger, max_deger, baslik):
    # Slider başlığı
    baslik_font = pygame.font.Font(None, 36)
    baslik_text = baslik_font.render(baslik, True, SIYAH)
    ekran.blit(baslik_text, (x, y - 30))
    
    # Slider arka planı
    pygame.draw.rect(ekran, SLIDER_RENK, (x, y, width, SLIDER_YUKSEKLIK))
    
    # Slider değeri
    deger_oran = (deger - min_deger) / (max_deger - min_deger)
    slider_pos = x + (width * deger_oran)
    
    # Aktif kısmı çiz
    pygame.draw.rect(ekran, SLIDER_AKTIF_RENK, 
                    (x, y, slider_pos - x, SLIDER_YUKSEKLIK))
    
    # Slider düğmesi
    pygame.draw.circle(ekran, SIYAH, (int(slider_pos), y + SLIDER_YUKSEKLIK//2), 10)
    
    # Değeri göster
    deger_text = baslik_font.render(str(deger), True, SIYAH)
    ekran.blit(deger_text, (x + width + 10, y))
    
    return pygame.Rect(x, y - 10, width, SLIDER_YUKSEKLIK + 20)

def ayarlar_menu_ciz(ekran, ilk_cizim=False):
    global zorluk_seviyesi, ses_seviyesi, secili_arkaplan, bg_image
    
    if ilk_cizim:
        overlay = pygame.Surface((GENISLIK, YUKSEKLIK))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        ekran.blit(overlay, (0, 0))
    
    menu_x = (GENISLIK - AYARLAR_MENU_GENISLIK) // 2
    menu_y = (YUKSEKLIK - AYARLAR_MENU_YUKSEKLIK) // 2
    menu_rect = pygame.Rect(menu_x, menu_y, AYARLAR_MENU_GENISLIK, AYARLAR_MENU_YUKSEKLIK)
    
    pygame.draw.rect(ekran, BEYAZ, menu_rect)
    pygame.draw.rect(ekran, SIYAH, menu_rect, 2)
    
    # Başlık
    baslik_font = pygame.font.Font(None, 48)
    baslik = baslik_font.render("Ayarlar", True, SIYAH)
    baslik_rect = baslik.get_rect(centerx=menu_x + AYARLAR_MENU_GENISLIK//2, top=menu_y + 20)
    ekran.blit(baslik, baslik_rect)
    
    # Sliderlar (mevcut)
    zorluk_slider = slider_ciz(ekran, menu_x + 50, menu_y + 100, SLIDER_GENISLIK, 
                             zorluk_seviyesi, 1, 9, "Zorluk Seviyesi")
    ses_slider = slider_ciz(ekran, menu_x + 50, menu_y + 180, SLIDER_GENISLIK,
                          int(ses_seviyesi * 100), 0, 100, "Ses Seviyesi")
    
    # Arka plan seçimi başlığı
    arkaplan_baslik = baslik_font.render("Arka Plan Seçimi", True, SIYAH)
    ekran.blit(arkaplan_baslik, (menu_x + 50, menu_y + 260))
    
    # Arka plan ön izlemeleri
    arkaplan_rects = []
    for i, bg in enumerate(["bg1", "bg2", "bg3", "bg4"]):
        x = menu_x + 50 + (i * (ARKAPLAN_ONIZLEME_BOYUT + 20))
        y = menu_y + 300
        
        # Ön izleme çerçevesi
        preview_rect = pygame.Rect(x, y, ARKAPLAN_ONIZLEME_BOYUT, ARKAPLAN_ONIZLEME_BOYUT)
        pygame.draw.rect(ekran, SIYAH, preview_rect, 2)
        
        # Ön izleme görüntüsü
        preview_img = pygame.image.load(os.path.join(ASSETS_DIR, f"{bg}.png"))
        preview_img = pygame.transform.scale(preview_img, (ARKAPLAN_ONIZLEME_BOYUT-4, ARKAPLAN_ONIZLEME_BOYUT-4))
        ekran.blit(preview_img, (x+2, y+2))
        
        # Seçili arka planı belirt
        if bg == secili_arkaplan:
            pygame.draw.rect(ekran, MAVI, preview_rect, 4)
        
        arkaplan_rects.append((preview_rect, bg))
    
    # Tamam butonu
    tamam_x = menu_x + (AYARLAR_MENU_GENISLIK - TAMAM_BUTON_GENISLIK) // 2
    tamam_y = menu_y + AYARLAR_MENU_YUKSEKLIK - TAMAM_BUTON_YUKSEKLIK - 20
    tamam_rect = pygame.Rect(tamam_x, tamam_y, TAMAM_BUTON_GENISLIK, TAMAM_BUTON_YUKSEKLIK)
    
    pygame.draw.rect(ekran, BUTON_RENK, tamam_rect, border_radius=5)
    pygame.draw.rect(ekran, SIYAH, tamam_rect, 2, border_radius=5)
    
    tamam_font = pygame.font.Font(None, 36)
    tamam_text = tamam_font.render("Tamam", True, SIYAH)
    tamam_text_rect = tamam_text.get_rect(center=tamam_rect.center)
    ekran.blit(tamam_text, tamam_text_rect)
    
    return zorluk_slider, ses_slider, tamam_rect, arkaplan_rects

def main():
    global ayarlar_acik, zorluk_seviyesi, ses_seviyesi, secili_arkaplan, bg_image
    oyun_aktif = True
    puan = 0
    
    # Başlangıçta rastgele seçilen arka planı yükle
    bg_image = arkaplan_yukle(secili_arkaplan)
    
    # Veritabanından ilk soruyu al
    soru_verisi = soru_olustur(zorluk_seviyesi)
    ingilizce = soru_verisi['soru']
    turkce = soru_verisi['dogru_cevap']
    secenekler = soru_verisi['siklar']
    dogru_sik_index = soru_verisi['dogru_cevap_index']
    
    # İlk ekran çizimi
    buton_rects, ayarlar_rect = kelime_goster(ingilizce, puan, secenekler)
    
    while oyun_aktif:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                oyun_aktif = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if not ayarlar_acik:
                    # Ayarlar butonu kontrolü
                    if ayarlar_rect.collidepoint(mouse_pos):
                        ayarlar_acik = True
                        zorluk_slider, ses_slider, tamam_rect, arkaplan_rects = ayarlar_menu_ciz(ekran, ilk_cizim=True)
                        pygame.display.flip()
                        continue
                    
                    # Şık seçme kontrolü
                    for i, rect in enumerate(buton_rects):
                        if rect.collidepoint(mouse_pos):
                            # Seçilen butonu vurgula
                            kelime_goster(turkce, puan, secenekler)
                            buton_ciz(ekran, secenekler[i], 
                                    rect.x, rect.y,
                                    BUTON_GENISLIK, BUTON_YUKSEKLIK,
                                    chr(65+i), True)
                            ayarlar_rect = ayarlar_buton_ciz(ekran)
                            pygame.display.flip()
                            
                            if i == dogru_sik_index:
                                puan += 10
                                sonuc_mesaji = "Doğru!"
                                bekleme_suresi = 1000  # 1 saniye
                            else:
                                puan -= 5
                                sonuc_mesaji = f"Yanlış! Doğru cevap: {turkce}"
                                bekleme_suresi = 2000  # 2 saniye
                            
                            # Sonucu göster
                            sonuc_yazisi = font.render(sonuc_mesaji, True, MAVI)
                            sonuc_rect = sonuc_yazisi.get_rect(center=(GENISLIK/2, YUKSEKLIK-50))

                            # Beyaz arka plan ekle
                            pygame.draw.rect(ekran, BEYAZ, 
                                            (sonuc_rect.x - 10, sonuc_rect.y - 5, 
                                             sonuc_rect.width + 20, sonuc_rect.height + 10))
                            ekran.blit(sonuc_yazisi, sonuc_rect)
                            pygame.display.flip()
                            
                            # Belirlenen süre kadar bekle
                            pygame.time.wait(bekleme_suresi)
                            
                            # Yeni soru hazırla
                            soru_verisi = soru_olustur(zorluk_seviyesi)
                            ingilizce = soru_verisi['soru']
                            turkce = soru_verisi['dogru_cevap']
                            secenekler = soru_verisi['siklar']
                            dogru_sik_index = soru_verisi['dogru_cevap_index']
                            
                            # Yeni soruyu göster
                            buton_rects, ayarlar_rect = kelime_goster(ingilizce, puan, secenekler)  # ayarlar_rect'i güncelle
                
                else:
                    # Ayarlar menüsü kontrolleri
                    if tamam_rect.collidepoint(mouse_pos):
                        ayarlar_acik = False
                        # Yeni zorluk seviyesiyle yeni soru al
                        soru_verisi = soru_olustur(zorluk_seviyesi)
                        ingilizce = soru_verisi['soru']
                        turkce = soru_verisi['dogru_cevap']
                        secenekler = soru_verisi['siklar']
                        dogru_sik_index = soru_verisi['dogru_cevap_index']
                        # Ekranı güncelle
                        buton_rects, ayarlar_rect = kelime_goster(ingilizce, puan, secenekler)
                        pygame.display.flip()
                        continue
                    
                    # Slider kontrolleri
                    if zorluk_slider.collidepoint(mouse_pos):
                        zorluk_seviyesi = round((mouse_pos[0] - zorluk_slider.x) / 
                                               zorluk_slider.width * 8 + 1)
                        zorluk_seviyesi = max(1, min(9, zorluk_seviyesi))
                        zorluk_slider, ses_slider, tamam_rect, arkaplan_rects = ayarlar_menu_ciz(ekran, ilk_cizim=False)
                        pygame.display.flip()
                    
                    elif ses_slider.collidepoint(mouse_pos):
                        ses_seviyesi = (mouse_pos[0] - ses_slider.x) / ses_slider.width
                        ses_seviyesi = max(0, min(1, ses_seviyesi))
                        pygame.mixer.music.set_volume(ses_seviyesi)
                        zorluk_slider, ses_slider, tamam_rect, arkaplan_rects = ayarlar_menu_ciz(ekran, ilk_cizim=False)
                        pygame.display.flip()
                    
                    # Arka plan seçimi kontrolü
                    for rect, bg in arkaplan_rects:
                        if rect.collidepoint(mouse_pos):
                            secili_arkaplan = bg
                            bg_image = arkaplan_yukle(bg)
                            zorluk_slider, ses_slider, tamam_rect, arkaplan_rects = ayarlar_menu_ciz(ekran, ilk_cizim=False)
                            pygame.display.flip()
                            break

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if ayarlar_acik:
                        ayarlar_acik = False
                        buton_rects, ayarlar_rect = kelime_goster(ingilizce, puan, secenekler)
                    else:
                        oyun_aktif = False

    pygame.quit()

if __name__ == "__main__":
    main()

import requests
from urllib.parse import urlparse
from flask import json

from bs4 import BeautifulSoup

def get_holding_links():
    # Wikipedia sayfasının URL'si
    url = "https://tr.wikipedia.org/wiki/T%C3%BCrkiye%27deki_holding_%C5%9Firketler"

    # Sayfanın içeriğini çek
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Türkiye'deki holding şirketler listesini bul
    list_section = soup.find("span", id="Türkiye'deki_holding_şirketler_listesi").parent

    # Sonraki tüm <ul> listelerini al
    for ul in list_section.find_all_next("ul"):
        holding_links = ul.find_all("a")
        for link in holding_links:
            title = link.get_text()
            href = link.get('href')
            full_url = "https://tr.wikipedia.org" + href
            print(f"{title}: {full_url}")      
            english_page_link = get_english_page_link(link)        
            if english_page_link is None:
                print ("english link is none")
            else:
                print ("english link is" + english_page_link)
                subsidiaries = get_subsidiaries(english_page_link)
                if subsidiaries:
                    print("Subsidiaries:")
                    for subsidiary in subsidiaries:
                        print("subsidiary " + subsidiary)
                #else:
                    # print("No subsidiaries found or no infobox present.")

        # Eğer başka bir başlık (örn. <h2>, <h3>) gelirse, döngüyü kır
        next_tag = ul.find_next_sibling()
        if next_tag and next_tag.name in ["h2", "h3"]:
            break

def get_english_page_link(link):
    # İngilizce versiyonun URL'sinin başlangıcı
    english_url_base = "https://en.wikipedia.org/wiki/"

    # Bağlantının URL'sini al
    href = link.get('href')

    # Bağlantının tam URL'sini oluştur
    if not ("https" or "wikipedia.org") in href:
        full_url = "https://tr.wikipedia.org" + href
    else:
        full_url = href

    # Bağlantının hedef sayfasını çek
    response = requests.get(full_url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Dil seçeneklerini kontrol et
    interwiki_links = soup.find_all("a", {"class": "interlanguage-link-target"})
    for interwiki_link in interwiki_links:
        language_code = interwiki_link.get('lang')
        if language_code == 'en':
            # İngilizce versiyonu bulduk, URL'yi döndür
            #print ("İngilizce versiyonu bulduk, URL'yi döndür")
            english_page_link = interwiki_link.get('href')
            return english_page_link

    # İngilizce versiyon bulunamadı
    return None

def get_subsidiaries(english_page_url):
    # Sayfanın içeriğini çek
    response = requests.get(english_page_url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Infobox'ı bul
    infobox = soup.find("table", {"class": "infobox"})
    if not infobox:
        return None  # Infobox bulunamadı

    # Infobox'taki "subsidiaries" satırını bul
    subsidiaries_row = None
    for row in infobox.find_all("tr"):
        header = row.find("th")
        if header and "subsidiaries" in header.get_text().lower():
            subsidiaries_row = row
            break

    if not subsidiaries_row:
        return None  # "Subsidiaries" satırı bulunamadı

    # Subsidiaries listesini çıkar
    subsidiaries = []
    for item in subsidiaries_row.find("td").find_all("a"):
        subsidiaries.append(item.get_text())

    return subsidiaries

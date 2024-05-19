from flask import json
import requests
from bs4 import BeautifulSoup

def get_holding_json():
    # Wikipedia sayfasının URL'si
    url = "https://tr.wikipedia.org/wiki/T%C3%BCrkiye%27deki_holding_%C5%9Firketler"

    # Sayfa içeriğini alma
    response = requests.get(url)
    html_content = response.content

    # HTML içeriğini parse etme
    soup = BeautifulSoup(html_content, 'html.parser')

    # Holding şirketler listesini bulma
    holding_sirketler = []
    # Sayfada genellikle <ul> (unordered list) ve <li> (list item) kullanılır.
    for ul in soup.find_all('ul'):
        for li in ul.find_all('li'):
            # Burada, her <li> öğesinin metin içeriğini listeye ekliyoruz.
            holding_sirketler.append(li.get_text())

    holding_data = {}
    # Listede tekrarlayan ve gereksiz elemanları çıkarmak için set kullanabiliriz
    holding_sirketler = list(set(holding_sirketler))

    # Holding şirketler listesini yazdırma
    print("Türkiye'deki Holding Şirketler:")
    count = 0
    for holding in holding_sirketler:
        print(holding)
        holding_data[holding] = get_subsidiaries(holding)
        # Increment the counter
        print(count)
        count += 1
        # Check if 10 items have been processed
        if count == 100:
            break

    return json.dumps(holding_data, indent=3)

def get_subsidiaries(holding_name):
    # Wikipedia API URL'si
    url = "https://en.wikipedia.org/w/api.php"

    # API istek parametreleri
    params = {
        "action": "parse",
        "page": holding_name,
        "prop": "text",
        "format": "json"
    }

    # API isteği gönderme
    response = requests.get(url, params=params)
    data = response.json()

    # Sayfa var mı kontrol etme
    if 'error' in data:
        print(f"{holding_name} adında bir sayfa bulunamadı.")
        return

    # Sayfa içeriğini HTML olarak alma
    html_content = data['parse']['text']['*']
    soup = BeautifulSoup(html_content, 'html.parser')

    # 'Subsidiaries' başlığını bulma ve altındaki listeyi çekme
    subsidiaries = []
    subsidiaries_section = soup.find('span', {'id': 'Subsidiaries'})
    if subsidiaries_section:
        list_items = subsidiaries_section.find_next('ul').find_all('li')
        subsidiaries = [item.get_text() for item in list_items]
    else:
        print("Subsidiaries section not found.")

    # İştirakleri yazdırma
    print("Sabancı Holding İştirakleri:")
    for subsidiary in subsidiaries:
        print("subsidiary " + subsidiary)
    
    return subsidiaries

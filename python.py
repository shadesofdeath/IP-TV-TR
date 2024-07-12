import requests
import aiohttp
import asyncio
import re

# m3u dosyasının URL'si
url = "https://raw.githubusercontent.com/iptv-org/iptv/2718e7bcf3dc9e401b2b7908adbc1e9a18476a18/streams/tr.m3u"

# Yeni m3u dosyasının ismi
output_file = "working_streams_cleaned.m3u"

# m3u dosyasını indir ve oku
response = requests.get(url)
m3u_content = response.text

# m3u8 URL'lerini ve ilgili bilgileri bul
lines = m3u_content.splitlines()
entries = []

for i in range(len(lines)):
    if lines[i].startswith("#EXTINF:"):
        entry = lines[i] + "\n" + lines[i + 1]
        entries.append(entry)

# m3u8 bağlantılarını test et
async def check_url(session, url):
    try:
        async with session.get(url, timeout=2) as response:
            if response.status == 200:
                return url
    except:
        pass
    return None

async def check_all_urls(entries):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for entry in entries:
            url = entry.splitlines()[1]
            tasks.append(check_url(session, url))
        return await asyncio.gather(*tasks)

working_urls = asyncio.run(check_all_urls(entries))

# Çalışan bağlantıları yeni bir m3u dosyasına kaydet
with open(output_file, "w") as f:
    f.write("#EXTM3U\n")
    for i in range(len(entries)):
        if working_urls[i]:
            # Kanal ismindeki id, kalite belirten kısımlar ve notları temizle
            extinf_line = entries[i].splitlines()[0]
            cleaned_line = re.sub(r'tvg-id=".*?",', '', extinf_line)
            cleaned_line = re.sub(r'\s*\(.*?\)', '', cleaned_line)
            cleaned_line = re.sub(r'\s*\[.*?\]', '', cleaned_line)
            f.write(cleaned_line + "\n" + working_urls[i] + "\n")

print(f"{output_file} dosyasına çalışan ve temizlenmiş m3u8 bağlantıları kaydedildi.")

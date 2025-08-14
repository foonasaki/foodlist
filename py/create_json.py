import requests
from bs4 import BeautifulSoup
import time
import random
import os
import json

headers = {"User-Agent": "Mozilla/5.0"}

# 画像保存フォルダ作成
img_dir = "../images"
os.makedirs(img_dir, exist_ok=True)

# JSONデータ保存フォルダ作成
json_dir = "../json"
os.makedirs(json_dir, exist_ok=True)

# JSONデータ保存用の辞書
menu_data = {}

# for n in range(0, 5001):
for n in range(1468, 1470):
    url = f"https://www.tokyodisneyresort.jp/food/{n}/"
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200:
            print(url, "にアクセスできませんでした。")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        if "このページは存在しません" in soup.text:
            print(url, "は存在しないページです。")
            continue

        print(url, "にアクセスしました。")

        # メニュー名
        menu_name_tag = soup.find("h1", class_="heading1")
        menu_name = menu_name_tag.get_text(strip=True) if menu_name_tag else None
        if not menu_name:
            print(f"メニュー名が見つかりませんでした: {url}")
            continue

        # 価格
        price_tag = soup.find("p", class_="price")
        price = price_tag.get_text(strip=True) if price_tag else None

        # 販売店舗（複数対応、リストで格納）
        place_list = []
        place_section = soup.find("h2", class_="heading2", string="販売店舗")
        if place_section:
            link_list_div = place_section.find_next("div", class_="linkList7")
            if link_list_div:
                list_items = link_list_div.find_all("li")
                for li in list_items:
                    name_tag = li.find("h3", class_="heading3")
                    area_tag = li.find("p")
                    name = name_tag.get_text(strip=True) if name_tag else ""
                    area = area_tag.get_text(strip=True) if area_tag else ""
                    if name or area:
                        place_list.append(f"{name}（{area}）")

        # 備考
        remarks_list = soup.find_all("div", class_="definitionList")
        remarks = " / ".join([r.get_text(strip=True) for r in remarks_list]) if remarks_list else None

        # 画像情報
        image_tag = soup.find("img", src=True, alt=True)
        image_url = image_tag["src"] if image_tag else None
        image_alt = image_tag["alt"] if image_tag else None

        image_filename = None
        if image_url:
            if image_url.startswith("/"):
                image_url = "https://www.tokyodisneyresort.jp" + image_url

            ext = os.path.splitext(image_url)[1]
            safe_alt = "".join(c if c.isalnum() else "_" for c in image_alt) if image_alt else f"{n}_image"
            image_filename = f"{n}_{safe_alt}{ext}"

            try:
                img_data = requests.get(image_url, headers=headers, timeout=10).content
                with open(os.path.join(img_dir, image_filename), "wb") as img_file:
                    img_file.write(img_data)
                print(f"画像保存: {image_filename}")
            except Exception as e:
                print(f"画像のダウンロードに失敗: {image_url} - {e}")
                image_filename = None

        # JSON用辞書に追加
        menu_data[menu_name] = {
            "URL": url,
            "価格": price,
            "販売場所": place_list if place_list else None,
            "備考": remarks,
            "画像URL": image_url,
            "画像ファイル名": image_filename,
            "分類": None
        }

        print(f"保存: {menu_name}")

        time.sleep(random.uniform(0.3, 1.0))

    except requests.exceptions.RequestException:
        print("エラーにより", url, "にアクセスできませんでした。")
        continue

# JSONファイルに保存
with open("../json/menu_data.json", "w", encoding="utf-8") as json_file:
    json.dump(menu_data, json_file, ensure_ascii=False, indent=2)

print("すべてのデータをJSONに保存しました。")

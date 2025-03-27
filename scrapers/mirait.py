import os
import sys
print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bs4 import BeautifulSoup
import requests
import json

from datetime import datetime

from utils.common_methods import read_url


def scrape_mirait_news(year):
    url = f"https://www.mirait-one.com/miraiz/whatsnew/?year={year}"
    response = requests.get(url)
    response.encoding = response.apparent_encoding  # エンコーディングを自動検出
    soup = BeautifulSoup(response.text, "html.parser")
    
    # データを格納するリスト
    articles = []

    # 追加タイトルキーワードリスト
    include_keywords = [
        ["市場について"],  # 単独のキーワード
        ["市場動向"], 
        ["市場規模"],
        ["市場"],
        ["について"]
        # 他の追加キーワードを追加可能
    ]

    # 記事データの抽出
    for article in soup.select('ul.new_art_box li'):
        try:
            # 日付
            date_tag = article.select_one("p.top_date span")
            date = date_tag.text.strip() if date_tag else None
            
            # タイトル
            title_tag = article.select_one("h2.top_title")
            title = title_tag.text.strip() if title_tag else None
            
            # 記事リンク
            link_tag = article.select_one("a")
            link = link_tag["href"] if link_tag else None
            full_link = f"https://www.mirait-one.com{link}" if link else None
            
            # タグ
            tags = [
                tag.text.strip()
                for tag in article.select("ul.top_tag object a")
            ]
            
            # 追加キーワードのチェック
            if title:
                should_include = False
                for keywords in include_keywords:
                    if all(keyword in title for keyword in keywords):
                        should_include = True
                        break
                if not should_include:
                    continue  # キーワードが含まれていなければスキップ

            # データを格納
            if date and title and full_link:
                articles.append({
                    "date": date,
                    "title": title,
                    "link": full_link,
                    "tags": tags,
                })
        except Exception as e:
            print(f"Error extracting article: {e}")
    
    return articles

if __name__ == "__main__":
    from utils.json_file_manager import JsonFileManager
    
    jfm = JsonFileManager()
    all_articles = []
    years = [2024, 2023, 2022, 2021]  # 収集する年のリスト

    # 各年のデータを収集
    for year in years:
        print(f"Extracting data for year {year}")
        articles = scrape_mirait_news(year)
        all_articles.extend(articles)
    
    all_articles and jfm.write_to_jsonl(file_path="input_file/mirait.jsonl", data_list=all_articles)
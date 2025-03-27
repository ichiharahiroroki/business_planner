import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.common_methods import read_url
from utils.json_file_manager import JsonFileManager

def scrape_mixonline_news(page=1):
    # ページ番号を含むURL
    url = f"https://www.mixonline.jp/news/tabid64.html?pno_2423={page}"

    # HTMLを取得
    soup = read_url(url)
    if not soup:
        return []

    # ニュースデータを保存するリスト
    news_data = []

    # "newsListItemWrap" を取得
    wrapper = soup.find("div", class_="newsListItemWrap")
    if not wrapper:
        return []

    # "newsListItems" を取得（各記事）
    news_items = wrapper.find_all("div", class_="newsListItems")

    for item in news_items:
        try:
            # 日付（. を / に変換）
            date = item.find("div", class_="releaseDate")
            if not date:
                continue
            date = date.get_text(strip=True).replace('.', '/')

            # カテゴリ
            category = item.find("div", class_="newsCategory")
            if not category:
                continue
            category = category.get_text(strip=True)

            # "市場調査" のカテゴリのみ処理
            if category != "市場調査":
                continue

            # タイトルとリンク
            subject_tag = item.find("div", class_="newsSubject").find("a")
            if not subject_tag:
                continue
            title = subject_tag.get_text(strip=True)
            link = subject_tag["href"]
            full_link = f"https://www.mixonline.jp{link}" if not link.startswith("http") else link

            # データをリストに追加
            news_data.append({
                "date": date,
                "category": category,
                "title": title,
                "link": full_link
            })
        except AttributeError:
            continue

    return news_data


if __name__ == "__main__":
    
    jfm = JsonFileManager()
    # ページ番号を指定して取得
    for page in range(1, 2000): 
        news_list = scrape_mixonline_news(page)
        # news_listをそのまま渡す（辞書形式のリスト）
        if(news_list and jfm.write_to_jsonl(file_path="input_file/mixonline.jsonl", data_list=news_list)):
            print("追加",page)
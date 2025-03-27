import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.json_file_manager import JsonFileManager
import requests
from bs4 import BeautifulSoup

def fetch_fuji_keizai_data(page):
    url = f"https://www.fuji-keizai.co.jp/press/?action=get_list&page={page}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.fuji-keizai.co.jp/press/",
        "Origin": "https://www.fuji-keizai.co.jp",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    
    # POSTリクエストを送信
    response = requests.post(url, headers=headers, verify=False)
    
    if response.status_code == 200:
        return response.json()  # JSON形式でデータを返す
    else:
        print(f"Failed to fetch page {page}. Status code: {response.status_code}")
        return None

def scrape_fuji_keizai_news(page=1):
    """
    指定されたページ番号のニュースデータを取得する関数。
    カテゴリとタイトルを正確に区別してデータを返す。

    Args:
        page (int): 取得するページ番号

    Returns:
        list: ニュースデータのリスト（辞書形式）
    """
    # データを取得
    data = fetch_fuji_keizai_data(page)
    if not data or "list" not in data:
        return []

    # BeautifulSoupでHTMLをパース
    soup = BeautifulSoup(data["list"], "html.parser")
    news_items = []

    for item in soup.find_all("li"):
        try:
            # 日付の取得
            date = item.find("dt").get_text(strip=True)
            
            # カテゴリをリストとして取得
            categories = [li.get_text(strip=True) for li in item.find("ul").find_all("li")]
            
            # タイトルの取得（カテゴリのテキスト部分を除く）
            title = item.find("dd").get_text(strip=True).replace("".join(categories), "").strip()
            
            # リンクの取得
            link = item.find("a")["href"]
            # "press" を追加し、先頭の "." を削除
            full_link = f"https://www.fuji-keizai.co.jp/press{link.lstrip('.')}"

            # ニュース項目として追加
            news_items.append({
                "date": date,
                "category": categories,
                "title": title,
                "link": full_link
            })
        except AttributeError:
            continue

    return news_items

if __name__ == "__main__":

    # 書き込み用のJsonFileManagerインスタンスを作成
    jfm = JsonFileManager()

    for page in range(1, 1000):  # 例: 1ページ目から12ページ目まで
        news_list = scrape_fuji_keizai_news(page)
        # news_listをそのまま渡す（辞書形式のリスト）
        if(news_list and jfm.write_to_jsonl(file_path="input_file/xxxx.jsonl", data_list=news_list)):
            print("追加")
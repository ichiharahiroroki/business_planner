import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode


def read_url(url,verify=True):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10,verify=verify)
        response.raise_for_status()  # HTTPエラーが発生した場合は例外をスロー
        response.encoding = 'utf-8'  # UTF-8エンコーディングを強制
        return BeautifulSoup(response.text, 'html.parser')
    
    except requests.exceptions.Timeout:
        print(f"タイムアウトしました: {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL {url}: {e}")
        #print(f"リンクを開くことができません。エンジニアに確認してもらって下さい。URL:{url}")
        return None

 # すべてのキーの値を空の文字列に設定 
def reset_researcher_dict(startup_dict):
    for key in startup_dict.keys():
        if key != '追加日':
            startup_dict[key] = ""
    return startup_dict


def check_existence(info_source: str, name: str,  link: str , existings: list) -> str:
    """
    """
    
    # 同じ情報源に絞り込む
    filtered_existings = [row for row in existings if row[0] == info_source]
    filtered_existings = filtered_existings[::-1]
    #print(filtered_existings)
   
    # 同じ情報源が見つからなかった場合は non-exist を返す
    if not filtered_existings:
        return "non-exist"
    
    # None を "" として扱う
    link = link or ""
    
    link = normalize_url(link)
    
    for existing in filtered_existings:
        existing_name, existing_link = existing[1],  normalize_url(existing[2])
        # None を "" として扱う
        existing_link = existing_link or ""
        
        # 企業名が一致する場合
        if name == existing_name:
    
            # HPリンクが一致する場合
            if link == existing_link:
                #print("exist:",link,"&",existing_link)
                return "exist"
            else:
                #print("HPlink-updated:",link,"&",existing_link)
                return "HPlink-updated"

       
        
    # 同じ情報源に企業名と授与番号が一致するものがない場合
    return "non-exist"

def find_disappeared_companies(info_source: str, cheacked_existing_list: list, existings: list) -> list:
    """
    指定された情報源で絞り込まれたexistingsから、cheacked_existing_listに存在しない企業を探す。

    :param info_source: 絞り込み対象の情報源
    :param cheacked_existing_list: チェックされた企業名のリスト
    :param existings: 既存のデータのリスト（各要素はリスト）
    :return: cheacked_existing_listに存在しない企業名のリスト
    """
    
    # 同じ情報源に絞り込む
    filtered_existings = [row for row in existings if row[0] == info_source]
    
    # チェックされていない企業名のリスト
    disappeared_companies = []
    
    # 絞り込んだexistingsの中で、cheacked_existing_listにない企業名を探す
    for row in filtered_existings:
        company_name = row[1]  # 企業名が存在する位置を指定（例：1番目）
        if company_name not in cheacked_existing_list:
            disappeared_companies.append(company_name)
    
    return disappeared_companies


from urllib.parse import urlparse, urlencode, parse_qsl, urlunparse

def normalize_url(url):
    """URLを正規化して統一フォーマットにします。"""
    
    # URLがNoneの場合をハンドリング
    if url is None:
        return ""
    
    if url == "https://":
        return ""
    
    parsed_url = urlparse(url)
    
    if not parsed_url.scheme or not parsed_url.netloc:
        print(f"リンクではありません: {url}")
        return None
    
    # スキームを小文字にする
    scheme = parsed_url.scheme.lower()
    
    # ネットワーク位置を小文字にする
    netloc = parsed_url.netloc.lower()
    
    # パスの末尾のスラッシュを削除し、必要であればパスを空文字に
    path = parsed_url.path
    if isinstance(path, bytes):
        path = path.decode('utf-8')
    path = path.rstrip('/')
    
    # クエリパラメータを標準的な順序に並べ替える
    query = urlencode(sorted(parse_qsl(parsed_url.query)))
    
    normalized_url = urlunparse((scheme, netloc, path, '', query, ''))
    
    return normalized_url

def is_valid_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
    }
    try:
        # GETリクエストを使用し、リダイレクトを許可
        response = requests.get(url, headers=headers, timeout=8, allow_redirects=True) # ,verify=False
        # ステータスコードが200番台であれば有効と判断
        #print(response)
        return 200 <= response.status_code < 300
    except requests.RequestException as e:
        print(f"URLのチェックに失敗しました: {e}")
        return False


# if __name__ == "__main__":
    
#     kekka = is_valid_url("https://www.nedo.go.jp/content/100921831.png")
#     print(kekka)

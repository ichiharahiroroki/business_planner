#webページでもメインの内容を抽出
import trafilatura
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from readability import Document 
import requests
from utils.common_methods import read_url

#GPT　APIを利用する場合は、.replace("\n", "")で改行を消してトークンを節約することができます。
def readability_method(input_value, is_html_string=False):
    try:
        if is_html_string:
            # HTML文字列が直接渡された場合
            html_content = input_value
        else:
            # URLが渡された場合、ウェブページの内容を取得
            soup = read_url(input_value,verify=False)
            html_content = str(soup)

        # Readabilityでメインコンテンツを抽出
        doc = Document(html_content)
        main_content = doc.summary()
        
        if main_content == "<html><body></body></html>":
            print(f"このリンクまたはHTMLではreadabilityライブラリを使用できませんでした。\n: {input_value}")
            return None
        
        return main_content

    except requests.RequestException as e:
        print(f"readabilityライブラリを使用中、リンクへのリクエストに失敗しました: {input_value} : エラーコード： {e}")
        return None
    except Exception as e:
        print(f"readabilityライブラリを使用中、コンテンツの抽出に失敗しました: {e}")
        return None


# 使用例:
# URLから読み取る場合
# url = "https://example.com"
# print(readability(url))

# # HTML文字列から読み取る場合
# html_string = "<html><body><h1>Example</h1><p>This is an example.</p></body></html>"
# print(readability(html_string, is_html_string=True))

if __name__ == "__main__":
    
    url = "https://www.fuji-keizai.co.jp/press/detail.html?cid=24115"
    print(readability_method(url))
    
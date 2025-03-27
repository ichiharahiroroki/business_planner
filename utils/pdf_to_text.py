import requests
import io
import PyPDF2
from PyPDF2.errors import PdfReadError

# PDFファイルからテキストを抽出する関数
def pdf_to_text_PyPDF2(pdf_url):
    try:
        if check_url_extension('pdf', pdf_url) or requests.head(pdf_url, allow_redirects=True,timeout=10).headers.get('Content-Type') == 'application/pdf':  # URLの拡張子を確認しPDFであることを確認
            
            try:
                # 指定されたURLからPDFファイルを取得
                response = requests.get(pdf_url,timeout=10)
                response.raise_for_status()  # Check that the request was successful
                # 取得したファイルをio.BytesIOオブジェクトにします
                pdf_io = io.BytesIO(response.content)
                
                try:
                    # io.BytesIOオブジェクトをテキストとして抽出します
                    reader = PyPDF2.PdfReader(pdf_io)
                    
                    # 暗号化されている場合、パスワードを設定
                    if reader.is_encrypted:
                        reader.decrypt("")  # 空のパスワードで解読を試みる
                    
                    text = ''
                    for page_num in range(len(reader.pages)):
                        page = reader.pages[page_num]
                        text += page.extract_text()
                    return text
                
                except PdfReadError as e:
                    print(f"PDFの読み込みに失敗しました: {e}")
                    return None
            except requests.exceptions.Timeout:
                print(f"タイムアウトしました: {pdf_url}")
                return None
            except requests.exceptions.HTTPError as e:
                print(f"HTTPリクエストが失敗しました: {e}")
                return None
            except Exception as e:
                print(f"その他のエラーが発生しました: {e}")
                return None

        else:
            text = "PDFファイルではありません。リンクを確認して下さい。"
            print(text, pdf_url)
            return None
        
    except requests.exceptions.Timeout:
        print(f"タイムアウトしました: {pdf_url}")
        return None
    except Exception as e:
        print(f"その他のエラーが発生しました: {e}")
        return None
                    
import subprocess
def pdf_to_text_with_pdftotext(pdf_url):
    if check_url_extension('pdf', pdf_url):  # URLの拡張子を確認しPDFであることを確認
        try:
            # pdftotextコマンドを実行してPDFをテキストに変換
            result = subprocess.run(['pdftotext', pdf_url, '-'], stdout=subprocess.PIPE)
            return result.stdout.decode('utf-8')
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            return None
    else:
        text = "PDFファイルではありません。リンクを確認して下さい。"
        print(text, pdf_url)
        return None
        

# 任意のURLが指定された拡張子を持つかどうかを判別する関数
def check_url_extension(expected_extension, url):
    if not url:
        return False

    from urllib.parse import urlparse
    import os
    
    parsed_url = urlparse(url)
    path = parsed_url.path
    _, ext = os.path.splitext(path)
    
    ext = ext.lstrip('.').lower()
    expected_extension = expected_extension.lower()
    
    return ext == expected_extension


if __name__ == "__main__":
    url = "https://www.meti.go.jp/press/2023/08/20230831002/20230831002-1.pdf"
    text = pdf_to_text_PyPDF2(url)
    print(text)

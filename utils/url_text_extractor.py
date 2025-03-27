import trafilatura
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.common_methods import read_url

def extract_text_from_url(url,verify=True):
    # ウェブページを取得
    soup = read_url(url,verify)
    if not soup:
        return None

    # テキストを抽出
    content = trafilatura.extract(str(soup), favor_recall=False)
    if content is None:
        print("Failed to extract content from the downloaded data.")
        return None

    # テキストを行ごとに分割
    lines = content.split('\n')

    # 1回でも検出されたらそれ以降を出力しないキーワードのリスト
    cutoff_keywords = [
        '企業プレスリリース詳細へ',
        'こんな記事も',
        'このプレスリリースには、メディア関係者向けの情報があります',
        'メディアユーザーログイン既に登録済みの方はこちら',
        'この記事が気に入ったらサポートをしてみませんか？',
        'トピック一覧に戻る',
        '関連するトピックス',
        'ログイン後、無料でお読みいただけます。',
    ]

    # 2回連続して検出されたら、それ以降を出力しないキーワードのリスト
    sequential_keywords = [
        'すべての画像',
        '種類',
        'その他',
        'ビジネスカテゴリ',
        'アプリケーション・セキュリティ',
        '関連リンク',
        'さらに読む',
        '意味をわかりやすく簡単に解説',
        '参考サイト',
        'PR TIMES.',
        '関連記事',
    ]

    cutoff_index = None
    prev_line_has_sequential_keyword = False

    def line_contains_keyword(line, keywords):
        for keyword in keywords:
            if keyword in line:
                return True
        return False

    for i, line in enumerate(lines):
        # まず、cutoff_keywordsのチェック
        if line_contains_keyword(line, cutoff_keywords):
            cutoff_index = i
            break

        # 次に、sequential_keywordsのチェック
        current_line_has_sequential_keyword = line_contains_keyword(line, sequential_keywords)
        if prev_line_has_sequential_keyword and current_line_has_sequential_keyword:
            cutoff_index = i - 1  # 最初のキーワードが見つかった行のインデックス
            break
        prev_line_has_sequential_keyword = current_line_has_sequential_keyword

    # キーワードが見つかった場合、それ以降の行を削除
    if cutoff_index is not None:
        lines = lines[:cutoff_index]

    # テキストを再結合
    content = '\n'.join(lines)
    return content


if __name__ == "__main__":
    
    url="https://www.fuji-keizai.co.jp/press/detail.html?cid=24115"
    print(extract_text_from_url(url,verify=False))
    
    
# サイトの読み込み https://www.wantedly.com/companies/company_6435340/post_articles/290912
# サイトの読み込み https://kyozon.net/list/youtube_mikiwame-differentiation/
# サイトの読み込み https://theepicinc.com/service/business-model-diagnosis/
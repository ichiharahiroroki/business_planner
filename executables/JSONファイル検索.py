import os
import sys
import json

def search_in_record(record, keyword):
    """
    再帰的にJSONレコード内を検索し、キーワードに一致するか判定する。

    :param record: JSONレコード（辞書またはリスト）
    :param keyword: 検索するキーワード
    :return: キーワードが含まれていればTrue、それ以外はFalse
    """
    if isinstance(record, dict):
        for key, value in record.items():
            if isinstance(value, (dict, list)):
                if search_in_record(value, keyword):
                    return True
            elif isinstance(value, str) and keyword in value:
                return True
    elif isinstance(record, list):
        for item in record:
            if isinstance(item, (dict, list)):
                if search_in_record(item, keyword):
                    return True
            elif isinstance(item, str) and keyword in item:
                return True
    elif isinstance(record, str):
        if keyword in record:
            return True
    return False

def limit_results(results, max_results):
    """
    検索結果を制限する関数。将来的に優先順位付け機能を追加しやすくするために分離。

    :param results: 検索結果のリスト
    :param max_results: 最大取得件数。Noneの場合は全件取得。
    :return: 制限された検索結果のリスト
    """
    if max_results is not None:
        return results[:max_results]
    return results

def search_json_file(file_paths, search_keywords, operator='or', max_results=None):
    """
    JSONファイル（複数）から指定したキーワードに基づいてデータを検索する。

    :param file_paths: JSONファイルのパスまたはパスのリスト
    :param search_keywords: 検索するキーワードのリスト
    :param operator: キーワードの論理演算子 'or' または 'and'
    :param max_results: 最大取得件数。Noneの場合は全件取得。
    :return: 検索結果のリスト
    """
    results = []

    # ファイルパスがリストでない場合、リストに変換
    if not isinstance(file_paths, list):
        file_paths = [file_paths]

    try:
        for file_path in file_paths:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)  # JSONファイル全体をロード

                for record in data:
                    if operator.lower() == 'or':
                        # 'or' 演算子の場合、いずれかのキーワードが一致すればTrue
                        if any(search_in_record(record, keyword) for keyword in search_keywords):
                            results.append(record)
                    elif operator.lower() == 'and':
                        # 'and' 演算子の場合、すべてのキーワードが一致すればTrue
                        if all(search_in_record(record, keyword) for keyword in search_keywords):
                            results.append(record)
                    else:
                        print(f"不正なoperator値です: {operator}. 'or' または 'and' を指定してください。")
                        return []

        # 検索結果を制限
        limited_results = limit_results(results, max_results)
        return limited_results

    except FileNotFoundError:
        print(f"ファイルが見つかりません: {file_path}")
        return []
    except json.JSONDecodeError:
        print("JSONファイルの形式が不正です。")
        return []
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return []



# 使用例
if __name__ == "__main__":
    # JSONファイルのパス（単一または複数）
    json_file_paths = [
        "output_file/fuji_keizai学習用キーワードあり.json",
        "output_file/mirait2学習用キーワードあり.json",
        "output_file/mixonline学習用キーワードあり.json"
        # 必要に応じて追加
    ]

    # 検索キーワード
    search_keywords = ["教育機関"]
    
    operator = 'and' 

    # max_resultsを指定して検索（例: 5件まで取得）
    limited_results = search_json_file(json_file_paths, search_keywords, operator=operator, max_results=None)

    # 結果を出力
    print(json.dumps(limited_results, ensure_ascii=False, indent=2))
    print(f"検索結果の件数: {len(limited_results)}")
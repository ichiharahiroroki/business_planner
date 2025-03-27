import os
import sys
print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.common_methods import read_url
from utils.url_text_extractor import extract_text_from_url
from api_clients.spreadsheet_manager import SpreadsheetManager
from storage.secret_manager import SecretManager
from api_clients.openai_handler import OpenAIHandler
from prompt.what_how_why_answer import what_how_why_answer
from services.get_competitor import GetCompetitorByKeywords
import whois
import json
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

def read_json_file_as_generator(file_path):
    """
    JSONファイルの各要素を順番に取得するジェネレーター関数。
    
    :param file_path: JSONファイルのパス
    :yield: JSON形式の各要素
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)  # JSON全体をロード
            if isinstance(data, list):  # データがリストであることを確認
                for item in data:
                    yield item  # 各要素を順番に返す
            else:
                raise ValueError("JSONデータの形式がリストではありません。")
    except FileNotFoundError:
        print(f"ファイルが見つかりません: {file_path}")
    except json.JSONDecodeError:
        print("JSONファイルの形式が不正です。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

def read_jsonl_file(file_path):
    """
    JSONLファイルから順番にデータを取得するジェネレーター関数。
    データが1つずつ取得されるたびに次のデータを返します。
    
    :param file_path: JSONLファイルのパス
    :yield: JSON形式のデータ
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():  # 空行を無視
                    try:
                        yield json.loads(line.strip())  # 1つずつデータを返す
                    except json.JSONDecodeError as e:
                        print(f"JSONのデコードエラー: {e}, 行: {line}")
    except FileNotFoundError:
        print(f"ファイルが見つかりません: {file_path}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")  
            
def convert_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()  # ISO 8601 形式の文字列に変換
    raise TypeError(f"Type {type(obj)} is not serializable")
  
   
def append_to_jsonl_file(file_path, dict_list):
    """
    JSONLファイルにデータを追記する関数。
    
    :param file_path: JSONLファイルのパス
    :param dict_list: データのリスト（辞書形式）
    :param info: 追加する情報（辞書形式）
    """
    if dict_list:
        try:
            with open(file_path, 'a', encoding='utf-8') as f:  # 'a' は追記モード
                for data in dict_list:
                    # JSONL形式で追記
                    f.write(json.dumps(data, ensure_ascii=False, default=convert_datetime) + '\n')
                    #f.write(json.dumps(data, ensure_ascii=False) + '\n')
            print(f"データが正常に {file_path} に追加されました。")
        except Exception as e:
            print(f"JSONLファイルへの追記中にエラーが発生しました: {e}")
            sys.exit()
    else:
        print("追加するものなし。")

def run_task(index, data, openai_api_key, output_file_path):
    """
    個々のデータを処理するタスク
    :param index: データの順序番号
    :param data: 処理対象のデータ
    :param openai_api_key: OpenAI APIキー
    :param output_file_path: 出力先のJSONLファイルパス
    :return: 処理結果（index, data）
    """
    client_setter = OpenAIHandler(openai_api_key)
    client = client_setter.setting_assistant_client()  # client を作成
    assistant_id = "asst_Sx1vb5wVjKpBS0xZtZLw2GxB"

    try:
        thread_id = client_setter.create_thread()
        client_setter.send_question_and_run(assistant_id, str(data))
        keywords_list = client_setter.get_first_message_as_list()

        if keywords_list:
            print(f"タスク{index}: AIの回答 - {keywords_list}")
            data["keywords"] = keywords_list
        else:
            print(f"タスク{index}: キーワードが空です。データ - {data}")

        # JSONLに追加
        append_to_jsonl_file(output_file_path, [data])
    except Exception as e:
        print(f"タスク{index}: エラーが発生しました - {e}")

    return index, data

def run(input_file_path, output_file_path, max_workers=4):
    """
    JSONLファイルの各データを並列処理する
    :param input_file_path: 入力JSONLファイルパス
    :param output_file_path: 出力JSONLファイルパス
    :param max_workers: 並列処理の最大ワーカー数
    """
    # OpenAI APIキーを取得
    openai_api_key = os.getenv('OPENAI_API_KEY')

    # データジェネレータを作成
    data_gen = read_jsonl_file(input_file_path)

    # 入力データをリストに変換
    data_list = list(enumerate(data_gen, start=1))

    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # mapで元の順序を維持しながら並列処理
        for result in executor.map(lambda args: run_task(*args, openai_api_key, output_file_path), data_list):
            results.append(result)

    # 結果を出力
    print("すべての処理が完了しました。結果:")
    for index, result_data in results:
        print(f"Index: {index}, Data: {result_data}")

# 使用例
if __name__ == "__main__":
    input_file_path = "/Users/ichikawatomohiro/Desktop/patent/output_file/mirait2.jsonl"
    output_file_path = "/Users/ichikawatomohiro/Desktop/patent/output_file/mirait2学習用キーワードあり.jsonl"
    run(input_file_path, output_file_path)
    
    # ジェネレーターを使用して各要素を取得
    # for item in read_json_file_as_generator(json_file_path):
    #     print(json.dumps(item, ensure_ascii=False, indent=2)) 
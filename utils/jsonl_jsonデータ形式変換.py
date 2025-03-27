import json
from datetime import datetime

def format_jsonl_date(input_path, output_path):
    """
    JSONLファイルの中でdateキーの値を指定された形式に変換し、新しいファイルとして保存する。

    :param file_path: 元のJSONLファイルのパス
    :param output_path: 修正後のJSONLファイルの保存先
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile, open(output_path, 'w', encoding='utf-8') as outfile:
            for line in infile:
                if line.strip():  # 空行を無視
                    try:
                        record = json.loads(line.strip())
                        if "date" in record:
                            # 日付の形式を変換
                            try:
                                # "2023年4月24日"を"2023/04/24"に変換
                                parsed_date = datetime.strptime(record["date"], "%Y年%m月%d日")
                                record["date"] = parsed_date.strftime("%Y/%m/%d")
                            except ValueError as e:
                                print(f"日付形式の変換エラー: {e}, dateの値: {record['date']}")
                        
                        # 修正したデータを新しいJSONLファイルに書き込む
                        outfile.write(json.dumps(record, ensure_ascii=False) + "\n")
                    except json.JSONDecodeError as e:
                        print(f"JSONのデコードエラー: {e}, 行: {line}")
    except FileNotFoundError:
        print(f"ファイルが見つかりません: {input_path}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")


def del_whois_data_replace_source(input_file,output_file):
    # 処理
    with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
        for line in infile:
            # 各行をJSONとして読み込む
            record = json.loads(line)
            
            # "source"に"FUJI-KEIZAI.CO.JP"を設定
            record["source"] = "FUJI-KEIZAI.CO.JP"
            
            # "whois_data"を削除
            if "whois_data" in record:
                del record["whois_data"]
            
            # JSONL形式で1行ずつ出力
            outfile.write(json.dumps(record, ensure_ascii=False) + "\n")

    print("新しいJSONLファイルが作成されました:", output_file)
        
        
def jsonl_to_json(input_path,output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]

    # JSONファイルとして保存
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # ファイルパスを指定して実行
    input_file = "/Users/ichikawatomohiro/Desktop/patent/output_file/mixonline学習用キーワードあり.jsonl"  # 元のJSONLファイル
    output_file = "/Users/ichikawatomohiro/Desktop/patent/output_file/mixonline学習用キーワードあり.json"  # 修正後のJSONLファイル
    jsonl_to_json(input_file, output_file)
    print(f"修正後のJSONLファイルが作成されました: {output_file}")
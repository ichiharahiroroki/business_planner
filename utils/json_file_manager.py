import json
from datetime import datetime

class JsonFileManager:

    @staticmethod
    def write_to_jsonl(file_path, data_list):
        #write_to_jsonl関数で各辞書を1行ずつJSONに変換して書き込む
        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                for data in data_list:
                    f.write(json.dumps(data, ensure_ascii=False, default=JsonFileManager.convert_datetime) + '\n')
            return True
        except Exception as e:
            print(f"JSONLファイルへの追記中にエラーが発生しました: {e}")
            return False
    
    
    # datetime を文字列に変換
    def convert_datetime(self,obj):
        if isinstance(obj, datetime):
            return obj.isoformat()  # ISO 8601 形式の文字列に変換
        raise TypeError(f"Type {type(obj)} is not serializable")
    
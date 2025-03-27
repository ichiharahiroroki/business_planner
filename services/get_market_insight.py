import json

class MarketInsight:
    
    def __init__(self):
        self.json_file_paths = [
            "output_file/fuji_keizai学習用キーワードあり.json",
            "output_file/mirait2学習用キーワードあり.json",
            "output_file/mixonline学習用キーワードあり.json"
            # 必要に応じて追加
        ]
        
    def ask_to_assistant(self):
        #assistantAImarket_size_answer(asst_Sx1vb5wVjKpBS0xZtZLw2GxB)に回答してもらう。
        #トークンの使用量が多大なため辞める。機能としてあってもいいが、メインでの使用は進めない。
        pass
        
    def search_by_keywords_list(self, search_keywords, operator='or', max_results=None):
        """
        JSONファイル（複数）から指定したキーワードに基づいてデータを検索する。
        search_keywordsの先頭のキーワードから順に検索を行う。

        :param search_keywords: 検索するキーワードのリスト
        :param operator: キーワードの論理演算子 'or' または 'and'
        :param max_results: 最大取得件数。Noneの場合は全件取得。
        :return: 検索結果のリスト
        """
        results = []
        seen_records = set()  # 重複を防ぐために記録

        try:
            for keyword in search_keywords:
                for file_path in self.json_file_paths:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)  # JSONファイル全体をロード

                            for record in data:
                                record_id = id(record)  # レコードの一意識別子
                                if record_id in seen_records:
                                    continue  # 既に追加済みの場合はスキップ

                                if operator.lower() == 'or':
                                    # 'or' 演算子の場合、キーワードが一致すればTrue
                                    if self.search_in_record(record, keyword):
                                        results.append(record)
                                        seen_records.add(record_id)
                                elif operator.lower() == 'and':
                                    # 'and' 演算子の場合、すべてのキーワードが一致すればTrue
                                    if all(self.search_in_record(record, kw) for kw in search_keywords):
                                        results.append(record)
                                        seen_records.add(record_id)
                                else:
                                    print(f"不正なoperator値です: {operator}. 'or' または 'and' を指定してください。")
                                    return []
                    except FileNotFoundError:
                        print(f"ファイルが見つかりません: {file_path}")
                    except json.JSONDecodeError:
                        print(f"JSONファイルの形式が不正です: {file_path}")
                    except Exception as e:
                        print(f"エラーが発生しました ({file_path}): {e}")

                if max_results is not None and len(results) >= max_results:
                    return self.limit_results(results, max_results)

            return self.limit_results(results, max_results)

        except Exception as e:
            print(f"エラーが発生しました: {e}")
            return []

    def search_in_record(self,record, keyword):
        """
        再帰的にJSONレコード内を検索し、キーワードに一致するか判定する。

        :param record: JSONレコード（辞書またはリスト）
        :param keyword: 検索するキーワード
        :return: キーワードが含まれていればTrue、それ以外はFalse
        """
        if isinstance(record, dict):
            for key, value in record.items():
                if isinstance(value, (dict, list)):
                    if self.search_in_record(value, keyword):
                        return True
                elif isinstance(value, str) and keyword in value:
                    return True
        elif isinstance(record, list):
            for item in record:
                if isinstance(item, (dict, list)):
                    if self.search_in_record(item, keyword):
                        return True
                elif isinstance(item, str) and keyword in item:
                    return True
        elif isinstance(record, str):
            if keyword in record:
                return True
        return False

    def limit_results(self,results, max_results):
        """
        検索結果を制限する関数。将来的に優先順位付け機能を追加しやすくするために分離。

        :param results: 検索結果のリスト
        :param max_results: 最大取得件数。Noneの場合は全件取得。
        :return: 制限された検索結果のリスト
        """
        if max_results is not None:
            return results[:max_results]
        return results
    
    def search_by_keywords_dict(self, keyword_dict, max_results=None):
        core_keywrods = keyword_dict.get("coreKeywords", [])
        action_keywords = keyword_dict.get("actionKeywrods", [])
        related_keywrods = keyword_dict.get("relatedKeywords", [])
        result = set()
        for core_keywrod in core_keywrods:
            for action_keyword in action_keywords:
                results = self.search_by_keywords_list([core_keywrod, action_keyword], operator="and")
                for res in results:  # リスト内の各要素をセットに追加
                    result.add(json.dumps(res, ensure_ascii=False))  # セット内で一意にするためハッシュ化可能にする

        for related_keywrod in related_keywrods:
            results = self.search_by_keywords_list([related_keywrod], operator="and")
            for res in results:
                result.add(json.dumps(res, ensure_ascii=False))

        for core_keywrod in core_keywrods:
            results = self.search_by_keywords_list([core_keywrod], operator="and")
            for res in results:
                result.add(json.dumps(res, ensure_ascii=False))

        # 必要なら文字列化された結果を元の形式に戻す
        final_result = [json.loads(res) for res in result]
        return final_result[:max_results]

    
# 使用例
if __name__ == "__main__":
    keyword_dict = {
                "coreKeywords": [
                    "レアメタル",
                    "海水",
                    "資源回収",
                    "海洋資源",
                    "環境保護"
                ],
                "actionKeywords": [
                    "回収",
                    "抽出",
                    "濃縮",
                    "分離"
                ],
                "relatedKeywords": [
                    "海水抽出技術",
                    "イオン交換",
                    "膜技術",
                    "化学処理"
                ]
    }
    
    core_keywrods = keyword_dict.get("coreKeywords",[])
    action_keywords = keyword_dict.get("actionKeywrods",[])
    related_keywrods = keyword_dict.get("relatedKeywords",[])
    
    #検索キーワード
    market = MarketInsight()
    results = market.search_by_keywords_dict(keyword_dict,max_results=2)
    print(results)
    
    # search_keywords =["レアメタル","海水","資源回収","海洋資源","環境保護","海水抽出技術","イオン交換","膜技術","化学処理"]
    # results = market.search_by_keywords_list(search_keywords,operator="or",max_results=2)
    # print(len(results))
    
    # for result in results:
    #     print(result)
    #     print()
    
    
    
    
    
    
    # search_keywords = ["教育"]

    # operator = 'and' 

    #market = MarketInsight()
    # # max_resultsを指定して検索（例: 5件まで取得）
    # limited_results = market.search_by_keywords_list(search_keywords, operator=operator, max_results=None)

    # # 結果を出力
    # print(json.dumps(limited_results, ensure_ascii=False, indent=2))
    # print(f"検索結果の件数: {len(limited_results)}")
    
    
    
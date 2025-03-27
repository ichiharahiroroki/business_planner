import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from storage.secret_manager import SecretManager
secret_manager = SecretManager()
from services.get_market_insight import MarketInsight
from api_clients.openai_handler import OpenAIHandler
from prompt.what_how_why_answer import what_how_why_answer
from services.get_competitor import GetCompetitorByKeywords

def run_executer(local_file):
    # 実行開始時刻を記録
    
    openai_api_key = os.getenv('OPENAI_API_KEY')
    client_setter = OpenAIHandler(openai_api_key)
    client = client_setter.setting_assistant_client()#client を作成

    #ファイルをベクトルストアに設定
    local_file_ids = [local_file]#["patents_files/レアメタル.pdf"]
    file_ids = client_setter.set_up_file_to_openAI(local_file_ids) # 相対パスを指定
    vector_store_id = client_setter.setuped_file_to_vector_store(file_ids)

    #アシスタントの作成
    idea_assistant_id = client_setter.create_assistant( #事業計画アイデアAI（アシスタント）の作成
    name="事業計画アイデアAI（What,How,Why)",system_instructions=what_how_why_answer, vector_store_id=vector_store_id, model="gpt-4o")
    lean_canvas_assistant_id = "asst_vIrrhnfK8Hd3nb3xLpSmd1Zb"#キャンバスクリエイター
    crunchbase_keywords_assistant_id = "asst_3O4NbuxVaaaHB5KhegCP7fSU"#類似企業検索用キーワード考案AI
    market_insight_keywords_assistant_id = "asst_aud1B8WtGi0FcIQ4oUqcupNK"#市場洞察キーワード考案AI
    
    #スレッドを作成。client_setterのselfで、定義されているので、ここではthread_idは使わない。
    thread_id = client_setter.create_thread()

    from prompt.create_business_idea import get_sequential_messages
    create_loop = 1
    replacements ={}
    messages_generator = get_sequential_messages()  # ジェネレーターを一度生成

    while 3>=create_loop:
        #事業計画アイデアAIが、が質問に答える。
        message = next(messages_generator) 
        client_setter.send_question_and_run(idea_assistant_id,message)
        idea_answer_dict = client_setter.get_first_message_as_dict()#AIの回答を取得。
        print(idea_answer_dict)

        #リーンキャンバスクリエイターが、が質問に答える。
        message="事業計画アイデアAIが考えた、アイデアを基にリーンキャンバスを記入してください。"
        client_setter.send_question_and_run(lean_canvas_assistant_id,message)
        lean_answer_dict = client_setter.get_first_message_as_dict()#AIの回答を取得。
        print(lean_answer_dict)
        
        #crunchbase short_description から検索する用のキーワード。
        message="この事業アイデアのキーワードを考えてください。"
        client_setter.send_question_and_run(crunchbase_keywords_assistant_id,message)
        crunch_keywords_list = client_setter.get_first_message_as_dict_list()
        print(crunch_keywords_list)
        num_of_competitor = 5
        competitor = GetCompetitorByKeywords(crunch_keywords_list,max_num= num_of_competitor)
        competitor_dict_list = competitor.get_competitors_as_dict_list()
        print(competitor_dict_list)

        #市場洞察検索キーワードAI
        message="現在の事業アイデアから関連キーワードを指示通り返してください。"
        client_setter.send_question_and_run(market_insight_keywords_assistant_id,message)
        market_search_keywords_dict = client_setter.get_first_message_as_dict()
        print(market_search_keywords_dict)
        num_of_market = 2
        market = MarketInsight()
        market_results = market.search_by_keywords_dict(market_search_keywords_dict,max_results=num_of_market)
        

        # "What", "How", "Why" のセクションを replacements に追加
        replacements[f"{{{create_loop}_This is the What section content}}"] = idea_answer_dict.get("What", "")
        replacements[f"{{{create_loop}_This is the How section content}}"] = idea_answer_dict.get("How", "")
        replacements[f"{{{create_loop}_This is the Why section content}}"] = idea_answer_dict.get("Why", "")

        # リーンキャンバスの各セクションを replacements に追加
        replacements[f"{{{create_loop}_Lean_Canvas_Subject}}"] = lean_answer_dict.get('Lean_Canvas_Subject', "")
        replacements[f"{{{create_loop}_Lean_Canvas_Solution}}"] = lean_answer_dict.get('Lean_Canvas_Solution', "")
        replacements[f"{{{create_loop}_Lean_Canvas_Key_Indicator}}"] = lean_answer_dict.get('Lean_Canvas_Key_Indicator', "")
        replacements[f"{{{create_loop}_Lean_Canvas_Unique_Value_Proposition}}"] = lean_answer_dict.get('Lean_Canvas_Unique_Value_Proposition', "")
        replacements[f"{{{create_loop}_Lean_Canvas_Superiority}}"] = lean_answer_dict.get('Lean_Canvas_Superiority', "")
        replacements[f"{{{create_loop}_Lean_Canvas_Channel}}"] = lean_answer_dict.get('Lean_Canvas_Channel', "")
        replacements[f"{{{create_loop}_Lean_Canvas_Customer_Segment}}"] = lean_answer_dict.get('Lean_Canvas_Customer_Segment', "")
        replacements[f"{{{create_loop}_Lean_Canvas_Cost_Structure}}"] = lean_answer_dict.get('Lean_Canvas_Cost_Structure', "")
        replacements[f"{{{create_loop}_Lean_Canvas_Revenue_Stream}}"] = lean_answer_dict.get('Lean_Canvas_Revenue_Stream', "")
 
        # 類似企業の各セクションを replacements に追加
        for idx in range(1, num_of_competitor + 1):
            if idx <= len(competitor_dict_list):
                # competitor_dict_list に要素がある場合はデータを取得
                competitor = competitor_dict_list[idx - 1]
                replacements[f"{{{create_loop}.{idx}_competitors_name}}"] = competitor.get("name", "N/A")
                replacements[f"{{{create_loop}.{idx}_competitors_description}}"] = competitor.get("short_description", "N/A")
                replacements[f"{{{create_loop}.{idx}_competitors_website_url}}"] = competitor.get("website_url", "N/A")
                replacements[f"{{{create_loop}.{idx}_competitors_crunchbase_url}}"] = competitor.get("crunchbase_url", "N/A")
            else:
                # competitor_dict_list に要素が足りない場合は空白で埋める
                replacements[f"{{{create_loop}.{idx}_competitors_name}}"] = ""
                replacements[f"{{{create_loop}.{idx}_competitors_description}}"] = ""
                replacements[f"{{{create_loop}.{idx}_competitors_website_url}}"] = ""
                replacements[f"{{{create_loop}.{idx}_competitors_crunchbase_url}}"] = ""

        ###ここにmarket_resultsをreplacements に追加
                # 市場洞察結果をreplacements に追加
        for idx, market_result in enumerate(market_results, start=1):
            base_key = f"{create_loop}.{idx}_market_insight"
            # タイトル
            replacements[f"{{{base_key}_title}}"] = market_result.get("title", "")

            # 大分類・中分類
            replacements[f"{{{base_key}_main_category}}"] = market_result.get("main_category", "")
            replacements[f"{{{base_key}_sub_category}}"] = market_result.get("sub_category", "")

            # サマリー
            replacements[f"{{{base_key}_summary}}"] = market_result.get("summary", "")

            # 知見
            replacements[f"{{{base_key}_knowledge}}"] = market_result.get("knowledge", "")

            # 出典
            replacements[f"{{{base_key}_source}}"] = market_result.get("source", "")
            replacements[f"{{{base_key}_link}}"] = market_result.get("link", "")

            # 市場規模情報を追加
            for market_idx, market_size in enumerate(market_result.get("market_size", []), start=1):
                market_key = f"{create_loop}.{idx}.{market_idx}_market_insight"
                replacements[f"{{{market_key}_market_type}}"] = market_size.get("market_type", "")
                replacements[f"{{{market_key}_year}}"] = str(market_size.get("year", ""))
                replacements[f"{{{market_key}_size}}"] = str(market_size.get("size", ""))

            # テンプレートに対応するデータが不足している場合、空白で埋める
            for empty_idx in range(len(market_result.get("market_size", [])) + 1, 5):
                market_key = f"{create_loop}.{idx}.{empty_idx}_market_insight"
                replacements[f"{{{market_key}_market_type}}"] = ""
                replacements[f"{{{market_key}_year}}"] = ""
                replacements[f"{{{market_key}_size}}"] = ""
        
        create_loop += 1

    from services.google_drive_slide_services import GoogleServices
    # Drive API と Slides API のサービスオブジェクトを取得
    SERVICE_ACCOUNT_FILE = "storage/uplifted-env-435001-p3-062d0440571e.json"
    # GoogleServices クラスのインスタンスを生成
    google_service = GoogleServices(service_account_file=SERVICE_ACCOUNT_FILE)
    google_service.perform_all_operations(new_folder_name="ユーザー名", new_presentation_name="リーンキャンバスのスライド", replacements=replacements, local_file_paths=local_file_ids)



if __name__ == "__main__":
   
    run_executer
    

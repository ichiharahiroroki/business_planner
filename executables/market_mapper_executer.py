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
from datetime import datetime

#inputファイル（JSONL)に載っているデータをAIに調べてもらい市場規模の結果をoutputファイルへ出力する
def market_size_executer(input_file_path,output_file_path):
    
    #初期設定
    add_sheet = SpreadsheetManager("市場規模調査","データ入力byAPI")
    openai_api_key = os.getenv('OPENAI_API_KEY')
    client_setter = OpenAIHandler(openai_api_key)
    client = client_setter.setting_assistant_client()#client を作成
    assistant_id = "asst_lLrwsBkSIWQDc32LHBjIhusa"
    
    # ファイルパスを指定
    data_gen = read_jsonl_file(input_file_path)
   
    while(True):    
        try:
            # next関数で次の値を取得
            data = next(data_gen)
            print(f"取得したデータ: {data}")
   
        except StopIteration:
            # ジェネレータが終了した場合の処理
            print("すべてのデータを読み終えました。")
            break
        
        date = data["date"]
        link = data["link"]
        

        #スレッドを作成。client_setterのselfで、定義されているので、ここではthread_idは使わない。
        thread_id = client_setter.create_thread()
        main_content = extract_text_from_url(link,verify=False) #記事の本文の取得。
        
        #AIに渡すmessageの作成
        message = f"作成日(dateキー):{date}\n 情報源のリンク(linkキー）:{link}\n{main_content}"
        
        client_setter.send_question_and_run(assistant_id,message)
        dict_list = client_setter.get_first_message_as_dict_list()
        
        if dict_list:
            #whois_dataの取得
            info = get_domain_info(link)
            #スプレットシートに追加
            append_data_to_sheet(add_sheet,dict_list,info)  
            #JSONLに追加する。
            append_to_jsonl_file(output_file_path,dict_list,info)
            
        else:
            print("dict_listは空でした。",link)

             
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
                                                   
def append_data_to_sheet(add_sheet,data_list,info):
    """
    指定されたデータをスプレッドシートに追加する関数。
    
    :param data_list: データのリスト（辞書形式）
    """
    # rows を初期化
    rows = []

    for data in data_list:
        # 必須フィールドを抽出
        row = [
            data.get('date',''),
            data.get('main_category', ''),
            data.get('sub_category', ''),
            data.get('title', ''),
            data.get('summary', ''),
            data.get('knowledge', ''),
            data.get('source', ''),
            data.get('link', ''),
            str(data.get('market_size',[])),
            str(info).replace("\n","")
        ]
        rows.append(row)
    # データをスプレッドシートに追加
    add_sheet.append_rows(rows)

def append_to_jsonl_file(file_path, dict_list, info):
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
                    # 各データに whois_data を追加
                    data['whois_data'] = info
                    # JSONL形式で追記
                    f.write(json.dumps(data, ensure_ascii=False, default=convert_datetime) + '\n')
                    #f.write(json.dumps(data, ensure_ascii=False) + '\n')
            print(f"データが正常に {file_path} に追加されました。")
        except Exception as e:
            print(f"JSONLファイルへの追記中にエラーが発生しました: {e}")
            sys.exit()
    else:
        print("追加するものなし。")

def get_domain_info(url):
    try:
        domain_info = whois.whois(url)
        return domain_info
    except:
        return {}

# datetime を文字列に変換
def convert_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()  # ISO 8601 形式の文字列に変換
    raise TypeError(f"Type {type(obj)} is not serializable")
  
def aditional_info_getter_for_fujikeizai(url):
    text =""
    soup = read_url(url,verify=False)
    if soup and soup.find('div' ,class_="press_subtitle"):
        text = soup.find('div' ,class_="press_subtitle").text
    
    return text
    
if __name__ == "__main__":
    import os
    import sys
    print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from storage.secret_manager import SecretManager
    secret = SecretManager()
    
    # ファイルパスを指定
    input_file_path = "input_file/mirait.jsonl"
    output_file_path = "output_file/mirait.jsonl"
    market_size_executer(input_file_path,output_file_path)
    #aditional_info_getter_for_fujikeizaiを追加している。
    #アシスタントAIが返事しなかった時のタイムアウト
    #fuji_keizai700前くらいに重複あり。

    #append_to_jsonl_fileのテスト
    #append_to_jsonl_file("out_put_file/market_size.jsonl",[],{})
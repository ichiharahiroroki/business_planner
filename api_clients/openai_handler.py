import ast
import os
import sys
import time
# 現在のスクリプトのディレクトリの親ディレクトリを取得
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openai
import json
from datetime import datetime, timezone

class OpenAIHandler:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = self.setting_assistant_client()
        self.thread_id =""
        # openai.api_key = self.api_key

    def setting_assistant_client(self):
        # ベータ版APIを使用する設定
        client = openai.OpenAI(
            api_key=self.api_key,
            default_headers={"OpenAI-Beta": "assistants=v2"}
        )
        return client
    
    #ファイルをOpenAIサーバーにアップロードしてから、ベクトルストアにセットし、ベクトルストアIDをreturnする関数。
    def set_up_file_to_openAI(self,path_list):
        file_ids = []
        for path in path_list:
            if not os.path.isabs(path):
                pdf_path = os.path.join(os.getcwd(), path) # 絶対パスを生成
            else:
                pdf_path = path
            try:
                # PDFファイルをアップロード
                with open(pdf_path, "rb") as file:
                    uploaded_file = self.client.files.create(
                        file=file,
                        purpose="assistants"
                    )
                file_id = uploaded_file.id
                print(f"File uploaded with ID: {file_id}")
                file_ids.append(file_id)  # ファイルIDをリストに追加
            except FileNotFoundError:
                print(f"File not found: {pdf_path}")
            except Exception as e:
                print(f"Error uploading file {path}: {e}")
        return file_ids
    
    def setuped_file_to_vector_store(self,file_ids):
        #ベクトルストアにアップロードしたファイルをセットする。
        if file_ids:
            try:
                vector_store = self.client.beta.vector_stores.create(
                    file_ids=file_ids  # アップロードしたファイルIDを教えて
                )
                # ベクトルストアのIDを取得
                vector_store_id = vector_store.id
                print(f"Vector store created with ID: {vector_store_id}")

                return vector_store_id
            except Exception as e:
                print(f"Error creating vector store: {e}")
                
        else:
            print("No files were uploaded successfully.")
        return None
     
    def create_assistant(self, name ,system_instructions, vector_store_id, model="gpt-4o"):
        """
        新しいアシスタントを作成し、設定を適用します。

        Args:
            system_instructions (str): アシスタントのシステム指示。
            vector_store_id (str): 関連付けるベクトルストアのID。
            model (str, optional): 使用するモデル。デフォルトは "gpt-4"。
            temperature (float, optional): 応答の多様性を制御するパラメータ。デフォルトは 0.4。

        Returns:
            str: 作成されたアシスタントのID。
        """
        try:
            assistant = self.client.beta.assistants.create(
                name=name,
                description="AI assistant to create business plans based on patent PDFs.",
                instructions=system_instructions,
                model=model,
                temperature=0.4,
                tools=[{"type": "file_search"}], # ファイル検索を有効化
                tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store_id]
                }
            }
            )
            assistant_id = assistant.id
            print(f"Assistant created with ID: {assistant_id}")
            return assistant_id
        except Exception as e:
            print(f"Error creating assistant: {e}")
            print("プログラムを終了します。")
            sys.exit(1) 
    
    def create_thread(self):
        try: 
            thread = self.client.beta.threads.create()
            print("スレッドが正常に作成されました。")
            print(f"スレッドID: {thread.id}")
            thread_info = thread.to_dict()
            self.thread_id = thread_info["id"]
            return thread_info["id"]
            
        except Exception as e:
            print(f"create_threadで予期しないエラーが発生しました: {e}")
            print("プログラムを終了します。")
            sys.exit()
            
     #client,assistant_id,thread_id,query,[filepath])
    def send_question_and_run(self,assistant_id,message):
         # ユーザーからのメッセージをスレッドに追加
        message_response = self.client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role="user", 
            content=message 
        )
        #スレッドを実行してアシスタントの回答を取得
        run_response = self.client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=assistant_id  # 作成したアシスタントのIDを使用
        )
        
        # ステータスが "completed" になるまで確認
        while run_response.status != "completed":
            print("Waiting for the assistant to complete the run...")
            time.sleep(1)  # 1秒待機
            # 再度ステータスを取得
            run_response = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread_id,  # スレッドIDを指定
                run_id=run_response.id  # 実行IDを指定
            )
        print("Run completed!")
      
    def get_first_message_as_dict(self):
        try:
            # スレッドのメッセージ一覧を取得
            messages = self.client.beta.threads.messages.list(thread_id=self.thread_id)

            if not messages.data:
                print("スレッドにメッセージがありません。")
                return None
            
            # 最初のメッセージを取得
            message = messages.data[0]
            message_dict =  OpenAIHandler.extract_text_and_convert_to_dict(message)
            
            return message_dict  
        except Exception as e:
            print(f"get_first_messageで予期しないエラーが発生しました: {e}")
            print("プログラムを終了します。")
            sys.exit()
     
    def get_first_message_as_list(self):
        # スレッドのメッセージ一覧を取得
        messages = self.client.beta.threads.messages.list(thread_id=self.thread_id)
        if not messages.data:
                print("スレッドにメッセージがありません。")
                return None
        message = messages.data[0]
        main_text = self.extract_text_from_message(message)
        # 文字列をリスト型に変換
        try:
            result = ast.literal_eval(main_text)
            if isinstance(result, list):
                return result
            else:
                raise ValueError("入力はリスト形式ではありません。")
        except (SyntaxError, ValueError) as e:
            print(f"エラーが発生しました: {e}")
            return None
    
    def get_first_message_as_dict_list(self):
        """
        スレッドの最初のメッセージを取得し、リスト形式に変換して返します。
        
        Returns:
            list: AIの返答をリスト形式で返します。失敗した場合はNoneを返します。
        """
        try:
            # スレッドのメッセージ一覧を取得
            messages = self.client.beta.threads.messages.list(thread_id=self.thread_id)

            if not messages.data:
                print("スレッドにメッセージがありません。")
                return None

            # 最初のメッセージを取得
            message = messages.data[0]
            main_text = self.extract_text_from_message(message)

            if main_text:
                # 文字列がJSON形式のリストであることを確認
                try:
                    data_list = json.loads(main_text)
                    if isinstance(data_list, list):
                        print("Successfully converted to list!")
                        return data_list
                    else:
                        print("メッセージの内容がリスト形式ではありません。")
                        return None
                except json.JSONDecodeError:
                    print("メッセージの内容をJSONとして解析できませんでした。")
                    return None
            else:
                print("メッセージにテキストが含まれていません。")
                return None

        except Exception as e:
            print(f"get_first_message_as_listで予期しないエラーが発生しました: {e}")
            print("プログラムを終了します。")
            sys.exit()
           
    @staticmethod
    def extract_text_from_message(message):
        # メッセージから content のテキスト部分を抽出
        if message.content and message.content[0].type == 'text':
            main_text = message.content[0].text.value  # value の部分を抽出
            return main_text
        else:
            print(message.content)
            print("extract_text_from_messageで予期しないエラーが起きました。")
            print("プログラムを終了します。")
            sys.exit()
            return None
        
    @staticmethod
    def extract_text_and_convert_to_dict(message):
        
        main_text = OpenAIHandler.extract_text_from_message(message)
        if main_text:
            if main_text.startswith("```json"):
                main_text = main_text[len("```json"):].strip()
            if main_text.endswith("```"):
                main_text = main_text[:-len("```")].strip()
                
            start = main_text.find("{")
            end = main_text.rfind("}")
            if start == -1 or end == -1 or start > end:
                print("JSONの開始または終了が見つかりません。内容を確認してください。")
                return None
            # '{' から '}' までを抽出
            json_str = main_text[start:end+1]
            try:
                data_dict = json.loads(json_str)
                print("Successfully converted to dictionary!")
            except json.JSONDecodeError as e:
                print(f"JSON decoding failed: {e}")
                data_dict = None
            return data_dict
        else:
            print("メッセージにテキストが含まれていません。")
            return None
      
    @staticmethod
    def update_assistant_vector_store_ids(client,assistant_id,vector_store_ids):
        # アシスタントを更新して新しいベクトルストアを使用するように設定
        try:
            updated_assistant = client.beta.assistants.update(
                assistant_id=assistant_id,
                tool_resources={
                    "file_search": {
                        "vector_store_ids": vector_store_ids  #リスト型で渡す必要がある。
                    }
                },
            ) 
            print("アシスタントが新しいベクトルストアで正常に更新されました。")
            
        except Exception as e:
            print(f"アシスタントの更新中にエラーが発生しました: {e}")
    
    
    def display_assistants_list(self):
        # OpenAIクライアントの作成
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)

        try:
            # 作成済みのアシスタントのリストを取得
            my_assistants = client.beta.assistants.list(
                order="desc",  # 降順で取得
                #limit=20       # 最大20件まで取得
            )
            
            # アシスタント情報を表示
            print("=== アシスタントリスト ===")
            for assistant in my_assistants.data:
                created_at_human_readable = datetime.fromtimestamp(assistant.created_at, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
                print(f"ID: {assistant.id}")
                print(f"名前: {assistant.name or 'なし'}")
                print(f"モデル: {assistant.model}")
                print(f"説明: {assistant.description or 'なし'}")
                print(f"作成日時: {created_at_human_readable}")
                print("-----")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
    
    @staticmethod
    def display_thread_history(client, thread_id):
        """
        指定されたスレッドIDの全てのトーク履歴を表示する関数。
        
        :param client: OpenAIクライアントインスタンス
        :param thread_id: 表示したいスレッドのID
        """
        try:
            # スレッドのメッセージ一覧を取得
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            
            print("=== スレッド履歴 ===")
            for message in messages.data:
                # メッセージの送信者の役割 (user, assistant, system)
                print(f"Role: {message.role}")
                
                # メッセージのコンテンツを表示
                for content in message.content:
                    if content.type == "text":
                        print(f"Text: {content.text.value}")  # テキストメッセージ
                    elif content.type == "file":
                        print(f"File uploaded: {content.file.name} ({content.file.size} bytes)")  # ファイル名とサイズ
                        print(f"File URL: {content.file.url}")  # ファイルのURL
                
                print("----------------------")  # 区切り線を表示

        except Exception as e:
            print(f"エラーが発生しました: {e}")
    
    def display_all_vector_stores_contents(self):
        """
        全てのベクトルストアを取得し、それぞれに紐づくファイルIDを表示する関数。

        :param client: OpenAIクライアントインスタンス
        """
        try:
            # 全ベクトルストアをリスト化
            vector_stores = self.client.beta.vector_stores.list()

            if not vector_stores.data:
                print("登録されているベクトルストアはありません。")
                return

            print("=== 全ベクトルストア情報一覧 ===")
            for vs in vector_stores.data:
                vs_id = vs.id
                file_ids = vs.file_ids if hasattr(vs, 'file_ids') else []
                print(f"ベクトルストアID: {vs_id}")
                print(f"紐付いているファイルID: {file_ids if file_ids else 'なし'}")
                print("----------------------------")
        except Exception as e:
            print(f"ベクトルストア一覧取得中にエラーが発生しました: {e}")

    def delete_all_vector_stores(self):
        """
        全てのベクトルストア自体を削除する関数。
        登録されている全てのベクトルストアIDを取得し、一つずつ削除していく。

        :param client: OpenAIクライアントインスタンス
        """
        try:
            # 全ベクトルストアをリスト化
            vector_stores = self.client.beta.vector_stores.list()

            if not vector_stores.data:
                print("削除対象となるベクトルストアはありません。")
                return

            for vs in vector_stores.data:
                vs_id = vs.id
                # ベクトルストア自体を削除
                self.client.beta.vector_stores.delete(vector_store_id=vs_id)
                print(f"ベクトルストア {vs_id} を削除しました。")

        except Exception as e:
            print(f"全ベクトルストア削除中にエラーが発生しました: {e}")
    
    
    def display_all_files_list(self):
        """
        指定された OpenAI クライアントを使用してファイルのリストを取得し、出力します。

        Args:
            client: OpenAI API クライアントのインスタンス。

        Returns:
            取得したファイルのリスト。
        """
        try:
            # ファイルのリストを取得
            response = self.client.files.list()
            files = response.data  # 修正箇所: response.get('data', []) から response.data へ

            # ファイル情報を出力
            for file in files:
                print(f"ID: {file.id}")
                print(f"ファイル名: {file.filename}")
                print(f"サイズ (bytes): {file.bytes}")
                print(f"作成日時: {file.created_at}")
                print(f"目的: {file.purpose}")
                print("-" * 40)

            return files

        except Exception as e:
            print(f"エラーが発生しました: {e}")
            return None

    def get_list_all_files(self):
        """
        OpenAI クライアントを使用して全てのファイルのリストを取得します。

        Args:
            client: OpenAI API クライアントのインスタンス。

        Returns:
            取得した全てのファイルのリスト。
        """
        try:
            print("list_all_filesの実行開始")
            all_files = []
            response = self.client.files.list()

            while True:
                files = response.data
                all_files.extend(files)

                if response.has_more:
                    print("ループ")
                    response = response.next_page()
                else:
                    break

            return all_files

        except Exception as e:
            print(f"ファイルのリスト取得中にエラーが発生しました: {e}")
            return None
    
    def delete_all_files(self):
        """
        指定された OpenAI クライアントを使用して全てのファイルを削除し、
        削除したファイルの情報を出力します。

        Args:
            client: OpenAI API クライアントのインスタンス。
        """
        try:
            # 全ファイルを取得
            all_files = self.get_list_all_files(self.client)
            if not all_files:
                print("削除するファイルがありません。")
                return

            for file in all_files:
                file_id = file.id
                file_name = file.filename
                print(f"ファイルを削除中: {file_name} (ID: {file_id})")
                response = self.client.files.delete(file_id)
                if response.deleted:
                    print(f"削除成功: {file_name} (ID: {file_id})")
                else:
                    print(f"削除失敗: {file_name} (ID: {file_id})")
            
            print("全てのファイルの削除が完了しました。")

        except Exception as e:
            print(f"ファイルの削除中にエラーが発生しました: {e}")

    #アシスタントリストの表示
    def display_all_assistant(self):
        """
        すべてのアシスタントを取得して出力する関数。

        Args:
            client: OpenAIのクライアントインスタンス。
        """
        assistants = []
        limit = 100  # 一度に取得するアシスタントの数（最大100）
        order = "desc"  # 降順で取得
        after = None  # ページネーションのカーソル

        while True:
            try:
                response = self.client.beta.assistants.list(
                    limit=limit,
                    order=order,
                    after=after
                )
                assistants.extend(response.data)  # 修正: response['data'] -> response.data

                if response.has_more:  # 修正: response['has_more'] -> response.has_more
                    after = response.last_id  # 修正: response['last_id'] -> response.last_id
                else:
                    break
            except openai.OpenAIError as e:  # 修正: openai.error.OpenAIError -> OpenAIError
                print(f"エラーが発生しました: {e}")
                break

        # 取得したアシスタントを出力
        for assistant in assistants:
            print(f"ID: {assistant.id}")
            print(f"名前: {assistant.name or 'なし'}")
            print(f"説明: {assistant.description or 'なし'}")
            print(f"モデル: {assistant.model}")
            print(f"作成日時: {assistant.created_at}")
            print(f"ツール: {[tool.type for tool in assistant.tools]}")
            print("-" * 40)
        
    #アシスタントをexcept以外すべて削除
    def delete_all_assistant(self,excepts=[]):
        """
        すべてのアシスタントを削除する関数。ただし、exceptsリストに含まれるIDのアシスタントは削除しない。

        Args:
            client: OpenAIのクライアントインスタンス。
            excepts: 削除しないアシスタントのIDリスト。
        """
        # 常に除外するアシスタントのIDリスト
        always_excepts = ["asst_vIrrhnfK8Hd3nb3xLpSmd1Zb","asst_3O4NbuxVaaaHB5KhegCP7fSU","asst_lLrwsBkSIWQDc32LHBjIhusa","asst_Sx1vb5wVjKpBS0xZtZLw2GxB","asst_k3nPRKRMxXuq2NCLHE4PJ9nt","asst_aud1B8WtGi0FcIQ4oUqcupNK"]  # ここに除外したいIDを追加
        # 引数のexceptsリストと常に除外するリストを結合
        combined_excepts = set(excepts) | set(always_excepts)
        
        assistants = []
        limit = 100  # 一度に取得するアシスタントの数（最大100）
        order = "desc"  # 降順で取得
        after = None  # ページネーションのカーソル

        print("アシスタントのリストを取得中...")
        while True:
            try:
                response = self.client.beta.assistants.list(
                    limit=limit,
                    order=order,
                    after=after
                )
                assistants.extend(response.data)

                if response.has_more:
                    after = response.last_id
                else:
                    break
            except openai.OpenAIError as e:
                print(f"アシスタントのリスト取得中にエラーが発生しました: {e}")
                return

        print(f"取得したアシスタントの総数: {len(assistants)}")
        print("削除対象のアシスタントを処理中...")

        # 削除処理
        for assistant in assistants:
            if assistant.id in combined_excepts:
                print(f"ID: {assistant.id} はexceptsリストに含まれているため削除しません。")
                continue
            try:
                response = self.client.beta.assistants.delete(assistant.id)
                if response.deleted:
                    print(f"ID: {assistant.id} を削除しました。")
                else:
                    print(f"ID: {assistant.id} の削除に失敗しました。")
            except openai.OpenAIError as e:
                print(f"ID: {assistant.id} の削除中にエラーが発生しました: {e}")

        print("削除処理が完了しました。")
        

if __name__ == "__main__":
    secret_manager = SecretManager()
    # OpenAI APIキーを設定
    #api_key = "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"
    handler = OpenAIHandler()
    response = handler.delete_all_assistant()
    
    #handler.delete_all_vector_stores()
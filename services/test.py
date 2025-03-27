import os
import sys
import uuid
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# テンプレートとなるGoogle SlidesファイルのID
TEMPLATE_PRESENTATION_ID = '1fRzGY-z6SXjeBomUsBZB2qhp_jTuzfpKHJNzwZTGMT4'
PARENT_FOLDER_ID = "1ydsJKCIHTet5d-A59tadTG3PXFye3t3E"

class GoogleServices:
    """
    Google Drive API と Google Slides API のサービスオブジェクトを保持し、関連する操作を提供するクラス。
    """
    def __init__(self, service_account_file):
        """
        GoogleServices クラスのコンストラクタ。サービスアカウントの認証情報を使用して
        Google Drive API と Google Slides API のサービスオブジェクトを初期化する。

        Args:
            service_account_file (str): サービスアカウントキーのJSONファイルのパス（相対パスまたは絶対パス）。
        """

        self.drive = None
        self.slides = None

        # ファイルパスが相対パスか絶対パスかを判断
        if not os.path.isabs(service_account_file):
            # 相対パスの場合、絶対パスに変換
            service_account_file = os.path.abspath(service_account_file)
            print(f"サービスアカウントファイルの絶対パスに変換しました: {service_account_file}")
        else:
            print(f"サービスアカウントファイルのパス: {service_account_file}")

        # スコープの定義（Google Drive APIとGoogle Slides APIへのフルアクセス）
        scopes = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/presentations'
        ]

        try:
            # サービスアカウントの認証情報を取得
            credentials = service_account.Credentials.from_service_account_file(
                service_account_file,
                scopes=scopes
            )
            print("認証情報を正常に取得しました。")
        except Exception as e:
            print(f"認証情報の取得に失敗しました: {e}")
            sys.exit(1)

        try:
            # Drive APIのサービスオブジェクトを構築
            self.drive = build('drive', 'v3', credentials=credentials)
            print("Google Drive APIのサービスオブジェクトを作成しました。")
        except Exception as e:
            print(f"Drive APIのサービスオブジェクトの作成に失敗しました: {e}")
            sys.exit(1)

        try:
            # Slides APIのサービスオブジェクトを構築
            self.slides = build('slides', 'v1', credentials=credentials)
            print("Google Slides APIのサービスオブジェクトを作成しました。")
        except Exception as e:
            print(f"Slides APIのサービスオブジェクトの作成に失敗しました: {e}")
            sys.exit(1)

    def perform_all_operations(self, new_folder_name, new_presentation_name, replacements, local_file_paths):
        """
        新しいフォルダーの作成、プレゼンテーションのコピー、スライドの複製・テキストの置換、およびファイルのアップロードを
        一連の操作として実行するメソッド。

        Args:
            new_folder_name (str): 作成する新しいフォルダーの名前。
            new_presentation_name (str): マスタープレゼンテーションの名前。
            replacements (list): 各ループの置換辞書のリスト。
                                 各辞書のキーが置換対象の文字列、値が置換後の文字列。
            local_file_paths (list): アップロードするローカルファイルパスのリスト。
        """
        # 親フォルダーのIDを使用
        parent_folder_id = PARENT_FOLDER_ID
        if not parent_folder_id:
            print("親フォルダーのIDが設定されていません。")
            sys.exit(1)

        # 新しいフォルダーを作成
        created_folder_id = self.create_folder(
            parent_folder_id=parent_folder_id,
            new_folder_name=new_folder_name
        )

        # フォルダーの作成に成功した場合のみ処理を続行
        if created_folder_id:
            # マスタープレゼンテーションを作成
            master_presentation_id = self.create_master_presentation(
                master_presentation_name=new_presentation_name,
                parent_folder_id=created_folder_id
            )

            if master_presentation_id:
                print("マスタープレゼンテーションの作成が正常に完了しました。")

                # テンプレートプレゼンテーションからテンプレートスライドIDを取得
                template_slide_id = self.get_template_slide_id(TEMPLATE_PRESENTATION_ID)
                if not template_slide_id:
                    print("テンプレートスライドの取得に失敗したため、スライドの複製を中止します。")
                    sys.exit(1)

                # 各置換辞書に基づいてスライドを作成・置換
                for i, loop_replacements in enumerate(replacements, start=1):
                    print(f"\nループ {i} のスライドを作成中...")
                    # スライドを複製
                    new_slide_id = self.duplicate_slide(
                        presentation_id=master_presentation_id,
                        slide_object_id=template_slide_id
                    )

                    if new_slide_id:
                        print(f"スライドが作成されました。ID: {new_slide_id}")
                        # テキストの置換を実行
                        print(f"ループ {i} のスライドに対して置換を行います。")
                        self.replace_text_in_slide(
                            presentation_id=master_presentation_id,
                            replacements=loop_replacements,
                            slide_object_id=new_slide_id
                        )
                    else:
                        print(f"ループ {i} のスライドの作成に失敗しました。")

                # ローカルファイルのアップロードを実行
                if local_file_paths:
                    self.upload_files_to_folder(
                        folder_id=created_folder_id,
                        local_file_paths=local_file_paths
                    )
                else:
                    print("アップロードするローカルファイルが指定されていません。")
            else:
                print("マスタープレゼンテーションの作成に失敗しました。")
        else:
            print("フォルダーの作成に失敗したため、プレゼンテーションのコピーを中止します。")

    def create_folder(self, parent_folder_id, new_folder_name):
        """
        指定したフォルダー内に新しいフォルダーを作成するメソッド。

        Args:
            parent_folder_id (str): 新しく作成するフォルダーの親フォルダーのID。
            new_folder_name (str): 作成する新しいフォルダーの名前。

        Returns:
            str: 作成されたフォルダーのID。失敗した場合はNone。
        """
        # フォルダーのメタデータを定義
        file_metadata = {
            'name': new_folder_name,  # 新しいフォルダーの名前
            'mimeType': 'application/vnd.google-apps.folder',  # フォルダーであることを示すMIMEタイプ
            'parents': [parent_folder_id]  # 新しく作成するフォルダーの親フォルダーIDを指定
        }

        try:
            # Drive APIを使用して新しいフォルダーを作成
            folder = self.drive.files().create(
                body=file_metadata,
                fields='id'  # 作成されたフォルダーのIDのみを取得
            ).execute()

            # 作成されたフォルダーのIDを取得
            folder_id = folder.get('id')
            print(f"フォルダーが作成されました。ID: {folder_id}")
            return folder_id
        except Exception as e:
            print(f"フォルダーの作成に失敗しました: {e}")
            return None

    def create_master_presentation(self, master_presentation_name, parent_folder_id):
        """
        マスタープレゼンテーションを新しく作成するメソッド。

        Args:
            master_presentation_name (str): マスタープレゼンテーションの名前。
            parent_folder_id (str): マスタープレゼンテーションを配置するフォルダーのID。

        Returns:
            str: 作成されたマスタープレゼンテーションのID。失敗した場合はNone。
        """
        try:
            # マスタープレゼンテーションのメタデータを定義
            file_metadata = {
                'name': master_presentation_name,  # 新しいプレゼンテーションの名前
                'mimeType': 'application/vnd.google-apps.presentation',  # プレゼンテーションであることを示すMIMEタイプ
                'parents': [parent_folder_id]  # マスタープレゼンテーションの親フォルダーIDを指定
            }

            # Drive APIを使用して新しいプレゼンテーションを作成
            presentation = self.drive.files().create(
                body=file_metadata,
                fields='id'  # 作成されたプレゼンテーションのIDのみを取得
            ).execute()

            # 作成されたプレゼンテーションのIDを取得
            presentation_id = presentation.get('id')
            print(f"マスタープレゼンテーションが作成されました。ID: {presentation_id}")

            return presentation_id
        except Exception as e:
            print(f"マスタープレゼンテーションの作成に失敗しました: {e}")
            return None

    def get_template_slide_id(self, template_presentation_id):
        """
        テンプレートプレゼンテーション内の最初のスライドのオブジェクトIDを取得するメソッド。

        Args:
            template_presentation_id (str): テンプレートプレゼンテーションのID。

        Returns:
            str: テンプレートスライドのオブジェクトID。失敗した場合はNone。
        """
        try:
            presentation = self.slides.presentations().get(presentationId=template_presentation_id).execute()
            slides = presentation.get('slides', [])
            if not slides:
                print("テンプレートプレゼンテーションにスライドがありません。")
                return None
            template_slide_id = slides[0].get('objectId')
            print(f"テンプレートスライドのID: {template_slide_id}")
            return template_slide_id
        except Exception as e:
            print(f"テンプレートスライドの取得に失敗しました: {e}")
            return None

    def duplicate_slide(self, presentation_id, slide_object_id):
        """
        テンプレートスライドを複製して新しいスライドを作成するメソッド。

        Args:
            presentation_id (str): プレゼンテーションのID。
            slide_object_id (str): 複製するテンプレートスライドのオブジェクトID。

        Returns:
            str: 複製されたスライドのオブジェクトID。失敗した場合はNone。
        """
        try:
            # 複製リクエストを作成
            requests = [{
                'duplicateObject': {
                    'objectId': slide_object_id,
                    'objectIds': {
                        slide_object_id: f"{slide_object_id}_copy_{uuid.uuid4().hex[:8]}"
                    }
                }
            }]

            # バッチリクエストを実行
            response = self.slides.presentations().batchUpdate(
                presentationId=presentation_id,
                body={'requests': requests}
            ).execute()

            # 複製されたスライドのオブジェクトIDを取得
            duplicate_object = response.get('replies')[0].get('duplicateObject')
            new_slide_id = duplicate_object.get('objectId')

            print(f"スライドが複製されました。新しいスライドID: {new_slide_id}")
            return new_slide_id
        except Exception as e:
            print(f"スライドの複製に失敗しました: {e}")
            return None

    def replace_text_in_slide(self, presentation_id, replacements, slide_object_id):
        """
        指定したスライド内で、辞書のキー値に一致するテキストを検索し、
        対応するバリュー値に置換するメソッド。

        Args:
            presentation_id (str): プレゼンテーションのID。
            replacements (dict): 置換するテキストの辞書。
                                 キーが置換対象の文字列、値が置換後の文字列。
                                 例: {"{key}": "value"}
            slide_object_id (str): テキストを置換するスライドのオブジェクトID。
        """
        try:
            # バッチリクエスト用リスト
            requests = []

            # 各置換対象を処理
            for search_text, replace_text in replacements.items():
                # 置換リクエストを作成
                requests.append({
                    'replaceAllText': {
                        'containsText': {
                            'text': search_text,  # 検索するテキスト
                            'matchCase': True    # 大文字・小文字を区別
                        },
                        'replaceText': replace_text,  # 置換後のテキスト
                        'pageObjectIds': [slide_object_id]  # 特定のスライド内で検索・置換
                    }
                })

            # バッチリクエストを実行
            if requests:
                response = self.slides.presentations().batchUpdate(
                    presentationId=presentation_id,
                    body={'requests': requests}
                ).execute()
                print(f"スライド {slide_object_id} のテキスト置換が完了しました。")
            else:
                print("置換するリクエストがありませんでした。")
        except Exception as e:
            print(f"テキストの置換中にエラーが発生しました: {e}")

    def upload_files_to_folder(self, folder_id, local_file_paths):
        """
        local_file_pathsに含まれるローカルファイルを指定フォルダにアップロードするメソッド。

        Args:
            folder_id (str): アップロード先フォルダID。
            local_file_paths (list): アップロードするローカルファイルパスのリスト。
        """
        for local_file_path in local_file_paths:
            if not os.path.isabs(local_file_path):
                local_file_path = os.path.join(os.getcwd(), local_file_path)

            if os.path.exists(local_file_path) and os.path.isfile(local_file_path):
                file_metadata = {
                    'name': os.path.basename(local_file_path),
                    'parents': [folder_id]
                }

                media = MediaFileUpload(local_file_path, resumable=True)

                try:
                    uploaded_file = self.drive.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id'
                    ).execute()

                    print(f"ローカルファイル '{local_file_path}' をアップロードしました。ID: {uploaded_file.get('id')}")
                except Exception as e:
                    print(f"ローカルファイル '{local_file_path}' のアップロード中にエラーが発生しました: {e}")
            else:
                print(f"ローカルファイルが見つかりません: {local_file_path}")

# メインの実行部分
if __name__ == "__main__":
    # 必要なライブラリをインポート
    import sys
    import os

    # 現在のスクリプトのディレクトリの親ディレクトリを取得
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    SERVICE_ACCOUNT_FILE = "/Users/ichikawatomohiro/Desktop/patent/storage/uplifted-env-435001-p3-062d0440571e.json"
    # GoogleServices クラスのインスタンスを生成
    google_service = GoogleServices(service_account_file=SERVICE_ACCOUNT_FILE)
    
    # replacementsをリストで管理し、各要素に辞書を入れる
    replacements = [
        # ループ1の置換辞書
        {
            "{1_This is the What section content}": "私たちのプロジェクトは、多角体固定化ナノファイバーを活用した、効率的なレアメタルと貴金属の回収サービスです。この技術により、産業廃棄物や使用済み製品から金属イオンを効率的に回収し、持続可能な資源利用を促進します。",
            "{1_This is the How section content}": "ナノファイバーを用いたフィルターを開発し、産業廃棄物や使用済み製品から金属イオンを吸着・回収します。この技術は短時間で高効率な吸着を可能にし、リサイクル工程を簡素化します。",
            "{1_This is the Why section content}": "レアメタルや貴金属の需要が増加している一方で、供給不足が課題となっています。このプロジェクトは、持続可能な資源管理と環境負荷の軽減を目的としています。",
            "{1_Lean_Canvas_Subject}": "多角体固定化ナノファイバーによるレアメタル・貴金属回収サービス",
            "{1_Lean_Canvas_Solution}": "多角体を担持または含有したナノファイバーを使用して、効率的かつ安価にレアメタルや貴金属を回収する技術。",
            "{1_Lean_Canvas_Key_Indicator}": "回収された金属の量、顧客数、技術導入企業数、コスト削減率。",
            "{1_Lean_Canvas_Unique_Value_Proposition}": "短時間で高効率な金属イオンの吸着が可能なナノファイバー技術により、環境負荷を軽減しつつ資源の再利用を促進。",
            "{1_Lean_Canvas_Superiority}": "大がかりな装置を必要とせず、安価で広範囲に金属回収が可能な点で他社技術に対する優位性。",
            "{1_Lean_Canvas_Channel}": "業界展示会、環境関連のカンファレンス、オンラインマーケティング、業界誌広告。",
            "{1_Lean_Canvas_Customer_Segment}": "レアメタルや貴金属を使用する製造業者、リサイクル業者、環境保護団体。",
            "{1_Lean_Canvas_Cost_Structure}": "研究開発費、製造コスト、マーケティング費用、技術サポート費用。",
            "{1_Lean_Canvas_Revenue_Stream}": "技術ライセンス料、金属回収サービスの提供、関連機器の販売。",
        },
        # ループ2の置換辞書
        {
            "{1_This is the What section content}": "第二のプロジェクトは、先端材料を使用したエネルギー効率化ソリューションの開発です。この技術は再生可能エネルギーの効率的な利用を目指しています。",
            "{1_This is the How section content}": "先端材料を活用して、エネルギー変換プロセスの効率を最大化します。これにより、コストを削減し環境負荷を軽減します。",
            "{1_This is the Why section content}": "地球規模でのエネルギー需要の増加に対し、効率的な利用技術が求められています。このソリューションはその課題を解決します。",
            "{1_Lean_Canvas_Subject}": "エネルギー効率化ソリューション",
            "{1_Lean_Canvas_Solution}": "高効率なエネルギー変換を可能にする先端材料技術。",
            "{1_Lean_Canvas_Key_Indicator}": "エネルギー削減率、導入顧客数、技術採用数。",
            "{1_Lean_Canvas_Unique_Value_Proposition}": "先端材料を活用したエネルギー効率の向上により、環境負荷を軽減。",
            "{1_Lean_Canvas_Superiority}": "他社製品よりも高い効率と低コストを実現する技術的優位性。",
            "{1_Lean_Canvas_Channel}": "オンラインマーケティング、業界展示会、専門誌。",
            "{1_Lean_Canvas_Customer_Segment}": "エネルギー企業、製造業者、政府機関。",
            "{1_Lean_Canvas_Cost_Structure}": "研究開発費、製造コスト、営業活動費用。",
            "{1_Lean_Canvas_Revenue_Stream}": "技術ライセンス、製品販売、コンサルティングサービス。",
        }
    ]
    # 例として、2つのループ分の置換辞書を含めています。
    # 必要に応じてリスト形式に変更してください。

    # 新しいプレゼンテーションを作成し、スライドをコピー・置換
    google_service.perform_all_operations(
        new_folder_name="ユーザー名",
        new_presentation_name="リーンキャンバスのスライド",
        replacements=replacements,
        local_file_paths=[]
    )
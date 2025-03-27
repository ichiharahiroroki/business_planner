# main.py
from executables.executer import run_executer
from storage.secret_manager import SecretManager
import time

def main():
    """
    アプリケーションのエントリーポイント。
    必要な初期化や複数の処理を順に呼び出す。
    """
    start_time = time.time()
    print("==== アプリケーション開始 ====")
    #envファイルを環境変数に設定
    secret_manager = SecretManager()
    local_pathes= ["patents_files/レアメタル.pdf","patents_files/ペプチド.pdf","patents_files/BNV_特許.pdf"]
    for path in local_pathes:
    # Executerモジュールを実行
        run_executer(path)
    print("==== アプリケーション終了 ====")
    # 実行終了時刻を記録
    end_time = time.time()
    # 実行時間を計算して表示
    execution_time = end_time - start_time
    print(f"コードの実行にかかった時間: {execution_time:.2f} 秒")

if __name__ == "__main__":
    main()
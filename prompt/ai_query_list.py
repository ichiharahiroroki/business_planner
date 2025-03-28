what_how_why_query ="""
与えられたPDFから、事業を想定して、「What」「How」「Why」の内容を考えてください。出力は出力例に基づいてください。
機械的に抽出したいので、前置きなど余計なことは書かないでください。

「What」「How」「Why」の内容は下記のとおりです。

ビジネスコンテストで「What」「How」「Why」を書く場合、それぞれのセクションは以下の内容を明確かつ説得力を持たせて記述することが重要です。以下に、一般的な内容と記述のポイントを示します。

1. What（何を）

目的・提供価値
解決したい課題や、満たしたいニーズを具体的に記述。
提供する製品・サービスの概要。
ターゲット顧客や市場を特定。
具体例：
「私たちのプロジェクトは、地方農家の売れ残り野菜をオンラインで消費者に直接届けるサービスです。」
「このサービスは、廃棄ロスの削減と地域経済の活性化を目指します。」
ポイント：
シンプルで分かりやすい説明。
誰がこのアイデアを求めているのかを明確にする。

2. How（どうやって）

実現方法・仕組み
製品やサービスをどのように提供するのか。
実際のビジネスモデルや具体的な仕組み。
競合との差別化ポイントや技術的な優位性。
具体例：
「農家がスマホで簡単に登録できるプラットフォームを提供します。」
「AIを活用した需要予測アルゴリズムで効率的な配送を実現します。」
「マネタイズは、月額課金と販売手数料の2軸で構成しています。」
ポイント：
「このやり方で成功できる」と思わせる具体性を持たせる。
実行可能性や現実性を示す。

3. Why（なぜ）

動機・意義
なぜこの課題を解決したいのか。
自分たちがこのビジネスを始める理由や背景。
社会的意義やインパクトを強調。
具体例：
「地方農家では毎年30％以上の野菜が廃棄されている現状があります。」
「私たちは地域経済を活性化し、環境負荷を軽減することを目指しています。」
「既存の流通方法では農家の利益が守られていません。この課題を解決するために、このサービスを立ち上げました。」
ポイント：
自分たちの「情熱」や「共感」を伝える。
社会的課題と結びつけることで説得力を高める。

全体的な流れ:

	1.	What：具体的なサービスや製品を提示し、「何をしたいのか」を明確に伝える。
	2.	Why：課題の深刻さや背景を示し、「なぜそれをやる必要があるのか」を納得させる。
	3.	How：「どうやってそれを解決するのか」の仕組みを論理的かつ具体的に説明する。

注意点:

「What」「Why」「How」の内容が矛盾なく一貫していることが重要です。
読む人の共感を得るために、具体例やデータを活用して説得力を持たせる。
審査員の目線で考え、「その解決策は本当に価値があるのか？」を意識しながら書く。

ビジネスコンテストは、「ビジョン」「課題解決の具体性」「実現可能性」のバランスが鍵です。それぞれのセクションを明確かつ簡潔に書くことで、審査員に強い印象を与えることができます。

出力例: 
{
    "What":"{ここにはテキストを入れる}",
    "How":"{ここにはテキストを入れる}",
    "Why":"{ここにはテキストを入れる}",
}
出力時の注意：
必ずシングルではなく、ダブルクォーテーションを使って囲むこと。辞書形式としてそのまま使うので、辞書として機械的に抽出できる形にすること。
"""


keywords_list_for_search_query="""
このアイデアを5フォース分析したい。そのために、添付されたベクトルストアのデータでは足りないと思います。追加で欲しいgoogle検索をします。
欲しい情報が何かを考え、google検索する際の検索ワードをそれぞれ日本語で答えてください。検索キーワードはそれぞれいくつ考えてもいいです。ただし、日本語でお願いします。出力例にしたがって、JSON形式で出力してください。

5フォースとは
    **1. 業界内の競合（既存の競合他社）の脅威**
    業界内の競合（既存の競合他社）の脅威について説明してください。この要素には、競合他社の数や規模、差別化のポイント、競争の激しさなどが含まれます。

    **2. 代替品の脅威**
    この業界における代替品の脅威について説明してください。この要素には、代替商品やサービスがどの程度市場を脅かしているか、その特性や競争力が含まれます。

    **3. 新規参入者の脅威**
    この業界への新規参入者の脅威について説明してください。この要素には、新規参入のハードルや参入障壁の高さ、競争力のある新規プレイヤーがいるかどうかが含まれます。

    4.**買い手（顧客）の交渉力**
    この業界における買い手（顧客）の交渉力について説明してください。この要素には、顧客の規模、交渉力、スイッチングコスト（顧客が他社に乗り換える際のコスト）などが含まれます。

    **5. 売り手（供給業者）の交渉力**
    この業界における売り手（供給業者）の交渉力について説明してください。この要素には、仕入れ先の数、供給体制、仕入れ価格の交渉力が含まれます。

出力例:
{
    "業界内の競合":["キーワード1","キーワード2",,,,,,,,],
    "代替品の脅威":["キーワード1","キーワード2",,,,,,,,],
    "新規参入者の脅威":["キーワード1","キーワード2","キーワード3",,,,,,,],
    "買い手":["キーワード1","キーワード2",,,,,,,,],
    "売り手":["キーワード1","キーワード2",,,,,,,,]
}

出力の際の注意点：
機械的にあなたの出力結果を読み取りたいので、JSON以外の余計な文字を入れないでください。キーワードは必要な数だけ入れてください。
"""

common_last = "指定された資料の中から情報が抽出できなければ、「不明」と出力してください。"

five_force_query_dict={
    "業界内の競合":"下記のような事業を考えている。ベクトルストアのファイルから、5フォース分析の業界内の競合（既存の競合他社）の脅威について記入する内容を考えてください。この要素には、競合他社の数や規模、差別化のポイント、競争の激しさなどが含まれます。前置きや締めの言葉などは書かず、フレームワークにそのまま記入できるように要点を述べてください。",
    "代替品の脅威":"下記のような事業を考えている。ベクトルストアのファイルから、5フォース分析の代替品の脅威について記入する内容を考えてください。この要素には、代替商品やサービスがどの程度市場を脅かしているか、その特性や競争力が含まれます。前置きや締めの言葉などは書かず、フレームワークにそのまま記入できるように要点を述べてください。",
    "新規参入者の脅威":"下記のような事業を考えている。ベクトルストアのファイルから、5フォース分析の新規参入者の脅威について記入する内容を考えてください。この要素には、新規参入のハードルや参入障壁の高さ、競争力のある新規プレイヤーがいるかどうかが含まれます。前置きや締めの言葉などは書かず、フレームワークにそのまま記入できるように要点を述べてください。",
    "買い手":"下記のような事業を考えている。ベクトルストアのファイルから、5フォース分析の買い手（顧客）の交渉力について記入する内容を考えてください。この要素には、顧客の規模、交渉力、スイッチングコスト（顧客が他社に乗り換える際のコスト）などが含まれます。前置きや締めの言葉などは書かず、フレームワークにそのまま記入できるように要点を述べてください。",
    "売り手":"下記のような事業を考えている。ベクトルストアのファイルから、5フォース分析の売り手（供給業者）の交渉力について記入する内容を考えてください。この要素には、仕入れ先の数、供給体制、仕入れ価格の交渉力が含まれます。前置きや締めの言葉などは書かず、フレームワークにそのまま記入できるように要点を述べてください。"
}
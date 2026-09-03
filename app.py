import streamlit as st

from utils.sidebar import render_common_sidebar

st.set_page_config(
    page_title="AIライティングツール",
    page_icon="✍️",
    layout="wide",
)

render_common_sidebar()

st.title("✍️ AIライティングツール")
st.caption("Gemini APIを使った個人用ライティング支援アプリ")

st.markdown(
    """
左のサイドバーからページを選んで使い始めてください。
初回はサイドバーで **Gemini APIキー** を入力するか、`.env` に `GEMINI_API_KEY` を設定してください。
"""
)

st.divider()

features = [
    ("📝", "ブログ記事作成", "pages/1_📝_ブログ記事作成.py", "テーマや要点からブログ記事の下書きを生成します。"),
    ("📧", "メール返信作成", "pages/2_📧_メール返信作成.py", "受信メールの内容とトーンを指定して返信文を作成します。"),
    ("📄", "文章要約", "pages/3_📄_文章要約.py", "長文を指定の文字数・箇条書きなどで要約します。"),
    ("✏️", "文章校正・リライト", "pages/4_✏️_文章校正リライト.py", "誤字脱字や表現をチェックし、自然な文章に整えます。"),
    ("🎭", "トーン変換", "pages/5_🎭_トーン変換.py", "文章の口調・トーンを丁寧語やカジュアルなどに変換します。"),
    ("💡", "タイトル・キャッチコピー生成", "pages/6_💡_タイトル案生成.py", "記事内容に合ったタイトル案を複数生成します。"),
    ("🌐", "翻訳", "pages/7_🌐_翻訳.py", "日本語⇔多言語の翻訳とニュアンス調整を行います。"),
]

cols = st.columns(2)
for i, (icon, title, page, desc) in enumerate(features):
    with cols[i % 2]:
        with st.container(border=True):
            st.markdown(f"### {icon} {title}")
            st.write(desc)
            st.page_link(page, label=f"{title}を開く", icon=icon)

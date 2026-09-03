"""各ページ共通のサイドバー(APIキー・モデル設定)。"""

import streamlit as st

from utils.gemini_client import AVAILABLE_MODELS, DEFAULT_MODEL, get_api_key


def render_common_sidebar():
    with st.sidebar:
        st.subheader("⚙️ 設定")

        api_key_input = st.text_input(
            "Gemini APIキー",
            value=st.session_state.get("gemini_api_key", ""),
            type="password",
            help="環境変数 GEMINI_API_KEY が設定済みの場合は空欄のままでOKです。",
        )
        if api_key_input:
            st.session_state["gemini_api_key"] = api_key_input

        st.session_state.setdefault("gemini_model", DEFAULT_MODEL)
        st.selectbox(
            "モデル",
            AVAILABLE_MODELS,
            key="gemini_model",
        )

        if get_api_key():
            st.success("APIキーが設定されています", icon="✅")
        else:
            st.warning("APIキーが未設定です", icon="⚠️")

        st.divider()
        st.page_link("app.py", label="🏠 ホーム")

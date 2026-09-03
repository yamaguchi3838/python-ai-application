"""Gemini API呼び出しの共通ラッパー。"""

import os

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

AVAILABLE_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.6-pro",
    "gemini-3.6-flash-lite",
]

DEFAULT_MODEL = "gemini-3.6-flash"


def get_api_key() -> str | None:
    """セッション状態 -> 環境変数の順でAPIキーを取得する。"""
    return st.session_state.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY")


def get_client() -> genai.Client | None:
    api_key = get_api_key()
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


def generate_text(
    prompt: str,
    system_instruction: str | None = None,
    temperature: float = 0.7,
    model: str | None = None,
) -> str:
    """Gemini APIにプロンプトを送信し、生成テキストを返す。"""
    client = get_client()
    if client is None:
        raise RuntimeError(
            "Gemini APIキーが設定されていません。サイドバーからAPIキーを入力してください。"
        )

    config = types.GenerateContentConfig(
        temperature=temperature,
        system_instruction=system_instruction,
    )

    response = client.models.generate_content(
        model=model or st.session_state.get("gemini_model", DEFAULT_MODEL),
        contents=prompt,
        config=config,
    )
    return response.text or ""


def generate_text_stream(
    prompt: str,
    system_instruction: str | None = None,
    temperature: float = 0.7,
    model: str | None = None,
):
    """Gemini APIへのリクエストをストリーミングで返すジェネレータ。"""
    client = get_client()
    if client is None:
        raise RuntimeError(
            "Gemini APIキーが設定されていません。サイドバーからAPIキーを入力してください。"
        )

    config = types.GenerateContentConfig(
        temperature=temperature,
        system_instruction=system_instruction,
    )

    stream = client.models.generate_content_stream(
        model=model or st.session_state.get("gemini_model", DEFAULT_MODEL),
        contents=prompt,
        config=config,
    )
    for chunk in stream:
        if chunk.text:
            yield chunk.text

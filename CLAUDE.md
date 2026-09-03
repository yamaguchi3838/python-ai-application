# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A Streamlit multipage app that wraps the Gemini API to provide Japanese-language writing assistance tools (blog drafts, email replies, summarization, proofreading/rewriting, tone conversion, title generation, translation). UI text, prompts, and comments are in Japanese.

## Commands

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then set GEMINI_API_KEY

# Run
streamlit run app.py
```

There is no lint/test/build tooling configured in this repo (no test suite, linter, or CI config present).

## Architecture

- `app.py` — home page; registers page config and links to each feature page via `st.page_link`.
- `pages/N_<emoji>_<name>.py` — one Streamlit page per writing feature. Streamlit auto-discovers files in `pages/` and orders them by the leading number. Each page is self-contained: builds a form, assembles a Japanese prompt string, and calls into `utils/gemini_client.py`.
- `utils/gemini_client.py` — sole integration point with the Gemini API (`google-genai` SDK).
  - `get_api_key()` resolves the key from `st.session_state["gemini_api_key"]` first, then the `GEMINI_API_KEY` env var (loaded via `python-dotenv`).
  - `generate_text()` / `generate_text_stream()` are the two entry points pages use; both raise `RuntimeError` with a Japanese message if no API key is set — pages catch this and render it via `st.error`.
  - Model selection comes from `st.session_state["gemini_model"]`, defaulting to `DEFAULT_MODEL`; available models are listed in `AVAILABLE_MODELS`.
- `utils/sidebar.py` — `render_common_sidebar()` renders the shared sidebar (API key input, model selector) and is called at the top of every page, including `app.py`.

## Conventions when adding a new feature page

- Follow the existing page structure: `st.set_page_config(...)` → `render_common_sidebar()` → `st.form(...)` with inputs → on submit, validate required fields with `st.error(...)` → build a prompt string → call `generate_text_stream` (streamed into an `st.empty()` placeholder, the default for most pages) or `generate_text` (non-streaming; used only by タイトル案生成 for its short list output) → wrap the call in `try/except RuntimeError` to surface missing-API-key errors via `st.error`.
- Prompts follow a `# 見出し` (heading) structure listing the source content and conditions, end with an explicit output-format instruction (e.g. "◯◯のみを出力してください"), and explicitly tell the model not to alter meaning/facts when rewriting or translating.
- `temperature` is chosen per task and is not a single shared constant: low (0.3–0.4) for accuracy-sensitive tasks (要約, 校正, 翻訳), mid (0.5–0.6) for tone/email conversion, high (0.8–0.9) for creative generation (ブログ, タイトル案). Match this range when adding a similar task.
- Only add `st.session_state["last_<feature>_result"]` + `st.download_button(...)` if the output is a document meant to be saved/reused (as in ブログ記事作成, メール返信作成) — most pages (要約/校正/トーン変換/翻訳/タイトル案) just render the result inline and don't need this.
- Register the new page in the `features` list in `app.py`.
- Keep prompts and user-facing strings in Japanese, consistent with existing pages.

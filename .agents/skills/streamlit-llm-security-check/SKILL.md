---
name: streamlit-llm-security-check
description: Runs a security check on a Streamlit application that calls an LLM API (Gemini, OpenAI, Anthropic, etc.) and produces a Markdown security report covering secret/API-key handling, prompt-injection exposure, Streamlit-specific rendering risks (unsafe_allow_html, file uploads), dependency vulnerabilities, and access control. Use this whenever the user asks to "security check", "audit", "review for vulnerabilities", or "セキュリティチェック/監査/脆弱性チェック" a Streamlit + LLM app, even if they don't name a specific vulnerability class — the skill covers the full checklist. Also trigger when the user is about to deploy a Streamlit/LLM app publicly and asks "is this safe to ship" or similar, or asks about API key exposure, prompt injection, or XSS in a Streamlit app specifically.
---

# Streamlit × LLM API セキュリティチェック

Streamlit + LLM API(Gemini/OpenAI/Anthropic 等)アプリケーションに対して、このアプリ形態特有のリスクを重点的に洗い出し、Markdown 形式のセキュリティレポートを作成する。

## なぜこの観点が必要か

Streamlit + LLM アプリは一般的な Web アプリの脆弱性(SQLi など)よりも、次の2つの要因から生じる固有のリスクが大きい:

1. **セッション状態(`st.session_state`)や `.env` に API キーを直接置く設計が一般的** で、個人のプロトタイプがそのまま共有・公開デプロイされることが多く、キー漏洩やコスト濫用のリスクが高い。
2. **ユーザー入力がほぼそのまま LLM プロンプトに埋め込まれる** ため、プロンプトインジェクションや、LLM の出力を `unsafe_allow_html=True` などでそのまま画面に描画してしまう XSS のリスクが構造的に存在する。

汎用の脆弱性スキャナはこれらを見落としがちなので、このスキルは Streamlit と LLM SDK の組み合わせに特化したチェックリストを使う。

## 進め方

### 1. 技術スタックを確認する

まず対象アプリの構成を把握する。

```bash
find . -maxdepth 2 -iname "requirements*.txt" -o -iname "pyproject.toml" -o -iname "Pipfile" | head
grep -rlE "streamlit" --include="*.txt" --include="*.toml" .
```

どの LLM SDK を使っているか(`google-genai`, `openai`, `anthropic` など)、Streamlit のバージョン、マルチページ構成かどうかを確認する。プロジェクトに `CLAUDE.md` があれば読んでアーキテクチャを把握しておくと、どのファイルが API 呼び出しの共通口(このプロジェクトなら `utils/gemini_client.py` に相当するもの)かが分かり、チェックが早い。

### 2. 自動 recon を走らせる

`scripts/recon.sh` は、以下のチェックリストの多くの項目について機械的に検出できる部分をまとめて実行する grep ベースのスクリプト。手作業で同じ grep を毎回書き直す必要がないよう、まずこれを実行してから目視確認に進む。

```bash
bash scripts/recon.sh <対象アプリのルートディレクトリ>
```

出力される候補行はすべて「疑わしい箇所の一覧」であって確定した脆弱性ではない。誤検知(例えば `api_key` という変数名だが値は環境変数から取得している等)を必ず目視で確認してから報告すること — 確認を飛ばしてそのまま報告すると誤ったレポートになる。

### 3. チェックリストに沿って読み込む

`references/checklist.md` に6カテゴリの詳細なチェック観点がある。recon スクリプトでヒットしなかった項目(設計判断が必要なもの、例えば「公開デプロイなのに認証がない」など)は目視でしか見つからないので、必ずこのファイルを開いて全項目を確認すること。

カテゴリ:
1. シークレット・APIキー管理
2. プロンプトインジェクション / LLMへの入力信頼境界
3. Streamlit 特有のレンダリング・入力リスク(XSS, ファイルアップロード)
4. データの取り扱い・プライバシー・コスト濫用
5. 依存パッケージの脆弱性
6. アクセス制御・公開範囲

### 4. 重要度を付ける

各指摘には以下の観点で重要度をつける。判断に迷ったら「実際にこのアプリがどうデプロイされるか」を軸に考える — ローカルで自分だけが使うプロトタイプと、社内共有や公開デプロイされるアプリとでは、同じコードでもリスクの重大性が変わる(例: セッションに平文で API キーを持つこと自体は Streamlit の設計上避けにくいが、公開デプロイでキー入力欄がある場合は通信経路の保護やログ出力の有無を重点確認する)。

- **High**: 攻撃者が直接悪用でき、実害(キー漏洩、コスト濫用、データ漏洩、任意コード実行)につながる
- **Medium**: 特定の条件(公開デプロイ、悪意あるファイルアップロード等)が揃うと実害になる
- **Low**: ベストプラクティスからの逸脱だが、単体では実害に直結しにくい

不確かな指摘(「〜の可能性がある」レベル)は重要度を下げつつも報告に含めてよい。ただし推測であることが分かるように書く。

### 5. レポートを作成する

`references/report_template.md` の構成に従い、Markdown レポートを作成する。書き出し先は特に指定がなければ対象アプリのルートに `security-report.md` として保存し、加えてチャット上にも要点(High/Medium の指摘とその件数)を要約して伝える。

レポートの各指摘には必ず次を含める:
- 該当ファイルと行(`path/to/file.py:42` の形式)
- 何が問題か(具体的なコードや設定を引用)
- どう悪用され得るか(攻撃シナリオを一言で)
- 具体的な修正案(コード例つきが望ましい)

「〜に注意しましょう」のような一般論だけの指摘は避け、必ずそのリポジトリの実際のコードに即して書く。

## 参考ファイル

- `references/checklist.md` — 6カテゴリの詳細チェック項目。ステップ3で必ず参照する。
- `references/report_template.md` — レポートの出力フォーマット。
- `scripts/recon.sh` — 機械的に検出できる項目をまとめて grep する自動 recon スクリプト。

#!/usr/bin/env bash
# Streamlit x LLM API アプリ向けの機械的 recon。
# ヒットした行はすべて「目視確認が必要な候補」であり、確定した脆弱性ではない。
#
# Usage: ./recon.sh <target-dir>

set -uo pipefail

TARGET="${1:-.}"
cd "$TARGET" || { echo "ディレクトリが見つかりません: $TARGET" >&2; exit 1; }

section() {
  echo
  echo "== $1 =="
}

section "1. シークレットファイルの git 追跡状態"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git ls-files | grep -E '(^|/)\.env($|\.)|secrets\.toml$' \
    && echo "^ 上記ファイルがgit管理下にあります。意図的でなければ機密情報の漏洩リスクがあります。" \
    || echo "追跡されているシークレットファイルなし"
else
  echo "gitリポジトリではないためスキップ"
fi

section "2. ハードコードされていそうなAPIキー/シークレット"
grep -rnE "(api_key|apikey|secret|token|password)\s*=\s*[\"'][A-Za-z0-9_\-]{16,}[\"']" \
  --include="*.py" --exclude-dir=".venv" --exclude-dir="venv" --exclude-dir="node_modules" . \
  || echo "該当なし"

section "3. unsafe_allow_html の使用箇所(XSSリスク)"
grep -rn "unsafe_allow_html" --include="*.py" --exclude-dir=".venv" --exclude-dir="venv" . \
  || echo "該当なし"

section "4. eval/exec の使用箇所"
grep -rnE "\b(eval|exec)\s*\(" --include="*.py" --exclude-dir=".venv" --exclude-dir="venv" . \
  || echo "該当なし"

section "5. ファイルアップロードの取り扱い"
grep -rn "st.file_uploader" --include="*.py" --exclude-dir=".venv" --exclude-dir="venv" . \
  || echo "st.file_uploader の使用なし"

section "6. 例外の詳細をそのままUI/ログに出している箇所"
grep -rnE "st\.exception\(|traceback\.print_exc\(|traceback\.format_exc\(" \
  --include="*.py" --exclude-dir=".venv" --exclude-dir="venv" . \
  || echo "該当なし"

section "7. requirements / pyproject のバージョン指定"
for f in requirements.txt pyproject.toml Pipfile; do
  if [ -f "$f" ]; then
    echo "--- $f ---"
    cat "$f"
  fi
done

section "8. .streamlit/config.toml のセキュリティ関連設定"
if [ -f ".streamlit/config.toml" ]; then
  grep -E "enableCORS|enableXsrfProtection|showErrorDetails" .streamlit/config.toml \
    || echo "該当する設定項目の明示的な記述なし(=Streamlitのデフォルト値が適用される)"
else
  echo ".streamlit/config.toml が存在しません(=デフォルト設定)"
fi

section "9. 既知の脆弱性チェック(pip-audit)"
if [ -f "requirements.txt" ]; then
  if command -v pip-audit >/dev/null 2>&1; then
    pip-audit -r requirements.txt || true
  else
    echo "pip-audit が未インストールのため実行不可。'pip install pip-audit' 後に 'pip-audit -r requirements.txt' の実行を推奨(レポートには要手動確認と明記する)。"
  fi
else
  echo "requirements.txt が見つかりません"
fi

echo
echo "recon完了。ヒットした各行は references/checklist.md の該当カテゴリと照合しながら目視確認すること。"

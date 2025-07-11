#!/bin/bash

# PDF翻訳機能の自動テストスクリプト

set -e  # エラーが発生したら即座に終了

echo "=== PLaMo Translate CLI PDF翻訳機能 自動テスト ==="
echo

# 1. 環境確認
echo "1. 環境を確認しています..."

# 仮想環境の確認
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  仮想環境が有効化されていません。"
    echo "   以下のコマンドで有効化してください:"
    echo "   source .venv/bin/activate"
    echo
fi

# plamo-translateコマンドの確認
if ! command -v plamo-translate &> /dev/null; then
    echo "✗ plamo-translateコマンドが見つかりません。"
    echo "  pip install -e . を実行してください。"
    exit 1
fi

echo "✓ plamo-translateコマンドが利用可能です。"

# 2. PDF関連の引数確認
echo
echo "2. PDF関連の引数を確認しています..."
if plamo-translate --help | grep -q "pdf-input"; then
    echo "✓ --pdf-input引数が追加されています。"
else
    echo "✗ --pdf-input引数が見つかりません。"
    exit 1
fi

if plamo-translate --help | grep -q "pdf-output"; then
    echo "✓ --pdf-output引数が追加されています。"
else
    echo "✗ --pdf-output引数が見つかりません。"
    exit 1
fi

# 3. 必要なパッケージの確認
echo
echo "3. 必要なパッケージを確認しています..."
python -c "
try:
    import PyPDF2
    print('✓ PyPDF2がインストールされています')
except ImportError:
    print('✗ PyPDF2が必要です: pip install PyPDF2')
    exit(1)

try:
    import reportlab
    print('✓ reportlabがインストールされています')
except ImportError:
    print('✗ reportlabが必要です: pip install reportlab')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "必要なパッケージをインストールしてください:"
    echo "pip install PyPDF2 reportlab"
    exit 1
fi

# 4. テスト用PDFの作成
echo
echo "4. テスト用PDFファイルを作成しています..."
python scripts/create_test_pdf.py

if [ ! -f "scripts/test_paper.pdf" ]; then
    echo "✗ テスト用PDFファイルの作成に失敗しました。"
    exit 1
fi

echo "✓ テスト用PDFファイルを作成しました: scripts/test_paper.pdf"

# 5. 基本的なテキスト翻訳のテスト
echo
echo "5. 基本的なテキスト翻訳をテストしています..."

# サーバーが起動しているか確認
if ! pgrep -f "plamo-translate.*server" > /dev/null; then
    echo "サーバーを起動しています..."
    plamo-translate server &
    SERVER_PID=$!
    echo "サーバーPID: $SERVER_PID"
    
    # サーバーの起動を待つ
    echo "サーバーの起動を待っています..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "✓ サーバーが起動しました。"
            break
        fi
        if [ $i -eq 30 ]; then
            echo "✗ サーバーの起動がタイムアウトしました。"
            kill $SERVER_PID 2>/dev/null || true
            exit 1
        fi
        sleep 1
    done
    
    STARTED_SERVER=true
else
    echo "✓ サーバーが既に起動しています。"
    STARTED_SERVER=false
fi

# 簡単なテキスト翻訳のテスト
echo "簡単なテキスト翻訳をテストしています..."
echo "Hello world" | plamo-translate --from English --to Japanese > /tmp/test_output.txt 2>&1

if [ $? -eq 0 ]; then
    echo "✓ 基本的なテキスト翻訳が動作しています。"
    echo "  出力: $(cat /tmp/test_output.txt)"
else
    echo "✗ 基本的なテキスト翻訳でエラーが発生しました。"
    cat /tmp/test_output.txt
    if [ "$STARTED_SERVER" = true ]; then
        kill $SERVER_PID 2>/dev/null || true
    fi
    exit 1
fi

# 6. PDF翻訳のテスト
echo
echo "6. PDF翻訳をテストしています..."
plamo-translate --pdf-input scripts/test_paper.pdf --pdf-output scripts/test_paper_jp.pdf --from English --to Japanese

if [ $? -eq 0 ] && [ -f "scripts/test_paper_jp.pdf" ]; then
    echo "✓ PDF翻訳が成功しました！"
    echo "  入力: scripts/test_paper.pdf"
    echo "  出力: scripts/test_paper_jp.pdf"
    
    # 出力PDFのサイズを確認
    INPUT_SIZE=$(stat -c%s scripts/test_paper.pdf 2>/dev/null || stat -f%z scripts/test_paper.pdf)
    OUTPUT_SIZE=$(stat -c%s scripts/test_paper_jp.pdf 2>/dev/null || stat -f%z scripts/test_paper_jp.pdf)
    echo "  入力ファイルサイズ: $INPUT_SIZE bytes"
    echo "  出力ファイルサイズ: $OUTPUT_SIZE bytes"
else
    echo "✗ PDF翻訳でエラーが発生しました。"
    if [ "$STARTED_SERVER" = true ]; then
        kill $SERVER_PID 2>/dev/null || true
    fi
    exit 1
fi

# 7. クリーンアップ
echo
echo "7. クリーンアップしています..."
if [ "$STARTED_SERVER" = true ]; then
    echo "サーバーを停止しています..."
    kill $SERVER_PID 2>/dev/null || true
    echo "✓ サーバーを停止しました。"
fi

rm -f /tmp/test_output.txt

echo
echo "🎉 全てのテストが成功しました！"
echo
echo "生成されたファイル:"
echo "  - scripts/test_paper.pdf (テスト用入力PDF)"
echo "  - scripts/test_paper_jp.pdf (翻訳済みPDF)"
echo
echo "次のステップ:"
echo "  1. 出力PDFをPDFビューアで確認してください"
echo "  2. 翻訳の品質を確認してください"
echo "  3. 問題がなければPRを作成してください"

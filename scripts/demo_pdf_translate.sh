#!/bin/bash

# plamo-translate-cli PDF翻訳機能のデモスクリプト

# 使用方法を表示
echo "=== PLaMo Translate CLI PDF翻訳機能のデモ ==="
echo

# 必要なパッケージの確認
echo "1. 必要なパッケージのインストール状況を確認..."
python -c "
try:
    import PyPDF2
    import reportlab
    print('✓ PDF処理用パッケージがインストールされています')
except ImportError as e:
    print('✗ PDF処理用パッケージが不足しています:')
    print('  pip install PyPDF2 reportlab')
    print('  または')
    print('  pip install plamo-translate[pdf]')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "PDF処理用パッケージをインストールしてから再実行してください。"
    exit 1
fi

echo

# サンプルPDFファイルの確認
if [ ! -f "sample_paper.pdf" ]; then
    echo "2. サンプルPDFファイルが見つかりません。"
    echo "   翻訳したいPDFファイルを 'sample_paper.pdf' として保存してください。"
    echo
    echo "   または、以下のコマンドでPDFファイルを指定して実行してください:"
    echo "   plamo-translate --pdf-input your_paper.pdf --pdf-output your_paper_jp.pdf"
    exit 1
fi

echo "2. サンプルPDFファイルを確認しました: sample_paper.pdf"
echo

# 翻訳実行
echo "3. PDF翻訳を実行します..."
echo "   入力: sample_paper.pdf"
echo "   出力: sample_paper_jp.pdf"
echo

plamo-translate --pdf-input sample_paper.pdf --pdf-output sample_paper_jp.pdf --from English --to Japanese

if [ $? -eq 0 ]; then
    echo
    echo "✓ 翻訳が完了しました！"
    echo "  出力ファイル: sample_paper_jp.pdf"
    echo
    echo "他の言語に翻訳する場合:"
    echo "  plamo-translate --pdf-input sample_paper.pdf --pdf-output sample_paper_zh.pdf --from English --to Chinese"
else
    echo
    echo "✗ 翻訳でエラーが発生しました。"
    echo "  サーバーが起動していない場合は、別のターミナルで以下を実行してください:"
    echo "  plamo-translate server"
fi

# ローカル環境でのPDF翻訳機能テスト手順

## 1. 開発環境のセットアップ

### 依存関係のインストール
```bash
# 開発環境の同期
uv sync

# 仮想環境の有効化
source .venv/bin/activate

# PDF処理用パッケージの追加インストール
pip install PyPDF2 reportlab
```

### 開発版のインストール
```bash
# 開発版をeditableモードでインストール
pip install -e .

# または
pip install -e .[pdf]
```

## 2. テスト用PDFファイルの準備

### 簡単なテスト用PDFの作成
```bash
# テスト用のPDFを作成するPythonスクリプト
python scripts/create_test_pdf.py
```

### または既存のPDFファイルを使用
```bash
# 任意の英語PDFファイルを scripts/ ディレクトリに配置
cp /path/to/your/english_paper.pdf scripts/test_paper.pdf
```

## 3. テスト実行

### 基本的なテスト
```bash
# サーバーを起動（別のターミナルで）
plamo-translate server

# PDF翻訳をテスト（メインターミナルで）
plamo-translate --pdf-input scripts/test_paper.pdf --pdf-output scripts/test_paper_jp.pdf --from English --to Japanese
```

### デモスクリプトを使用したテスト
```bash
cd scripts/
# test_paper.pdfをsample_paper.pdfとしてコピー
cp test_paper.pdf sample_paper.pdf

# デモスクリプトを実行
./demo_pdf_translate.sh
```

## 4. 各段階での確認ポイント

### 4.1 インストール確認
```bash
# plamo-translateコマンドが利用可能か確認
plamo-translate --help

# PDF関連の引数が表示されるか確認
plamo-translate --help | grep pdf
```

### 4.2 PDF処理ライブラリの確認
```bash
python -c "
try:
    import PyPDF2
    import reportlab
    print('✓ PDF処理用パッケージOK')
except ImportError as e:
    print('✗ 不足:', e)
"
```

### 4.3 基本機能の確認
```bash
# 通常のテキスト翻訳が動作するか確認
echo "Hello world" | plamo-translate --from English --to Japanese
```

## 5. トラブルシューティング

### よくある問題と解決方法

1. **コマンドが見つからない**
   ```bash
   # パッケージを再インストール
   pip uninstall plamo-translate
   pip install -e .
   ```

2. **PDF処理でエラーが発生**
   ```bash
   # 依存関係を確認
   pip list | grep -E "(PyPDF2|reportlab)"
   
   # 再インストール
   pip install --force-reinstall PyPDF2 reportlab
   ```

3. **サーバーが起動しない**
   ```bash
   # ポートを確認
   lsof -i :8000
   
   # プロセスを終了
   pkill -f "plamo-translate"
   ```

## 6. 自動テストスクリプト

以下のスクリプトで一通りのテストを実行できます：
```bash
./scripts/test_pdf_functionality.sh
```

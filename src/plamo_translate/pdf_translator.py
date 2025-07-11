#!/usr/bin/env python3
"""
PDF翻訳機能を提供するモジュール
"""
import os
import tempfile
from pathlib import Path
from typing import Optional

try:
    import PyPDF2
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

import asyncio
from plamo_translate.clients.translate import MCPClient


class PDFTranslator:
    """PDFファイルの翻訳を行うクラス"""
    
    def __init__(self, from_lang: str = "English", to_lang: str = "Japanese"):
        if not PDF_AVAILABLE:
            raise ImportError(
                "PDF処理機能を使用するには、以下のパッケージをインストールしてください:\n"
                "pip install PyPDF2 reportlab"
            )
        self.from_lang = from_lang
        self.to_lang = to_lang
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """PDFからテキストを抽出"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n\n"
        except Exception as e:
            raise RuntimeError(f"PDFからのテキスト抽出に失敗しました: {e}") from e
        return text
    
    def translate_text(self, text: str) -> str:
        """テキストを翻訳"""
        try:
            # MCPClientを使用して翻訳を実行
            client = MCPClient(stream=False)
            
            # 翻訳用のメッセージを作成
            from_lang = f" lang={self.from_lang}" if self.from_lang else ""
            to_lang = f" lang={self.to_lang}" if self.to_lang else ""
            
            messages = [
                {
                    "role": "user",
                    "content": f"input{from_lang}\n{text}",
                },
                {
                    "role": "user",
                    "content": f"output{to_lang}\n",
                },
            ]
            
            # 翻訳を実行
            result = []
            async def run_translation():
                async for chunk in client.translate(messages):
                    result.append(chunk)
            
            asyncio.run(run_translation())
            return "".join(result)
            
        except Exception as e:
            raise RuntimeError(f"翻訳に失敗しました: {e}") from e
    
    def create_pdf_from_text(self, text: str, output_path: str) -> None:
        """翻訳されたテキストからPDFを作成"""
        try:
            # 日本語フォントを設定（システムにインストールされているフォントを使用）
            font_paths = [
                "/System/Library/Fonts/Hiragino Sans GB.ttc",  # macOS
                "/System/Library/Fonts/Arial Unicode.ttf",      # macOS
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            ]
            
            font_registered = False
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('JapaneseFont', font_path))
                        font_registered = True
                        break
                    except Exception:
                        continue
            
            if not font_registered:
                print("警告: 日本語フォントが見つかりませんでした。英語フォントを使用します。")
                font_name = "Helvetica"
            else:
                font_name = "JapaneseFont"
            
            # PDFドキュメントを作成
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # 日本語対応のスタイルを作成
            if font_registered:
                styles['Normal'].fontName = font_name
                styles['Heading1'].fontName = font_name
            
            story = []
            
            # テキストを段落に分割
            paragraphs = text.split('\n\n')
            for para_text in paragraphs:
                if para_text.strip():
                    para = Paragraph(para_text.strip(), styles['Normal'])
                    story.append(para)
                    story.append(Spacer(1, 0.2 * inch))
            
            # PDFを構築
            doc.build(story)
            
        except Exception as e:
            raise RuntimeError(f"PDFの作成に失敗しました: {e}") from e
    
    def translate_pdf(self, input_path: str, output_path: str) -> None:
        """PDFファイルを翻訳"""
        print(f"PDFファイルを読み込み中: {input_path}")
        
        # テキストを抽出
        text = self.extract_text_from_pdf(input_path)
        
        if not text.strip():
            raise RuntimeError("PDFからテキストを抽出できませんでした。画像ベースのPDFまたは保護されたPDFの可能性があります。")
        
        print(f"抽出されたテキスト量: {len(text)} 文字")
        print("翻訳を開始しています...")
        
        # テキストを翻訳
        translated_text = self.translate_text(text)
        
        print("翻訳されたPDFを作成中...")
        
        # 翻訳されたテキストからPDFを作成
        self.create_pdf_from_text(translated_text, output_path)
        
        print(f"翻訳完了: {output_path}")


def translate_pdf_file(input_path: str, output_path: str, from_lang: str = "English", to_lang: str = "Japanese") -> None:
    """PDFファイルを翻訳する関数"""
    translator = PDFTranslator(from_lang, to_lang)
    translator.translate_pdf(input_path, output_path)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("使用方法: python pdf_translator.py <input_pdf> <output_pdf> [from_lang] [to_lang]")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]
    from_lang = sys.argv[3] if len(sys.argv) > 3 else "English"
    to_lang = sys.argv[4] if len(sys.argv) > 4 else "Japanese"
    
    try:
        translate_pdf_file(input_pdf, output_pdf, from_lang, to_lang)
    except RuntimeError as e:
        print(f"エラー: {e}")
        sys.exit(1)

#!/usr/bin/env python3
"""
テスト用のPDFファイルを作成するスクリプト
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

def create_test_pdf():
    """テスト用のPDFファイルを作成"""
    
    # サンプルの英語論文テキスト
    content = """
    # Machine Learning in Natural Language Processing

    ## Abstract

    This paper presents a comprehensive study of machine learning techniques applied to natural language processing tasks. We explore various algorithms and their effectiveness in handling text classification, sentiment analysis, and language translation.

    ## Introduction

    Natural Language Processing (NLP) has become increasingly important in the era of big data and artificial intelligence. The ability to understand and process human language automatically has numerous applications in business, research, and daily life.

    Machine learning algorithms have proven to be particularly effective in NLP tasks. Traditional rule-based approaches often struggle with the complexity and ambiguity inherent in natural language. In contrast, machine learning methods can learn patterns from large datasets and generalize to new, unseen examples.

    ## Methodology

    Our research focuses on three main areas:

    1. **Text Classification**: We implemented several algorithms including Support Vector Machines, Random Forest, and Neural Networks to classify documents into predefined categories.

    2. **Sentiment Analysis**: We developed models to determine the emotional tone of text, distinguishing between positive, negative, and neutral sentiments.

    3. **Language Translation**: We explored neural machine translation approaches using transformer architectures.

    ## Results

    The experimental results demonstrate that deep learning approaches consistently outperform traditional methods across all three tasks. Neural networks showed particularly strong performance in sentiment analysis, achieving an accuracy of 92.3% on our test dataset.

    ## Conclusion

    This study confirms the effectiveness of machine learning in NLP applications. Future work will focus on improving model interpretability and reducing computational requirements for deployment in resource-constrained environments.
    """
    
    # PDFファイルを作成
    doc = SimpleDocTemplate("scripts/test_paper.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # テキストを段落に分割
    paragraphs = content.strip().split('\n\n')
    
    for para_text in paragraphs:
        if para_text.strip():
            # ヘッダーの処理
            if para_text.strip().startswith('# '):
                # メインタイトル
                title = para_text.strip()[2:]
                para = Paragraph(title, styles['Title'])
            elif para_text.strip().startswith('## '):
                # セクションタイトル
                title = para_text.strip()[3:]
                para = Paragraph(title, styles['Heading1'])
            else:
                # 通常のテキスト
                para = Paragraph(para_text.strip(), styles['Normal'])
            
            story.append(para)
            story.append(Spacer(1, 0.2 * inch))
    
    # PDFを構築
    doc.build(story)
    print("✓ テスト用PDFファイルを作成しました: scripts/test_paper.pdf")

if __name__ == "__main__":
    try:
        create_test_pdf()
    except ImportError:
        print("reportlabが必要です: pip install reportlab")
    except Exception as e:
        print(f"PDFの作成でエラーが発生しました: {e}")

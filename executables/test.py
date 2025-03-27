import pdfplumber

def pdf_to_text_with_pdfplumber(pdf_path):
    """
    pdfplumberを使用してPDFからテキストを抽出します。

    Args:
        pdf_path (str): PDFファイルのパス。

    Returns:
        str: 抽出されたテキスト。
        None: エラーが発生した場合。
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page_num, page in enumerate(pdf.pages):
                print(f"ページ {page_num + 1} を処理中...")
                text += page.extract_text() + "\n"
            return text
    except FileNotFoundError:
        print(f"指定されたファイルが見つかりません: {pdf_path}")
        return None
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

# PDFファイルのパスを指定
pdf_path = "/Users/ichikawatomohiro/Desktop/BNV_特許.pdf"

# PDFからテキストを抽出
text = pdf_to_text_with_pdfplumber(pdf_path)

if text:
    print("\n=== 抽出されたテキスト ===\n")
    print(text)
else:
    print("テキストを抽出できませんでした。")
    
    
    
    
    
import pytesseract
from pdf2image import convert_from_path
import os

def pdf_to_text_with_ocr(pdf_path, tesseract_cmd="/usr/local/bin/tesseract"):
    """
    OCRを使用してスキャンPDFからテキストを抽出します。

    Args:
        pdf_path (str): PDFファイルのパス。
        tesseract_cmd (str): Tesseractコマンドのパス。

    Returns:
        str: 抽出されたテキスト。
        None: エラーが発生した場合。
    """
    try:
        # Tesseractのパスを設定
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        # PDFを画像に変換
        pages = convert_from_path(pdf_path)
        text = ""

        # 各ページをOCRで処理
        for page_num, page in enumerate(pages):
            print(f"ページ {page_num + 1} を処理中...")
            text += pytesseract.image_to_string(page, lang="jpn") + "\n"

        return text

    except FileNotFoundError:
        print(f"指定されたファイルが見つかりません: {pdf_path}")
        return None
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

# PDFファイルのパスを指定
pdf_path = "/Users/ichikawatomohiro/Desktop/BNV_特許.pdf"

# OCRを使用してテキストを抽出
text = pdf_to_text_with_ocr(pdf_path)

if text:
    print("\n=== 抽出されたテキスト ===\n")
    print(text)
else:
    print("テキストを抽出できませんでした。")
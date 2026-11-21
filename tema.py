"""Arayüz teması: renkler, QSS stil sayfası ve rapor (HTML) yardımcıları."""
import os
import re
import tempfile

from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap, QPolygonF

# --- Renk paleti (koyu tema) ---
ARKAPLAN = "#0e1124"
KART = "#171b36"
KART_UST = "#1e2345"
KENAR = "#2b3160"
METIN = "#eef0ff"
SOLUK = "#9aa3d0"
VURGU = "#7c5cff"
VURGU_ACIK = "#9b82ff"
TURKUAZ = "#22d3ee"
YESIL = "#22c55e"
KIRMIZI = "#ef4444"
SARI = "#f59e0b"

_OK_DOSYASI = os.path.join(tempfile.gettempdir(), "miyt_ok_asagi.png")


def ok_ikonu_olustur():
    """ComboBox açılır oku için küçük bir PNG üretir ve yolunu döndürür."""
    try:
        pm = QPixmap(14, 14)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor(SOLUK), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawPolyline(QPolygonF([QPointF(3, 5), QPointF(7, 9), QPointF(11, 5)]))
        p.end()
        pm.save(_OK_DOSYASI, "PNG")
        return _OK_DOSYASI.replace("\\", "/")
    except Exception:
        return ""


def tema_qss():
    ok = ok_ikonu_olustur()
    ok_css = f"image: url({ok});" if ok else ""
    return f"""
    QMainWindow, QDialog, QMessageBox {{
        background: {ARKAPLAN};
    }}
    QWidget {{
        color: {METIN};
        font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
        font-size: 14px;
    }}
    QLabel {{ background: transparent; }}
    QToolTip {{
        background: {KART_UST}; color: {METIN}; border: 1px solid {KENAR};
        padding: 6px 8px; border-radius: 6px;
    }}

    /* Başlık alanı */
    #baslik {{ font-size: 26px; font-weight: 700; color: {METIN}; }}
    #altBaslik {{ font-size: 13px; color: {SOLUK}; }}
    #rozet {{
        background: rgba(124, 92, 255, 0.15); color: {VURGU_ACIK};
        border: 1px solid rgba(124, 92, 255, 0.45); border-radius: 12px;
        padding: 5px 12px; font-size: 12px; font-weight: 600;
    }}

    /* Kartlar (QGroupBox) */
    QGroupBox {{
        background: {KART};
        border: 1px solid {KENAR};
        border-radius: 16px;
        margin-top: 14px;
        padding: 22px 14px 14px 14px;
        font-weight: 600;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 16px;
        padding: 0 8px;
        color: {SOLUK};
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1px;
    }}

    /* Form alanları */
    QLineEdit, QSpinBox, QComboBox {{
        background: {ARKAPLAN};
        border: 1px solid {KENAR};
        border-radius: 10px;
        padding: 8px 12px;
        min-height: 22px;
        selection-background-color: {VURGU};
        color: {METIN};
    }}
    QLineEdit:hover, QSpinBox:hover, QComboBox:hover {{ border-color: #444c8a; }}
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
        border: 1px solid {VURGU};
        background: #121632;
    }}
    QComboBox::drop-down {{ border: none; width: 30px; }}
    QComboBox::down-arrow {{ {ok_css} width: 14px; height: 14px; }}
    QComboBox QAbstractItemView {{
        background: {KART_UST}; color: {METIN}; border: 1px solid {KENAR};
        selection-background-color: {VURGU}; outline: 0; padding: 4px;
    }}
    QFormLayout QLabel {{ color: {SOLUK}; font-size: 13px; }}

    /* Butonlar */
    QPushButton {{
        background: {VURGU};
        color: white;
        border: none;
        padding: 11px 20px;
        border-radius: 12px;
        font-size: 14px;
        font-weight: 600;
    }}
    QPushButton:hover {{ background: {VURGU_ACIK}; }}
    QPushButton:pressed {{ background: #6446e0; }}
    QPushButton:disabled {{ background: #2a2f55; color: #6f76a8; }}
    QPushButton#ikincil {{
        background: {KART_UST}; border: 1px solid {KENAR}; color: {METIN};
    }}
    QPushButton#ikincil:hover {{ background: #272d5a; border-color: #444c8a; }}
    QPushButton#evet {{
        background: {YESIL}; font-size: 17px; font-weight: 700; border-radius: 14px;
    }}
    QPushButton#evet:hover {{ background: #34d673; }}
    QPushButton#evet:pressed {{ background: #16a34a; }}
    QPushButton#hayir {{
        background: {KIRMIZI}; font-size: 17px; font-weight: 700; border-radius: 14px;
    }}
    QPushButton#hayir:hover {{ background: #f56565; }}
    QPushButton#hayir:pressed {{ background: #dc2626; }}
    QPushButton#basari {{ background: {YESIL}; }}
    QPushButton#basari:hover {{ background: #34d673; }}

    /* Durum kutusu */
    #statusLabel {{
        background: rgba(34, 211, 238, 0.10);
        color: {TURKUAZ};
        border: 1px solid rgba(34, 211, 238, 0.35);
        border-radius: 12px;
        padding: 11px 12px;
        font-size: 13px;
        font-weight: 600;
    }}

    /* Kamera */
    #cameraFrame {{
        background: #080a18;
        border: 1px solid {KENAR};
        border-radius: 14px;
        color: {SOLUK};
        font-size: 16px;
        font-weight: 600;
    }}

    /* Soru kartı */
    #soruNo {{
        background: rgba(124, 92, 255, 0.18); color: {VURGU_ACIK};
        border-radius: 10px; padding: 4px 12px;
        font-size: 12px; font-weight: 700; letter-spacing: 1px;
    }}
    #questionLabel {{
        color: {METIN}; font-size: 22px; font-weight: 600; padding: 6px 2px;
    }}

    /* İlerleme */
    QProgressBar {{
        background: {ARKAPLAN}; border: 1px solid {KENAR}; border-radius: 9px;
        text-align: center; color: {METIN}; font-size: 12px; font-weight: 700;
        min-height: 18px; max-height: 18px;
    }}
    QProgressBar::chunk {{
        border-radius: 8px;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {VURGU}, stop:1 {TURKUAZ});
    }}
    #ilerlemeYazi {{ color: {SOLUK}; font-size: 12px; }}

    /* Kaydırma çubukları */
    QScrollBar:vertical {{ background: transparent; width: 12px; margin: 2px; }}
    QScrollBar::handle:vertical {{ background: #3a4180; border-radius: 5px; min-height: 30px; }}
    QScrollBar::handle:vertical:hover {{ background: #4d56a8; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}

    /* Sonuç penceresi */
    QTextEdit {{
        background: {KART}; border: 1px solid {KENAR}; border-radius: 14px;
        padding: 14px; font-size: 14px; selection-background-color: {VURGU};
    }}
    #karar {{ border-radius: 16px; padding: 16px 20px; }}
    #istatKart {{
        background: {KART}; border: 1px solid {KENAR}; border-radius: 14px;
        padding: 10px 14px;
    }}
    #uyari {{ color: {SOLUK}; font-size: 12px; }}
    """


def rapor_html(mesaj):
    """Düz metin + basit <b> etiketli raporu, satır sonları korunan okunaklı HTML'e çevirir."""
    govde = []
    for satir in mesaj.split("\n"):
        ayrac = satir.strip()
        if ayrac and set(ayrac) <= set("=─-"):
            govde.append(f'<hr style="border:0; border-top:1px solid {KENAR};">')
            continue
        # Bölüm başlıkları (emoji ile başlayan, <b> içeren satırlar) vurgulansın
        if re.match(r"^\s{0,3}(🔹|🔍|🖼️|🔬|🏆)", satir):
            govde.append(f'<div style="color:{VURGU_ACIK}; font-size:16px; margin-top:8px;">{satir.strip()}</div>')
        else:
            govde.append(f'<div style="white-space:pre-wrap;">{satir if satir else "&nbsp;"}</div>')
    return (
        f'<div style="font-family:\'Segoe UI\'; color:{METIN}; line-height:140%;">'
        + "".join(govde)
        + "</div>"
    )

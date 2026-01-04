# Metoder for å skrive ut QR-koder til pdf'er.
import qrcode

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

from math import floor
from utils import now

""" 
Hva trenger vi her: 
En metode som genererer en PDF fra en liste med prefikser. 
En funksjon som genererer en QRcode med valgt størrelse og farger. OK

"""

QR_SIZE = 9 * mm
CELL_PADDING = 2 * mm
MARGIN = 4 * mm
FONT_SIZE = 6  # px
FONT = "Helvetica"

CELL_SIZE = QR_SIZE + 2 * CELL_PADDING
ROW_WIDTH = CELL_SIZE
ROW_HEIGHT = CELL_SIZE + 3 * FONT_SIZE

# Number of QR's
width, height = A4
QR_ROWS = floor((width - MARGIN) // ROW_WIDTH)
QR_COLS = floor((height - MARGIN) // ROW_HEIGHT)
MAX_PAGE_QR = QR_COLS * QR_ROWS

# TABLE
DASH = [height / 100, height / 25]  # 1px drawing, 4px space
LINE_WIDTH = 1  # px

# Debug info:
# print(width - 2 * MARGIN, height - 2 * MARGIN)
# print(ROW_WIDTH, ROW_HEIGHT)
# print(QR_ROWS, QR_COLS, MAX_PAGE_QR)


def make_qr(prefix: str, **kwargs):
    """Prints a QR-code with prefix as data"""

    fill = kwargs.get("fg", "White")
    back = kwargs.get("bg", "Black")
    QR = qrcode.QRCode(
        version=1,
        error_correction=qrcode.ERROR_CORRECT_H,
        box_size=3,
        border=1,
    )
    QR.add_data(prefix)
    QR.make(fit=True)
    return QR.make_image(fill_color=fill, back_color=back)


def draw_table(c: canvas.Canvas):
    c.saveState()
    points = []
    x = MARGIN
    y = MARGIN
    while x < width:
        points.append((x, 0, x, height))
        x += ROW_WIDTH
    while y < height:
        points.append((0, y, width, y))
        y += ROW_HEIGHT
    c.setDash(DASH)
    c.setLineWidth(LINE_WIDTH)
    c.setStrokeColorRGB(0.5, 0.5, 0.5)
    c.lines(points)
    c.restoreState()


def qr_pdf_generator(items: list[dict[str,str]], name: str = ""):
    if name:
        name = f"{name}_{now()}.pdf"
    else:
        name = f"{now()}.pdf"
    # print(prefixes)
    # print(name)
    c = canvas.Canvas(name, pagesize=A4)
    c.setFont("Helvetica", FONT_SIZE)

    for i, item in enumerate(items):
        if i % MAX_PAGE_QR == 0 and i != 0:
            draw_table(c)
            c.showPage()
            c.setFont("Helvetica", FONT_SIZE)
            x, y = 0, 0
            # print("New Page")
        x = ROW_WIDTH * (i % MAX_PAGE_QR % QR_ROWS) + MARGIN
        y = ROW_HEIGHT * (i % MAX_PAGE_QR // QR_ROWS) + MARGIN
        # Generer-QR-kode
        # print(
        #     prefix,
        #     x,
        #     y,
        #     i
        # )
        prefix = item.pop("prefix")
        img = make_qr(prefix, **item)

        # legg til PDF.
        c.drawInlineImage(
            img, x + CELL_PADDING, y + 3 * FONT_SIZE, width=QR_SIZE, height=QR_SIZE
        )

        t = c.beginText(x + CELL_PADDING, y + 2 * FONT_SIZE)
        size = c.stringWidth(prefix, FONT, FONT_SIZE)
        
        ratio = size / (ROW_WIDTH - 2 * CELL_PADDING)
        if ratio > 1.5:

            n = len(prefix)
            prefix = prefix[: n // 2] + "\n" + prefix[n // 2 :]
            ratio /= 2
            # print(prefix)

        if ratio > 1:  # tekst str
            c.setFontSize(floor(FONT_SIZE / ratio))

        t.textLines(prefix)

        c.drawText(t)
        # c.drawString(x,y, prefix)
        c.setFontSize(FONT_SIZE)

    draw_table(c)
    c.showPage()
    c.save()


if __name__ == "__main__":
    # img = make_qr("HEI0123", fill_color="Red", back_color="blue")
    # img.save("test.png")
    prefixes = [ {"prefix":f"HEI00{i}", "fg":"Black", "bg":"White"}  for i in range(MAX_PAGE_QR - 1)]
    prefixes.insert(0, {"prefix":f"qwertyuioølkioprtyqwertyuioølkioprty", "fg":"Black", "bg":"White"})
    prefixes.insert(0, {"prefix":f"qwertyuioølkioprty", "fg":"Black", "bg":"White"})
    prefixes.insert(0, {"prefix":f"qwertyui", "fg":"Black", "bg":"White"})

    qr_pdf_generator(prefixes)

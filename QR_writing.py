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

QR_SIZE = 6 * mm
CELL_PADDING = 3 * mm
MARGIN = 4 * mm
BORDER_SIZE = 1
FONT_SIZE = 6  # px
FONT = "Helvetica"

CELL_SIZE = QR_SIZE + 2 * CELL_PADDING
ROW_WIDTH = CELL_SIZE+MARGIN
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
print(width - 2 * MARGIN, height - 2 * MARGIN)
print(ROW_WIDTH, ROW_HEIGHT)
print(QR_ROWS, QR_COLS, MAX_PAGE_QR)


def make_qr(prefix: str, fill):
    """Prints a QR-code with prefix as data"""

    
    QR = qrcode.QRCode(
        version=1,
        error_correction=qrcode.ERROR_CORRECT_H,
        box_size=3,
        border=BORDER_SIZE,
    )
    QR.add_data(prefix)
    QR.make(fit=True)
    
    return QR.make_image(fill_color="Black", back_color=fill)


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
        name = "test.pdf"
    
    c = canvas.Canvas(name, pagesize=A4)
    c.setFont("Helvetica", FONT_SIZE)

    for i, item in enumerate(items):
        if i % MAX_PAGE_QR == 0 and i != 0:
            # draw_table(c)
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
        fill = item.get("fg", "255. 255. 255")
        back = item.get("bg","0. 0. 0")
        fill_int = tuple(int(x) for x in fill.split("."))
        fill = tuple(int(x)/255 for x in fill.split("."))
        back = tuple(int(x)/255 for x in back.split("."))
        
        img = make_qr(prefix,fill_int)
        c.saveState()
        # legg til PDF.
        # c.setFillColorRGB(*back)
        c.setFillColorRGB(*fill)
        c.rect(x + CELL_PADDING//2, y+CELL_PADDING//2, width= ROW_WIDTH - CELL_PADDING, height=CELL_SIZE+CELL_PADDING, fill=1)
        c.restoreState()
        c.drawInlineImage(
            img, x+MARGIN/2+CELL_PADDING, y + 3 * FONT_SIZE+CELL_PADDING, width=QR_SIZE, height=QR_SIZE
        )

        # c.setStrokeColorRGB(*back)
        t = c.beginText(x + CELL_PADDING, y + 2 * FONT_SIZE+CELL_PADDING//2)
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
    prefixes = [ {"prefix":f"HEI00{i}", "fg":"255. 0. 0", "bg":"255. 255. 255"}  for i in range(MAX_PAGE_QR - 1)]
    prefixes.insert(0, {"prefix":f"qwertyuioølkioprtyqwertyuioølkioprty","fg":"255. 220. 95", "bg":"255. 255. 255"})
    prefixes.insert(0, {"prefix":f"qwertyuioølkioprty", "fg":"255. 220. 95", "bg":"255. 255. 255"})
    prefixes.insert(0, {"prefix":f"qwertyui", "fg":"255. 220. 95", "bg":"255. 255. 255"})

    qr_pdf_generator(prefixes)

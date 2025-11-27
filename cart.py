import requests
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import io
import time

def obtener_imagen_scryfall(nombre_carta):
    url = f"https://api.scryfall.com/cards/named?exact={nombre_carta}"
    r = requests.get(url)
    if r.status_code != 200:
        print(f"❌ Carta no encontrada: {nombre_carta}")
        return None

    data = r.json()
    if 'image_uris' in data and 'normal' in data['image_uris']:
        img_url = data['image_uris']['normal']
    elif 'card_faces' in data and 'image_uris' in data['card_faces'][0]:
        img_url = data['card_faces'][0]['image_uris']['normal']
    else:
        print(f"⚠️ No hay imagen para {nombre_carta}")
        return None

    try:
        img_data = requests.get(img_url).content
        return io.BytesIO(img_data)
    except:
        return None

def crear_pdf_cartas(lista_cartas, archivo_salida="cartas.pdf"):
    c = canvas.Canvas(archivo_salida, pagesize=A4)
    ancho_pagina, alto_pagina = A4

    # Tamaño exacto de carta
    ancho_carta = 63.5 * mm
    alto_carta = 88 * mm

    cartas_por_fila = 3
    filas_por_pagina = 3
    cartas_por_pagina = cartas_por_fila * filas_por_pagina

    for i, nombre in enumerate(lista_cartas):
        if i % cartas_por_pagina == 0 and i != 0:
            c.showPage()

        col = i % cartas_por_fila
        fila = (i % cartas_por_pagina) // cartas_por_fila

        # Pegadas sin margen
        x = col * ancho_carta
        y = alto_pagina - (fila + 1) * alto_carta

        img = obtener_imagen_scryfall(nombre)
        if not img:
            continue

        try:
            c.drawImage(ImageReader(img), x, y, ancho_carta, alto_carta)
        except:
            print(f"⚠️ No se pudo colocar la imagen de {nombre}")

        time.sleep(0.3)

    c.save()
    print(f"✅ PDF generado: {archivo_salida}")

def leer_lista_cartas(archivo_txt):
    with open(archivo_txt, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

if __name__ == "__main__":
    archivo_entrada = "cartas.txt"
    archivo_salida = "mazo_magic.pdf"

    lista_cartas = leer_lista_cartas(archivo_entrada)
    crear_pdf_cartas(lista_cartas, archivo_salida)
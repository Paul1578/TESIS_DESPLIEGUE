from PIL import Image, ImageDraw, ImageFont
import random

FONT = '/tmp/DejaVuSerif-Bold.ttf'
OUT = '/var/lib/mayan/watch_folder'


def render_pdf(filename, lines, size=(1240, 1754)):
    img = Image.new('RGB', size, 'white')
    draw = ImageDraw.Draw(img)
    font_large = ImageFont.truetype(FONT, 56)
    font_normal = ImageFont.truetype(FONT, 40)
    y = 180
    first = True
    for text in lines:
        font = font_large if first else font_normal
        draw.text((100, y), text, fill='black', font=font)
        y += 110 if first else 95
        first = False
    img.save(f'{OUT}/{filename}', 'PDF')
    print('OK', filename)


render_pdf(
    'factura.pdf',
    [
        'FACTURA N° 001-001-000000123',
        'Emisor: INSUMOS AGRICOLAS DEL GUAYAS S.A.',
        'RUC: 0999999999001',
        'Fecha de Emision: 15/08/2026',
        'Cliente: DISTRIBUIDORA EL ROBLE CIA. LTDA.',
        'Descripcion: 50 sacos de fertilizante N-P-K',
        'Subtotal: $ 1,250.00    IVA: $ 150.00',
        'TOTAL: $ 1,400.00',
    ],
)

render_pdf(
    'contrato.pdf',
    [
        'CONTRATO DE SERVICIOS N° CS-2026-041',
        'Contratante: MUNICIPIO DE GUAYAQUIL',
        'Contratista: SERVICIOS GENERALES LEONARDO C.A.',
        'Objeto: Mantenimiento preventivo de equipos de oficina',
        'Plazo: 12 meses, a partir del 15/08/2026',
        'Valor del contrato: $ 24,000.00',
    ],
)

random.seed(42)
noise = Image.effect_noise((2400, 2400), 90).convert('RGB')
noise.save('/tmp/big.pdf', 'PDF')
print('OK big.pdf (prueba de subida grande)')

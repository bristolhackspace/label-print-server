from PIL import Image, ImageDraw, ImageFont
from datetime import date, timedelta
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send
from brother_ql import BrotherQLRaster
from brother_ql.devicedependent import label_type_specs
import time
import logging

logger = logging.Logger(__name__)

LABEL_SIZE = '62x100'
MODEL = "QL-570"
BACKEND = "linux_kernel"
PRINTER = "/dev/usb/lp0"
# BACKEND = "pyusb"
# PRINTER = "usb://0x04f9:0x2028"

PRINT_TO_FILE = False


def draw_label(name, description, expiry, serial=None):
    # Draw horizontally and rotate later
    dots = label_type_specs[LABEL_SIZE]["dots_printable"]
    image = Image.new("RGB", (dots[1], dots[0]), "white")
    draw = ImageDraw.Draw(image)

    font_small = ImageFont.truetype("DejaVuSansMono.ttf", size=40)
    font = ImageFont.truetype("DejaVuSansMono.ttf", size=60)
    font_medium = ImageFont.truetype("DejaVuSansMono.ttf", size=80)
    font_large = ImageFont.truetype("DejaVuSansMono.ttf", size=150)

    draw.text((dots[1]/2, 10), description, font=font_large, fill="black", anchor="ma")

    if not isinstance(expiry, str):
        expiry = expiry.strftime("%d %b %Y")
    
    draw.text((dots[1]/2, 200), "Do not hack until", font=font, fill="black", anchor="ma")
    draw.text((dots[1]/2, 280), expiry, font=font_large, fill="black", anchor="ma")

    draw.text((10, 450), "Owner:", font=font, fill="black")
    draw.text((10, 530), name, font=font_medium, fill="black")

    if serial is not None:
        serial_text = f"{serial:08d}"
        draw.text((dots[1]-10, dots[0]-10), serial_text, font=font_small, fill="black", anchor="rd")

    return image


def send_to_printer(image, cut=True):
    logger.info("printing label")

    if PRINT_TO_FILE:
        image.save("test.png")
        # Simulate printing time
        time.sleep(2.0)
    else:
        qlr = BrotherQLRaster(MODEL)
        qlr.exception_on_warning = True
        instructions = convert(
            qlr=qlr, 
            images=[image],    #  Takes a list of file names or PIL objects.
            label=LABEL_SIZE, 
            rotate='90',    # 'Auto', '0', '90', '270'
            threshold=70.0,    # Black and white threshold in percent.
            dither=False, 
            compress=False, 
            red=False,    # Only True if using Red/Black 62 mm label tape.
            dpi_600=False, 
            hq=True,    # False for low quality.
            cut=cut
        )

        send(instructions=instructions, printer_identifier=PRINTER, backend_identifier=BACKEND, blocking=True)
    logger.info("printing done")

def print_label(name, description, expiry, serial=None, cut=True):
    image = draw_label(name, description, expiry, serial)
    send_to_printer(image, cut)

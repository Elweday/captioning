from PIL import Image, ImageDraw, ImageFilter


def roundedImage(image, radius, back_color):
    image = image.copy()
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, image.size[0], image.size[1]), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius))
    return Image.composite(image, "transparent", mask)
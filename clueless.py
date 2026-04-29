# Various functions from Clueless that are extremely helpful, with some slight modifications
# https://github.com/pxlsspace/Clueless

import numpy as np
from PIL import Image, ImageColor

# https://github.com/pxlsspace/Clueless/blob/ddf69363ba786104ac36014740876b2930dbc471/src/utils/pxls/pxls_stats_manager.py#L183
def palettize_array(array, palette):
    """Convert a numpy array of palette indexes to a color numpy array
    (RGBA). If a palette is given, it will be used to map the array, if not
    the current pxls palette will be used"""
    colors_list = []
    for color in palette:
        rgb = ImageColor.getcolor(color, "RGBA")
        colors_list.append(rgb)
    colors_dict = dict(enumerate(colors_list))
    colors_dict[255] = (0, 0, 0, 0)

    img = np.stack(np.vectorize(colors_dict.get)(array), axis=-1)
    return img.astype(np.uint8)

# https://github.com/pxlsspace/Clueless/blob/ddf69363ba786104ac36014740876b2930dbc471/src/utils/image/image_utils.py#L249
def hex_to_rgb(hex: str, mode="RGB"):
    """convert a hex color string to a RGB tuple
    ('#ffffff' -> (255,255,255) or 'ffffff' -> (255,255,255)"""
    if "#" in hex:
        return ImageColor.getcolor(hex, mode)
    else:
        return ImageColor.getcolor("#" + hex, mode)


# https://github.com/pxlsspace/Clueless/blob/ddf69363ba786104ac36014740876b2930dbc471/src/utils/pxls/template.py#L113
def get_rgba_palette(palette):
    res = []
    for i in palette:
        c = hex_to_rgb(i, "RGBA")
        res.append(c)
    return np.array(res)

# https://github.com/pxlsspace/Clueless/blob/ddf69363ba786104ac36014740876b2930dbc471/src/utils/pxls/template.py#L145
def _fast_reduce(array, palette, dist_func):
    cache = {}
    res = np.empty(array.shape[:2], dtype=np.uint8)
    width = array.shape[1]
    for idx in range(array.shape[0] * array.shape[1]):
        i = idx // width
        j = idx % width
        alpha = array[i, j, 3]
        if alpha > 128:
            color = array[i, j, :3]
            color_bit = (np.uint32(color[0]) << 16) + (np.uint32(color[1]) << 8) + color[2]
            if color_bit in cache:
                mapped_color_idx = cache[color_bit]
                # if mapped_color_idx == 19:
                #     print(color)
            else:
                mapped_color_idx = dist_func(color, palette)
                cache[color_bit] = mapped_color_idx
            # if color[0] == 20 or color[0] == 141:
            #     print(color_bit, color, mapped_color_idx)
            #     print(color[0] << 16, color[1] << 8, color[2])
        else:
            mapped_color_idx = 255
        res[i, j] = mapped_color_idx
    return res


# https://github.com/pxlsspace/Clueless/blob/ddf69363ba786104ac36014740876b2930dbc471/src/utils/pxls/template.py#L167
def reduce(array: np.array, palette: np.array) -> np.array:
    """Convert an image array of RGBA colors to an array of palette index
    matching the nearest color in the given palette

    Parameters
    ----------
    array: a numpy array of RGBA colors (shape (h, w, 4))
    palette: a numpy array (shape (h, w, 1))
    matching: the algorithm to use to match the colors
    (fast = Euclidean distance, accurate = CIEDE2000)
    """
    # convert to array just in case
    palette = np.asarray(palette, dtype=np.uint8)
    array = np.asarray(array, dtype=np.uint8)

    # print(palette)
    
    # Get rid of the alpha component
    # palette = palette[:, :3]

    dist_func = nearest_color_idx_euclidean
    
    res = _fast_reduce(array, palette, dist_func)

    return res


# https://github.com/pxlsspace/Clueless/blob/ddf69363ba786104ac36014740876b2930dbc471/src/utils/pxls/template.py#L222
def nearest_color_idx_euclidean(color, palette) -> int:
    """
    Find the nearest color to `color` in `palette` using the Euclidean distance

        Parameters
    ----------
    color: a rgb ndarray of uint8 of shape (3,)
    palette: a rgb ndarray of uint8 of shape (palette_size,3)

    """
    distances = np.sum((palette - color) ** 2, axis=1)
    minn = np.argmin(distances)
    # if minn == 19:
    #     print(palette)
    #     print(color)
    #     print(distances)
    # hacky workaround to fix mauve being detected as grey
    if minn == 1 and distances[0] == 372:
        return 13
    return minn


# https://github.com/pxlsspace/Clueless/blob/ddf69363ba786104ac36014740876b2930dbc471/src/utils/pxls/template.py#L123
def stylize(style, stylesize, palette, glow_opacity=0):
    res = np.zeros((len(palette), stylesize, stylesize, 4))
    for i in range(len(palette)):
        cstyle = np.zeros((stylesize, stylesize, 4))
        glow_value = np.copy(palette[i])
        glow_value[3] = glow_opacity * 255
        cstyle[:, :] = glow_value
        for j in range(stylesize):
            for k in range(stylesize):
                if style[i, j, k]:
                    cstyle[j, k] = palette[i]
                    # change the alpha channel to the value in the style
                    cstyle[j, k, 3] = style[i, j, k]
        res[i] = cstyle
    return res


# https://github.com/pxlsspace/Clueless/blob/ddf69363ba786104ac36014740876b2930dbc471/src/utils/pxls/template.py#L237C1-L246C15
def fast_templatize(n, m, st, red, style_size):
    res = np.zeros((style_size * n, style_size * m, 4), dtype=np.uint8)
    for i in range(n):
        for j in range(m):
            if red[i, j] != 255:  # non-alpha values
                res[
                    style_size * i : style_size * i + style_size,
                    style_size * j : style_size * j + style_size,
                ] = st[red[i][j]]
    return res


# https://github.com/pxlsspace/Clueless/blob/ddf69363ba786104ac36014740876b2930dbc471/src/utils/pxls/template.py#L249
def templatize(
    style: dict, image: Image.Image, palette
) -> np.ndarray:
    style_array = style["array"]
    style_size = style["size"]
    red_palette = [hex_to_rgb(i) for i in palette]
    # print(red_palette)
    image_array = np.array(reduce(image, red_palette))
    # for i in range(len(image_array)):
    #     print(image_array[i])
    # print(image_array[50])
    n = image_array.shape[0]
    m = image_array.shape[1]
    rgba_palette = get_rgba_palette(palette)

    st = stylize(style_array, style_size, rgba_palette)
    res = fast_templatize(n, m, st, image_array, style_size)
    return res


# https://github.com/pxlsspace/Clueless/blob/ddf69363ba786104ac36014740876b2930dbc471/src/utils/pxls/template.py#L24
def parse_style_image(style_image: Image.Image):
    try:
        img_array = np.array(style_image.convert("RGBA"))
        alpha = img_array[:, :, 3]
        symbols_per_line = 16
        style_size = int(style_image.width / symbols_per_line)
        res = np.zeros((symbols_per_line * symbols_per_line, style_size, style_size))
        color_idx = 0
        for i in range(symbols_per_line):
            for j in range(symbols_per_line):
                x0 = i * style_size
                y0 = j * style_size
                x1 = x0 + style_size
                y1 = y0 + style_size
                res[color_idx] = alpha[x0:x1, y0:y1]
                color_idx += 1
        return res, style_size

    except Exception:
        return None, None

# https://github.com/pxlsspace/Clueless/blob/ddf69363ba786104ac36014740876b2930dbc471/src/utils/pxls/template.py#L46
def get_style_from_name(style_name):
    style_image = Image.open(f"other/{style_name}.png")
    style_array, style_size = parse_style_image(style_image)
    style = {"name": style_name, "size": style_size, "array": style_array}
    return style
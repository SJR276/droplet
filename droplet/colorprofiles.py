from enum import Enum

class ColorProfile(Enum):
    STICKORDER = 1
    ORIGINDIST = 2

def blue_through_red_stick_order(colors):
    """Takes an array/list where the data-type is a 3-tuple
    of float types and assigns each element an (r,g,b) value
    corresponding to the gradient from pure blue through to
    pure red.

    Arguments:
    ----------
    colors -- A list or array where `dtype=(float, 3)`.

    Returns:
    --------
    The modified `colors` container.
    """
    ncolors = len(colors) - 1
    for idx in range(ncolors):
        ratio = 2*idx/ncolors
        blue = max(0, 1-ratio)
        red = max(0, ratio-1)
        green = 1 - blue - red
        colors[idx] = red, green, blue
    return colors

from enum import Enum

class ColorProfile(Enum):
    BLUETHROUGHRED = 1
    THERMAL = 2

def blue_through_red(colors):
    """Takes an array/list where the data-type is a 3-tuple
    of float types and assigns each element an (r,g,b) value
    corresponding to the gradient from pure blue through to
    pure red.

    Parameters:
    -----------
    colors -- A list or array where `dtype=(float, 3)`.

    Returns:
    --------
    The modified `colors` container.
    """
    ncolors = len(colors)
    for idx in range(ncolors):
        ratio = 2*idx/ncolors
        blue = max(0, 1-ratio)
        red = max(0, ratio-1)
        green = 1 - blue - red
        colors[idx] = red, green, blue
    return colors

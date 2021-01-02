"""  The `printer` is a collection of object that print information to the console.
Those objects can print simple text, forms, or even complex art and images. """

# General printing
from .general import (
    KarmaRexBanner,
    DrawingBox,
    HeavyDrawingBox,
    LightDrawingBox,
)

# Printing information about reddit object (subreddits, comments, etc.)
from .reddit import (
    PrintSubreddit,
    PrintComment,
)

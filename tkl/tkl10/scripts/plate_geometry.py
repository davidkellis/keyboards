"""Generic diagnostic plate apertures; actual stabilizer fit remains unverified."""
from shapely.geometry import box
from shapely.ops import unary_union

def stabilizer_apertures(x, y, span):
    shapes=[]
    for sign in (-1, 1):
        cx=x+sign*span/2
        shapes.extend([box(cx-3.375,y-6.25,cx+3.375,y+6.15),
                       box(cx-4.25,y-.8,cx+4.25,y+2),
                       box(cx-1.55,y+6.1,cx+1.55,y+7.4)])
    return unary_union(shapes)

def switch_aperture(x, y):
    return box(x-7.075,y-7.075,x+7.075,y+7.075)

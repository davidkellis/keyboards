"""Bonded half-lap splits with a glue gap, cut entirely inside the full design."""
from shapely.geometry import box
import cadquery as cq


def lap_split(shape,left_polygon,domain,z_bottom,z_top,lap_width,gap,polygon_solid):
    mid=(z_bottom+z_top)/2
    core_left=left_polygon.buffer(-lap_width/2-gap/2,join_style=2)
    core_right=domain.difference(left_polygon.buffer(lap_width/2+gap/2,join_style=2))
    lower_left=left_polygon.buffer(lap_width/2-gap/2,join_style=2)
    upper_right=domain.difference(left_polygon.buffer(-lap_width/2+gap/2,join_style=2))
    outside=[left_polygon.buffer(-gap/2,join_style=2),
             domain.difference(left_polygon.buffer(gap/2,join_style=2))]
    halves=[]
    for side,core,lap in [('left',core_left,lower_left),('right',core_right,upper_right)]:
        j=0 if side=='left' else 1
        masks=[polygon_solid(core,z_bottom-.01,z_top-z_bottom+.02),
               polygon_solid(outside[j],-20,z_bottom+20),
               polygon_solid(outside[j],z_top,50-z_top)]
        if j==0:masks.append(polygon_solid(lap,z_bottom,mid-gap/2-z_bottom))
        else:masks.append(polygon_solid(lap,mid+gap/2,z_top-mid-gap/2))
        mask=masks[0].fuse(*masks[1:]).clean()
        half=shape.intersect(mask).clean()
        assert half.isValid() and len(half.Solids())==1,(side,'split is disconnected')
        assert half.cut(shape).Volume()<1e-4,'Joint must not enlarge outside envelope'
        halves.append(half)
    assert halves[0].intersect(halves[1]).Volume()<1e-4
    return halves,dict(type='bonded half-lap',overlap_width_mm=lap_width,glue_gap_mm=gap,
                      missing_joint_volume_mm3=shape.Volume()-sum(s.Volume() for s in halves),
                      requires_bonding=True,halves=[dict(side=label,bounds_mm=[s.BoundingBox().xlen,s.BoundingBox().ylen,s.BoundingBox().zlen]) for label,s in zip(('left','right'),halves)])


def export_splits(case,upper,CW,CD,W,D,left_polygon,plate_bottom,plate_top,floor,polygon_solid,flat_export,out):
    case_domain=box(-10,-10,CW+10,CD+10)
    case_left=box(-10,-10,CW/2,CD+10)
    case_halves,cr=lap_split(case,case_left,case_domain,0,floor,6,.2,polygon_solid)
    upper_halves,ur=lap_split(upper,left_polygon,box(-10,-10,W+10,D+10),plate_bottom,plate_top,4,.2,polygon_solid)
    for name,halves in [('case',case_halves),('plate',upper_halves)]:
        for side,s in zip(('left','right'),halves):flat_export(s,f'{name}-{side}.stl')
    # Reference in common assembly coordinates, unlike bed-normalized STL halves.
    for name,halves in [('base',case_halves),('plate',upper_halves)]:
        asm=cq.Assembly(name=name+'-joined')
        for side,s,c in zip(('left','right'),halves,[(.25,.4,.7),(.6,.7,.85)]):asm.add(s,name=side,color=cq.Color(*c))
        asm.export(str(out/(name+'-split.step')))
    return dict(base=cr,upper=ur,note='Bond both seams before installing components. The continuous FR4 and distributed screws bridge the joined plastic halves; printed PCB halves do not.')

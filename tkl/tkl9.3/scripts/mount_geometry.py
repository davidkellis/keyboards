"""Coordinated M2 plate/PCB/base clamp stack and floor reinforcement."""
import cadquery as cq
import math


def cylinder(x,y,z,r,h):
    return cq.Workplane('XY').circle(r).extrude(h).translate((x,y,z)).val()


def block(x,y,z,w,d,h):
    return cq.Workplane('XY').box(w,d,h,centered=False).translate((x,y,z)).val()


def hexagon(x,y,z,af,height):
    radius=af/math.sqrt(3)
    points=[(x+radius*math.cos(i*math.pi/3),y+radius*math.sin(i*math.pi/3)) for i in range(6)]
    return cq.Workplane('XY').polyline(points).close().extrude(height).translate((0,0,z)).val()


def add_case_mounts(case, config, place, bottom_parts, battery, W, D, CW, CD, floor):
    m=config['mounting'];posts=[];records=[];hardware=[]
    # Ribs sit above the floor and are trimmed around component clearance boxes.
    # They add material only where it fits; no pad, pin, battery or outside change.
    ri=config['integrated_upper'];rw=ri['floor_rib_width_mm'];rh=ri['floor_rib_height_mm']
    ribs=[]
    for y in (29,47,68):ribs.append(block(2,y,floor-.05,CW-4,rw,rh+.05))
    for x in (45,95,155,215,275,310):ribs.append(block(x,2,floor-.05,rw,72,rh+.05))
    ribs=cq.Compound.makeCompound(ribs)
    clear=[]
    for ref,s in bottom_parts:
        b=s.BoundingBox();gap=.45
        clear.append(block(b.xmin-gap,b.ymin-gap,b.zmin-gap,
                           b.xlen+2*gap,b.ylen+2*gap,b.zlen+2*gap))
    b=battery.BoundingBox()
    clear.append(block(b.xmin-.5,b.ymin-.5,b.zmin-.5,b.xlen+1,b.ylen+1,b.zlen+1))
    clear.append(place(block(-10,-10,-.4,W+20,D+20,20)))
    ribs=ribs.cut(*clear)
    case=case.fuse(ribs).clean()
    for p in m['points']:
        x,y=p['xy'];r=m['case_post_radius_mm']
        if p['support']=='rear-wall bracket':
            post=place(block(x-r,y-r,-3.5,2*r,D+2-y+r,3.5))
            post=post.intersect(block(0,0,floor-.05,CW,CD,30))
        else:
            post=place(cylinder(x,y,-25,r,25))
            post=post.intersect(block(0,0,floor-.05,CW,CD,30))
        assert post.isValid() and len(post.Solids())==1
        for ref,s in bottom_parts:
            assert post.intersect(s).Volume()<1e-5,(p['ref'],ref,'post collision')
        assert post.intersect(battery).Volume()<1e-5,(p['ref'],'battery')
        posts.append(post)
    case=case.fuse(*posts).clean()
    for p in m['points']:
        x,y=p['xy'];af=m['nut_pocket_across_flats_mm']
        # Side-loaded nut has a 1 mm printed roof. An open-top nut well would
        # clamp only plate/PCB, not the base; this roof positively captures it.
        seat=m['nut_seat_z_mm'];roof=-1.0
        pocket=hexagon(x,y,seat,af,roof-seat)
        entry=block(x,y-af/2,seat,10,af,roof-seat)
        bore=cylinder(x,y,m['screw_tip_clearance_z_mm'],m['screw_clearance_mm']/2,
                      -m['screw_tip_clearance_z_mm']+.05)
        case=case.cut(place(pocket),place(entry),place(bore)).clean()
        nut=hexagon(x,y,roof-m['nut_height_mm'],m['nut_across_flats_mm'],m['nut_height_mm'])
        nut=nut.cut(cylinder(x,y,roof-m['nut_height_mm']-.1,1, m['nut_height_mm']+.2))
        headseat=m['screw_head_seat_z_mm']
        screw=cylinder(x,y,headseat-m['screw_length_mm'],1,m['screw_length_mm'])
        screw=screw.fuse(cylinder(x,y,headseat,m['screw_head_diameter_mm']/2,m['screw_head_height_mm']))
        hardware.extend([(p['ref']+' screw',place(screw)),(p['ref']+' nut',place(nut))])
        records.append(dict(**p,nut_roof_thickness_mm=1.0,nut_entry='from +X before PCB installation',
                            screw_tip_board_z_mm=headseat-m['screw_length_mm'],
                            nominal_nut_thread_engagement_mm=m['nut_height_mm']))
    assert case.isValid() and len(case.Solids())==1
    for label,s in hardware:
        assert case.intersect(s).Volume()<1e-5,(label,'hardware/case collision')
        assert battery.intersect(s).Volume()<1e-5,(label,'hardware/battery collision')
    return case,records,hardware


def mount_spacers(config,T,plate_bottom):
    m=config['mounting']
    return [cylinder(*p['xy'],T,m['plate_spacer_radius_mm'],plate_bottom-T+.01)
            for p in m['points']]


def drill_upper(upper,config):
    m=config['mounting'];tools=[]
    for p in m['points']:
        x,y=p['xy']
        tools.append(cylinder(x,y,-.1,m['screw_clearance_mm']/2,10))
        tools.append(cylinder(x,y,m['screw_head_seat_z_mm'],m['plate_head_recess_diameter_mm']/2,10))
    return upper.cut(*tools).clean()

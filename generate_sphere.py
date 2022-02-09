import math

if __name__ == '__main__':
    side_u = 64
    side_v = 32

    vp = []
    f = []

    vp.append([0.0, 1.0, 0.0])
    for i in range(side_v):
        v = (i + 0.5) / side_v
        theta = v * math.pi
        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        for j in range(side_u):
            u = (j + 0.5) / side_u
            phi = u * 2.0 * math.pi

            p = [-sin_theta * math.sin(phi), cos_theta, sin_theta * math.cos(phi)]
            vp.append(p)
    vp.append([0.0, -1.0, 0.0])

    for i in range(side_u):
        left = 1 + i
        right = 1 + ((i + 1) % side_u)
        f.append([0, right, left])
    
    for i in range(side_v - 1):
        for j in range(side_u):
            up_left = 1 + i * side_u + j
            up_right = 1 + i * side_u + ((j + 1) % side_u)
            down_left = up_left + side_u
            down_right = up_right + side_u
            f.append([up_left, down_right, down_left])
            f.append([up_left, up_right, down_right])
    
    last = len(vp) - 1
    for i in range(side_u):
        left = 1 + (side_v - 1) * side_u + i
        right = 1 + (side_v - 1) * side_u + ((i + 1) % side_u)
        f.append([left, right, last])
    
    obj_file = open('sphere.obj', 'w')
    v_count = len(vp)
    f_count = len(f)
    lines = []
    for i in range(v_count):
        lines.append('v %f %f %f\n' % tuple(vp[i]))
    for i in range(v_count):
        lines.append('vn %f %f %f\n' % tuple(vp[i]))
    for i in range(f_count):
        lines.append('f %d//%d %d//%d %d//%d\n' % (f[i][0]+1,f[i][0]+1,f[i][1]+1,f[i][1]+1,f[i][2]+1,f[i][2]+1))
    obj_file.writelines(lines)
    obj_file.close()

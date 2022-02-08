import sys
import os.path as osp


def string_to_index(string):
    try:
        return int(string) - 1
    except:
        return -1

# convert 'v/vt/vn' to index list [v, vt, vn], start from 0
def parse_attr_string(vertex_string):
    vertex_attributes = [-1, -1, -1]
    string = vertex_string[0:]
    for i in range(3):
        pos = string.find('/')
        if pos < 0:
            vertex_attributes[i] = string_to_index(string)
            break
        else:
            vertex_attributes[i] = string_to_index(string[0: pos])
            string = string[pos+1:]
    return vertex_attributes


def parse_obj(lines):
    v_lines = []
    vn_lines = []
    vt_lines = []
    meshes = {}
    mtllib = ''

    usemtl = ''
    for i in range(len(lines)):
        line = lines[i].strip()
        substrs = line.split()
        substr_count = len(substrs)
        if substr_count == 0:
            continue
        if substrs[0] == 'mtllib':
            mtllib = substrs[1]
        elif substrs[0] == 'v':
            v_lines.append(line)
        elif substrs[0] == 'vn':
            vn_lines.append(line)
        elif substrs[0] == 'vt':
            vt_lines.append(line)
        elif substrs[0] == 'usemtl':
            usemtl = line
        elif substrs[0] == 'f':
            if substr_count != 4:
                raise Exception('only support triangle')
            if usemtl not in meshes:
                meshes[usemtl] = []
            meshes[usemtl].append(line)
    
    if len(v_lines) == 0:
        raise Exception('no vertices')
    
    if len(vn_lines) == 0:
        vn_lines.append('vn 1 1 1')
        print('[warning] no surface normals, add default')
    
    if len(vt_lines) == 0:
        vt_lines.append('vt 0 0')
        print('[warning] no texture coordinates, add default')
    
    return mtllib, v_lines, vn_lines, vt_lines, meshes

def parse_mtl(mtllib):
    materials = {}
    mtl = ''
    
    try:
        file = open(mtllib, 'r')
        lines = file.readlines()
        file.close()

        for i in range(len(lines)):
            line = lines[i].strip()
            substrs = line.split()
            if len(substrs) == 0:
                continue
            if substrs[0] == 'newmtl':
                mtl = substrs[1]
                if mtl not in materials:
                    materials[mtl] = ['1', '1', '1', 'null']
            elif substrs[0] == 'Kd':
                materials[mtl][0:3] = substrs[1:]
            elif substrs[0] == 'map_Kd':
                materials[mtl][3] = substrs[1]
    except:
        print("[warning] invalid mtllib file: %s" % mtllib)
    
    if len(materials) == 0:
        materials[''] = ['1', '1', '1', 'null']
    
    return materials

def convert_to_rendering(materials, v_lines, vn_lines, vt_lines, meshes):
    mtl_list = []
    mtl_index = {}

    rendering_lines = []
    
    for name, mtl in materials.items():
        if name not in mtl_index:
            mtl_index[name] = len(mtl_list)
            mtl_list.append(mtl)
    
    for i in range(len(mtl_list)):
        rendering_lines.append('mtl %s %s %s %s\n' % tuple(mtl_list[i]))
    
    new_v_lines = []
    new_vn_lines = []
    new_meshes = {}
    
    g_list = [] # geometry attribute: v/vn
    g_index = {} # index of v/vn
    
    for mtl, faces in meshes.items():
        mtl_name = ''
        if len(mtl) > 0:
            mtl_name = mtl.split()[1]
        new_meshes[mtl_index[mtl_name]] = []
        for face in faces:
            attrs = face.split()[1:]
            face_attr = []
            for attr in attrs:
                index = parse_attr_string(attr)
                if index[1] < 0:
                    index[1] = 0
                if index[2] < 0:
                    index[2] = 0
                g_key = '%d %d' % (index[0], index[2])
                if g_key not in g_index:
                    g_index[g_key] = len(g_list)
                    g_list.append(g_key)
                    new_v_lines.append(v_lines[index[0]])
                    new_vn_lines.append(vn_lines[index[2]])
                face_attr.append('%d|%d' % (g_index[g_key], index[1]))
            new_meshes[mtl_index[mtl_name]].append(face_attr)
    
    for i in range(len(new_v_lines)):
        rendering_lines.append('%s\n' % new_v_lines[i])
    for i in range(len(new_vn_lines)):
        rendering_lines.append('%s\n' % new_vn_lines[i])
    for i in range(len(vt_lines)):
        rendering_lines.append('%s\n' % vt_lines[i])
    
    for mtl, faces in new_meshes.items():
        rendering_lines.append('usemtl %s\n' % mtl)
        for face in faces:
            rendering_lines.append('f %s %s %s\n' % tuple(face))
    
    return rendering_lines
    

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: python obj2rendering.py <.obj file path>")
    else:
        try:
            file = open(sys.argv[1], 'r')
            lines = file.readlines()
            file.close()

            (path, name) = osp.split(sys.argv[1])

            mtllib, v_lines, vn_lines, vt_lines, meshes = parse_obj(lines)
            materials = parse_mtl(osp.join(path, mtllib))
            
            rendering_lines = convert_to_rendering(materials, v_lines, vn_lines, vt_lines, meshes)
            
            output_file_path = osp.join(path, name + '.rendering')
            output_file = open(output_file_path, 'w')
            output_file.writelines(rendering_lines)
            output_file.close()
            print('[info] saved: %s' % output_file_path)
        except:
            print("[error] fail to parse obj file: %s" % sys.argv[1])

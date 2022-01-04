from obj_data import ObjData
import sys
import os.path as osp

def get_geometry_lines(v_lines, vn_lines, mesh_dic):
    new_v_lines = []
    new_vn_lines = []
    faces = []
    dic = {}
    for face_list in mesh_dic.values():
        for face in face_list:
            face_vertices = []
            for v in face:
                if v[0] < 0 or v[2] < 0:
                    raise Exception('[error] lack normal')
                key = '%d/%d' % (v[0], v[2])
                if key not in dic:
                    dic[key] = len(new_v_lines)
                    new_v_lines.append(v_lines[v[0]])
                    new_vn_lines.append(vn_lines[v[2]])
                face_vertices.append(dic[key])
            faces.append(face_vertices)
    print("[info] new info <v: %d, vn: %d, f: %d>" % (len(new_v_lines), len(new_vn_lines), len(faces)))
    new_lines = []
    for line in new_v_lines:
        new_lines.append('%s\n' % line)
    for line in new_vn_lines:
        new_lines.append('%s\n' % line)
    for face in faces:
        new_lines.append('f %d %d %d\n' % (face[0], face[1], face[2]))
    return new_lines

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: python obj2geometry.py <.obj file path>")
    else:
        file = open(sys.argv[1], 'r')
        lines = file.readlines()
        file.close()
        
        obj_data = ObjData(lines)
        print("[info] old info <%s>" % obj_data.get_old_info())

        v_lines = obj_data.new_v_lines
        vn_lines = obj_data.new_vn_lines
        mesh_dic = obj_data.new_mesh_dic

        (path, name) = osp.split(sys.argv[1])
        output_file_path = osp.join(path, name + '.geometry')
        obj_file = open(output_file_path, 'w')
        obj_file.writelines(get_geometry_lines(v_lines, vn_lines, mesh_dic))
        obj_file.close()
        print('[info] saved: %s' % output_file_path)

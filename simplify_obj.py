from obj_data import ObjData
import sys
import os.path as osp

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: python simplify_obj.py <.obj file path>")
    else:
        file = open(sys.argv[1], 'r')
        lines = file.readlines()
        file.close()
        
        obj_data = ObjData(lines)
        print("[info] old info <%s>" % obj_data.get_old_info())
        print("[info] new info <%s>" % obj_data.get_new_info())

        (path, name) = osp.split(sys.argv[1])
        output_file_path = osp.join(path, 'simplified-' + name)
        obj_file = open(output_file_path, 'w')
        obj_file.writelines(obj_data.get_new_obj_lines())
        obj_file.close()
        print('[info] saved: %s' % output_file_path)

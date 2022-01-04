class ObjData:

    def __parse_lines(self, lines):
        usemtl = ''
        self.old_mesh_dic[usemtl] = []
        for line in lines:
            line = line.strip()
            substrs = line.split()
            if len(substrs) == 0:
                continue
            if substrs[0] == 'mtllib':
                self.mtllib = line
            elif substrs[0] == 'v':
                self.old_v_lines.append(line)
            elif substrs[0] == 'vt':
                self.old_vt_lines.append(line)
            elif substrs[0] == 'vn':
                self.old_vn_lines.append(line)
            elif substrs[0] == 'usemtl':
                usemtl = line
                if usemtl not in self.old_mesh_dic:
                    self.old_mesh_dic[usemtl] = []
            elif substrs[0] == 'f':
                if len(substrs) != 4:
                    raise Exception("\"%s\" is not a triangle" % line)
                self.old_mesh_dic[usemtl].append(line)
    
    def __string_to_index(self, string):
        try:
            return int(string) - 1
        except:
            return -1
    
    # 将字符串 'v/vt/vn' 转换成索引(需要减一)列表 [v, vt, vn]
    def __parse_face_vertex_string(self, vertex_string):
        vertex_attributes = [-1, -1, -1]
        string = vertex_string[0:]
        for i in range(3):
            pos = string.find('/')
            if pos < 0:
                vertex_attributes[i] = self.__string_to_index(string)
                break
            else:
                vertex_attributes[i] = self.__string_to_index(string[0: pos])
                string = string[pos+1:]
        return vertex_attributes
    
    # 将行字符串'f v0/vt0/vn0 v1/vt1/vn1 v1/vt1/vn1' 转换成列表 [[v0,vt0,vn0], [v1,vt1,vn1], [v1,vt1,vn1]]
    def __parse_face_line(self, face_line):
        face_vertices = face_line.split()
        v0 = self.__parse_face_vertex_string(face_vertices[1])
        v1 = self.__parse_face_vertex_string(face_vertices[2])
        v2 = self.__parse_face_vertex_string(face_vertices[3])

        if self.old_v_lines[v0[0]] == self.old_v_lines[v1[0]] or self.old_v_lines[v1[0]] == self.old_v_lines[v2[0]] or self.old_v_lines[v2[0]] == self.old_v_lines[v0[0]]:
            return None
        return [v0, v1, v2]
    
    # 只保留被有效面引用的顶点坐标且对顶点坐标去重
    def __simplify(self):
        new_v_dic = {}  # 每行 'v x y z' 在 new_v_lines 中的索引
        new_vt_dic = {} # 每行 'vt tx ty' 在 new_vt_lines 中的索引
        new_vn_dic = {} # 每行 'vn nx ny nz' 在 new_vn_lines 中的索引
        
        for mtl, face_list in self.old_mesh_dic.items():
            self.new_mesh_dic[mtl] = []
            for face_line in face_list:
                face_vertices = self.__parse_face_line(face_line)
                if face_vertices is None:
                    continue
                new_face_vertices = []
                for v in face_vertices:
                    face_vertex = [-1, -1, -1]
                    if v[0] >= 0:
                        v_line = self.old_v_lines[v[0]]
                        if v_line not in new_v_dic:
                            new_v_dic[v_line] = len(self.new_v_lines)
                            self.new_v_lines.append(v_line)
                        face_vertex[0] = new_v_dic[v_line]
                    
                    if v[1] >= 0:
                        vt_line = self.old_vt_lines[v[1]]
                        if vt_line not in new_vt_dic:
                            new_vt_dic[vt_line] = len(self.new_vt_lines)
                            self.new_vt_lines.append(vt_line)
                        face_vertex[1] = new_vt_dic[vt_line]
                    
                    if v[2] >= 0:
                        vn_line = self.old_vn_lines[v[2]]
                        if vn_line not in new_vn_dic:
                            new_vn_dic[vn_line] = len(self.new_vn_lines)
                            self.new_vn_lines.append(vn_line)
                        face_vertex[2] = new_vn_dic[vn_line]
                    
                    new_face_vertices.append(face_vertex)
                self.new_mesh_dic[mtl].append(new_face_vertices)
    
    def get_old_info(self):
        v_count = len(self.old_v_lines)
        vt_count = len(self.old_vt_lines)
        vn_count = len(self.old_vn_lines)
        f_count = 0
        for faces in self.old_mesh_dic.values():
            f_count += len(faces)
        return 'v: %d, vt: %d, vn: %d, f: %d' % (v_count, vt_count, vn_count, f_count)
    
    def get_new_info(self):
        v_count = len(self.new_v_lines)
        vt_count = len(self.new_vt_lines)
        vn_count = len(self.new_vn_lines)
        f_count = 0
        for faces in self.new_mesh_dic.values():
            f_count += len(faces)
        return 'v: %d, vt: %d, vn: %d, f: %d' % (v_count, vt_count, vn_count, f_count)
    
    # 把列表 [v, vt, vn] 转换成字符串 'v/vt/vn'
    def __face_vertex_to_string(self, face_vertex):
        string = ''
        for i in range(len(face_vertex)):
            if i > 0:
                string += '/'
            if face_vertex[i] >= 0:
                string += ('%d' % (face_vertex[i] + 1))
        return string
        
    
    def get_new_obj_lines(self):
        lines = []
        lines.append('%s\n' % self.mtllib)
        for line in self.new_v_lines:
            lines.append('%s\n' % line)
        for line in self.new_vt_lines:
            lines.append('%s\n' % line)
        for line in self.new_vn_lines:
            lines.append('%s\n' % line)
        for mtl, faces in self.new_mesh_dic.items():
            lines.append('%s\n' % mtl)
            for face in faces:
                string = 'f %s %s %s\n' % (self.__face_vertex_to_string(face[0]), self.__face_vertex_to_string(face[1]), self.__face_vertex_to_string(face[2]))
                lines.append(string)
        return lines

    def __init__(self, lines):
        self.mtllib = ''        # .obj文件mtllib
        self.old_v_lines = []   # .obj文件顶点坐标v
        self.old_vt_lines = []  # .obj文件纹理坐标vt
        self.old_vn_lines = []  # .obj文件法向量vn
        self.old_mesh_dic = {}  # .obj文件mtl与对应的面f

        self.new_v_lines = []   # .obj文件被引用且去重的顶点坐标v
        self.new_vt_lines = []  # .obj文件被引用且去重的顶点坐标v
        self.new_vn_lines = []  # .obj文件被引用且去重的顶点坐标v
        self.new_mesh_dic = {}  # .obj文件mtl与对应的有效的面f

        self.__parse_lines(lines)
        self.__simplify()


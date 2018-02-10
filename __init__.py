import numpy as np
import bpy
import bmesh
import math
import mathutils

bl_info = {
    "name": "Nrotator",
    "author": "tanitta",
    "version": (0, 0),
    "blender": (2, 79, 0),
    "location": "",
    "description": "Nrotator description",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}

def set_raw_orientation(obj, q):
    obj["nrotator_qx"] = q.x
    obj["nrotator_qy"] = q.y
    obj["nrotator_qz"] = q.z
    obj["nrotator_qw"] = q.w

def get_raw_orientation(obj):
    q = mathutils.Quaternion()
    q.x = obj["nrotator_qx"]
    q.y = obj["nrotator_qy"]
    q.z = obj["nrotator_qz"]
    q.w = obj["nrotator_qw"]
    return q

def is_rotated(obj):
    return ("nrotator_qx" in obj) and ("nrotator_qy" in obj) and ("nrotator_qz" in obj) and ("nrotator_qw" in obj)

def remove_props(obj):
    del obj["nrotator_qx"]
    del obj["nrotator_qy"]
    del obj["nrotator_qz"]
    del obj["nrotator_qw"]

def create_props(obj):
    if is_rotated(obj):
        return 
    q = obj.rotation_quaternion
    obj["nrotator_qx"] = q.x
    obj["nrotator_qy"] = q.y
    obj["nrotator_qz"] = q.z
    obj["nrotator_qw"] = q.w

class NRotator(bpy.types.Operator):
    bl_idname = "object.nrotate"
    bl_label  = "Nrotate"
    bl_description = "nrotator description"

    def __init__(self):
        pass

    def face_normal(self, obj):
        bm = bmesh.from_edit_mesh(obj.data)
        num_selected_polygons = len(list(filter(lambda f: f.select, bm.faces)))
        if num_selected_polygons == 0 :
            return
        active_polygon = obj.data.polygons[obj.data.polygons.active]
        return active_polygon.normal

    def rotate(self, context):
        obj = context.edit_object
        if obj.type != 'MESH': 
            return
        obj.update_from_editmode()

        obj.rotation_mode = 'QUATERNION'
        q = obj.rotation_quaternion
        normal = self.face_normal(obj)
        global_normal = q*normal
        back = mathutils.Vector((0.0, -1.0, 0.0))
        axis = back.cross(global_normal).normalized()
        angle = back.angle(global_normal)

        create_props(obj)

        if not is_rotated(obj) :
            set_raw_orientation(obj, q)

        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.transform.rotate(value=-angle, axis = axis)
        bpy.ops.object.mode_set(mode = 'EDIT')

    def rotate_on_vertex_mode(self):
        pass

    def rotate_on_edge_mode(self):
        pass

    def rotate_on_polygon_mode(self):
        pass

    def execute(self, context):
        selecteds = context.selected_objects
        if len(selecteds) > 0:
            self.rotate(context)
        return {'FINISHED'}

class NrotatorAdjust(bpy.types.Operator):
    bl_idname = "object.nrotate_adjust"
    bl_label  = "Nrotate adjust"
    bl_description = "nrotator description"

    def __init__(self):
        pass

    def rotate(self, obj):
        obj.rotation_mode = 'QUATERNION'
        bm = bmesh.from_edit_mesh(obj.data)
        selecteds = list(filter(lambda v: v.select, bm.verts))
        num_selected_vertices = len(selecteds)
        if not num_selected_vertices == 2:
            return
        
        q = obj.rotation_quaternion
        v_global_a = q*selecteds[0].co
        v_global_b = q*selecteds[1].co
        v_global_d = v_global_b - v_global_a
        back = mathutils.Vector((0.0, -1.0, 0.0))
        up = mathutils.Vector((0.0, 0.0, 1.0))
        scaled = v_global_d.copy()
        scaled.x *= back.x
        scaled.y *= back.y
        scaled.z *= back.z
        v_global_projected = v_global_d - scaled
        axis = back
        angle = back.cross(up).angle(v_global_projected)

        create_props(obj)

        if not is_rotated(obj) :
            set_raw_orientation(obj, q)

        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.transform.rotate(value=angle, axis = axis)
        bpy.ops.object.mode_set(mode = 'EDIT')

    def execute(self, context):
        selecteds = context.selected_objects
        if len(selecteds) > 0:
            self.rotate(selecteds[0])
        return {'FINISHED'}

class NrotatorApply(bpy.types.Operator):
    bl_idname = "object.nrotate_apply"
    bl_label  = "Nrotate apply"
    bl_description = "nrotator description"

    def __init__(self):
        pass

    def rotate(self, obj):
        pass

    def execute(self, context):
        return {'FINISHED'}

class NrotatorCancel(bpy.types.Operator):
    bl_idname = "object.nrotate_cancel"
    bl_label  = "Nrotate cancel"
    bl_description = "nrotator description"

    def __init__(self):
        pass

    def rotate(self, obj):
        obj.rotation_quaternion = get_raw_orientation(obj)

    def execute(self, context):
        selecteds = context.selected_objects
        if len(selecteds) == 0:
            return

        obj = selecteds[0]

        if not is_rotated(obj) :
            return

        self.rotate(obj)

        remove_props(obj)
        return {'FINISHED'}

class UI(bpy.types.Panel):
  bl_label = "Nrotator"
  bl_space_type = "VIEW_3D"
  bl_region_type = "TOOLS"
  
  def draw(self, context):
    self.layout.operator("object.nrotate")
    self.layout.operator("object.nrotate_adjust")
    self.layout.operator("object.nrotate_apply")
    self.layout.operator("object.nrotate_cancel")


def menu_func(self, context):
    self.layout.separator()
    self.layout.operator(NRotator.bl_idname)
    self.layout.operator(NRotatorCancel.bl_idname)

def register():
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()

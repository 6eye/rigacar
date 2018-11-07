# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    "name": "Rigacar (Generates Car Rig)",
    "author": "David Gayerie",
    "version": (3, 0),
    "version": (3, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Armature",
    "description": "Adds a deformation rig for vehicules, generates animation rig and bake wheels animation.",
    "wiki_url": "http://digicreatures.net/articles/rigacar.html",
    "tracker_url": "https://github.com/digicreatures/rigacar/issues",
    "category": "Rigging"}

if "bpy" in locals():
    import importlib
    if "bake_operators" in locals():
        importlib.reload(bake_operators)
    if "car_rig" in locals():
        importlib.reload(car_rig)


import bpy
from . import bake_operators
from . import car_rig


class BaseCarRigPanel:

    @classmethod
    def is_car_rig(cls, context):
        return context.object is not None and context.object.data is not None and 'Car Rig' in context.object.data

    @classmethod
    def is_car_rig_generated(cls, context):
        return cls.is_car_rig(context) and context.object.data['Car Rig']

    def display_generate_section(self, context):
        self.layout.operator(car_rig.GenerateCarAnimationRigOperator.bl_idname, text='Generate')

    def display_bake_section(self, context):
        self.layout.operator(bake_operators.BakeSteeringOperator.bl_idname, text='Bake steering')
        self.layout.operator(bake_operators.BakeWheelRotationOperator.bl_idname, text='Bake wheels rotation')

    def display_rig_props_section(self, context):
        layout = self.layout.column()
        layout.prop(context.object, '["wheels_on_y_axis"]', text="Wheels on Y axis")
        layout.prop(context.object, '["suspension_factor"]', text="Suspension fact.")
        layout.prop(context.object, '["suspension_rolling_factor"]', text="Suspension rolling fact.")

    def display_ground_sensors_section(self, context, bones):
        ground_sensors_name = [b.name for b in bones if b.name.startswith('GroundSensor.')]
        for name in ground_sensors_name:
            ground_projection_constraint = context.object.pose.bones[name].constraints.get('Ground projection')
            if ground_projection_constraint is not None:
                self.layout.label(text="%s:" % name, icon='BONE_DATA')
                self.layout.prop(ground_projection_constraint, 'target', text='Ground')
                if ground_projection_constraint.target is not None:
                    self.layout.prop(ground_projection_constraint, 'shrinkwrap_type')
                    if ground_projection_constraint.shrinkwrap_type == 'PROJECT':
                        self.layout.prop(ground_projection_constraint, 'project_limit')
                    self.layout.prop(ground_projection_constraint, 'influence')
            ground_projection_limit_constraint = context.object.pose.bones[name].constraints.get('Ground projection limitation')
            if ground_projection_limit_constraint is not None:
                self.layout.prop(ground_projection_limit_constraint, 'min_z', text='min Z')
                self.layout.prop(ground_projection_limit_constraint, 'max_z', text='max Z')
            self.layout.separator()


class UIRigacarRigPropertiesPanel(bpy.types.Panel, BaseCarRigPanel):
    bl_label = "Rigacar"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return BaseCarRigPanel.is_car_rig(context)

    def draw(self, context):
        if BaseCarRigPanel.is_car_rig_generated(context):
            self.display_bake_section(context)
            self.layout.separator()
            self.display_rig_props_section(context)
        else:
            self.display_generate_section(context)


class UIRigacarGroundSensorsPropertiesPanel(bpy.types.Panel, BaseCarRigPanel):
    bl_label = "Ground Sensors"
    bl_parent_id = "UIRigacarRigPropertiesPanel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return BaseCarRigPanel.is_car_rig_generated(context)

    def draw(self, context):
        self.display_ground_sensors_section(context, bpy.context.object.data.bones)


class UIRigacarAnimationRigView3DPanel(bpy.types.Panel, BaseCarRigPanel):
    bl_category = "Rigacar"
    bl_label = "Animation Rig"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return BaseCarRigPanel.is_car_rig(context)

    def draw(self, context):
        if BaseCarRigPanel.is_car_rig_generated(context):
            self.display_rig_props_section(context)
        else:
            self.display_generate_section(context)


class UIRigacarWheelsAnimationView3DPanel(bpy.types.Panel, BaseCarRigPanel):
    bl_category = "Rigacar"
    bl_label = "Wheels animation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return BaseCarRigPanel.is_car_rig_generated(context)

    def draw(self, context):
        self.display_bake_section(context)


class UIRigacarGroundSensorsView3DPanel(bpy.types.Panel, BaseCarRigPanel):
    bl_category = "Rigacar"
    bl_label = "Ground Sensors"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return BaseCarRigPanel.is_car_rig_generated(context)

    def draw(self, context):
        self.display_ground_sensors_section(context, bpy.context.object.data.bones)


def menu_entries(menu, context):
    menu.layout.operator(car_rig.AddCarDeformationRigOperator.bl_idname, text="Car (deformation rig)", icon='AUTO')


classes = (
  UIRigacarRigPropertiesPanel,
  UIRigacarGroundSensorsPropertiesPanel,
  UIRigacarAnimationRigView3DPanel,
  UIRigacarWheelsAnimationView3DPanel,
  UIRigacarGroundSensorsView3DPanel,
)


def register():
    bpy.types.VIEW3D_MT_armature_add.append(menu_entries)
    for c in classes:
        bpy.utils.register_class(c)
    car_rig.register()
    bake_operators.register()


def unregister():
    bake_operators.unregister()
    car_rig.unregister()
    for c in classes:
        bpy.utils.unregister_class(c)
    bpy.types.VIEW3D_MT_armature_add.remove(menu_entries)


if __name__ == "__main__":
    register()

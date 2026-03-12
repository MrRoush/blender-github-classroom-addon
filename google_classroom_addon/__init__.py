"""
Classroom Blender Add-on
Integrates Google Classroom and GitHub Classroom with Blender to manage assignments
"""

bl_info = {
    "name": "Classroom Integration",
    "author": "Educational Technology",
    "version": (1, 1, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > Classroom",
    "description": "Connect to Google Classroom or GitHub Classroom to view and submit assignments",
    "category": "System",
    "doc_url": "https://github.com/MrRoush/blender-addon",
}

import bpy
import sys
import os

# Add the addon directory to the path to import modules
addon_dir = os.path.dirname(os.path.realpath(__file__))
if addon_dir not in sys.path:
    sys.path.append(addon_dir)

from . import properties
from . import operators
from . import ui

classes = (
    # Property groups (must be registered before they are referenced)
    properties.CourseItem,
    properties.AssignmentItem,
    properties.GitHubRepoItem,
    properties.GoogleClassroomProperties,
    # Google Classroom operators
    operators.GCLASS_OT_Authenticate,
    operators.GCLASS_OT_RefreshCourses,
    operators.GCLASS_OT_RefreshAssignments,
    operators.GCLASS_OT_OpenAssignment,
    operators.GCLASS_OT_SubmitAssignment,
    operators.GCLASS_OT_Logout,
    # GitHub Classroom operators
    operators.GITHUB_OT_Authenticate,
    operators.GITHUB_OT_Logout,
    operators.GITHUB_OT_RefreshRepos,
    operators.GITHUB_OT_OpenAssignment,
    operators.GITHUB_OT_SubmitAssignment,
    # UI helper operators
    ui.GCLASS_OT_SelectCourse,
    ui.GCLASS_OT_SelectAssignment,
    ui.GITHUB_OT_SelectRepo,
    # Panels
    ui.GCLASS_PT_MainPanel,
    ui.GCLASS_PT_CoursesPanel,
    ui.GCLASS_PT_AssignmentsPanel,
    ui.GITHUB_PT_ReposPanel,
)

def register():
    """Register all classes and properties"""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.google_classroom = bpy.props.PointerProperty(
        type=properties.GoogleClassroomProperties
    )

def unregister():
    """Unregister all classes and properties"""
    del bpy.types.Scene.google_classroom
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()

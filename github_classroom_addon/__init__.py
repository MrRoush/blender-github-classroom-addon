"""
GitHub Classroom Blender Add-on
Connect to GitHub Classroom to manage Blender assignments
"""

bl_info = {
    "name": "GitHub Classroom",
    "author": "Educational Technology",
    "version": (3, 0, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Classroom",
    "description": "Connect to GitHub Classroom to manage Blender assignments",
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
    properties.GitHubRepoItem,
    properties.GitHubClassroomProperties,
    # Operators
    operators.GITHUB_OT_Authenticate,
    operators.GITHUB_OT_Logout,
    operators.GITHUB_OT_RefreshRepos,
    operators.GITHUB_OT_OpenFile,
    operators.GITHUB_OT_PushFile,
    operators.GITHUB_OT_SetAutoPushMode,
    operators.GITHUB_OT_ToggleAdvancedMode,
    operators.GITHUB_OT_PullFromURL,
    operators.GITHUB_OT_Disconnect,
    operators.GITHUB_OT_SelectRepo,
    operators.GITHUB_OT_ToggleAssignment,
    operators.GITHUB_OT_RecoverAndPush,
    operators.GITHUB_OT_UploadRender,
    operators.GITHUB_OT_ToggleUploadRenders,
    # Panels
    ui.GITHUB_PT_MainPanel,
    ui.GITHUB_PT_ReposPanel,
)

def register():
    """Register all classes, properties, and handlers"""
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.github_classroom = bpy.props.PointerProperty(
        type=properties.GitHubClassroomProperties
    )

    # Register save handler for auto-push on save
    if operators.auto_push_on_save not in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.append(operators.auto_push_on_save)

    # Register load_pre handler for auto-push on quit
    if operators.auto_push_on_quit not in bpy.app.handlers.load_pre:
        bpy.app.handlers.load_pre.append(operators.auto_push_on_quit)

    # Register load_post handler for crash recovery detection
    if operators.check_crash_recovery not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(operators.check_crash_recovery)

    # Register render_complete handler for auto-upload of renders
    if operators.auto_upload_render not in bpy.app.handlers.render_complete:
        bpy.app.handlers.render_complete.append(operators.auto_upload_render)

def unregister():
    """Unregister all classes, properties, and handlers"""
    # Remove save handler
    if operators.auto_push_on_save in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.remove(operators.auto_push_on_save)

    # Remove load_pre handler
    if operators.auto_push_on_quit in bpy.app.handlers.load_pre:
        bpy.app.handlers.load_pre.remove(operators.auto_push_on_quit)

    # Remove load_post handler for crash recovery detection
    if operators.check_crash_recovery in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(operators.check_crash_recovery)

    # Remove render_complete handler for auto-upload of renders
    if operators.auto_upload_render in bpy.app.handlers.render_complete:
        bpy.app.handlers.render_complete.remove(operators.auto_upload_render)

    del bpy.types.Scene.github_classroom

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()

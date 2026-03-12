"""
Operator classes for GitHub Classroom Blender add-on
"""

import bpy
import os
import tempfile
from bpy.types import Operator
from .github_client import get_github_client


class GITHUB_OT_Authenticate(Operator):
    """Authenticate with GitHub"""
    bl_idname = "github_class.authenticate"
    bl_label = "Sign In"
    bl_description = "Sign in with your GitHub Personal Access Token"

    def execute(self, context):
        props = context.scene.github_classroom
        client = get_github_client()

        token = props.github_token
        props.status_message = "Signing in..."
        props.error_message = ""

        success, message = client.authenticate(token or None)

        if success:
            props.is_authenticated = True
            props.github_username = client.username or ""
            props.status_message = message
            # Auto-refresh repos if org is set
            if props.github_org:
                bpy.ops.github_class.refresh_repos()
        else:
            props.is_authenticated = False
            props.error_message = message
            self.report({'ERROR'}, message)

        return {'FINISHED'}


class GITHUB_OT_Logout(Operator):
    """Logout from GitHub"""
    bl_idname = "github_class.logout"
    bl_label = "Sign Out"
    bl_description = "Sign out from GitHub"

    def execute(self, context):
        props = context.scene.github_classroom
        client = get_github_client()

        client.logout()
        props.is_authenticated = False
        props.github_username = ""
        props.github_token = ""
        props.github_repos.clear()
        props.show_repos = False
        props.status_message = "Signed out"
        props.error_message = ""

        return {'FINISHED'}


class GITHUB_OT_RefreshRepos(Operator):
    """Refresh GitHub Classroom assignment repositories"""
    bl_idname = "github_class.refresh_repos"
    bl_label = "Load Assignments"
    bl_description = "Load assignment repositories from GitHub Classroom"

    def execute(self, context):
        props = context.scene.github_classroom
        client = get_github_client()

        if not client.is_authenticated():
            props.error_message = "Please sign in first"
            self.report({'ERROR'}, "Please sign in first")
            return {'CANCELLED'}

        if not props.github_org:
            props.error_message = "Please enter your classroom organization"
            self.report({'ERROR'}, "Organization name is required")
            return {'CANCELLED'}

        props.status_message = "Loading repositories..."
        props.error_message = ""

        # Teachers see all org repos, students see only their own
        if props.role == 'TEACHER':
            is_admin, admin_error = client.is_org_admin(props.github_org)
            if not is_admin:
                props.error_message = admin_error
                self.report({'ERROR'}, admin_error)
                return {'CANCELLED'}
            success, repos, error = client.get_org_repos(props.github_org)
        else:
            success, repos, error = client.get_repos(props.github_org)

        if success:
            props.github_repos.clear()
            for repo in repos:
                item = props.github_repos.add()
                item.repo_name = repo.get('name', '')
                item.full_name = repo.get('full_name', '')
                item.owner = repo.get('owner', {}).get('login', '')
                item.description = repo.get('description', '') or ''
                item.html_url = repo.get('html_url', '')
                updated = repo.get('updated_at', '')
                if updated:
                    item.updated_at = updated[:10]

                # Check for .blend files in the repo
                blend_success, blend_files, _ = client.find_blend_files(
                    item.owner, item.repo_name
                )
                if blend_success and blend_files:
                    item.has_blend_file = True
                    item.blend_file_path = blend_files[0].get('path', '')
                    item.blend_file_name = blend_files[0].get('name', '')

            props.show_repos = True
            count = len(repos)
            if props.role == 'TEACHER':
                props.status_message = f"Found {count} student repositories"
            else:
                props.status_message = f"Found {count} assignments"
        else:
            props.error_message = error
            self.report({'ERROR'}, error)

        return {'FINISHED'}


class GITHUB_OT_OpenFile(Operator):
    """Download and open a .blend file from GitHub"""
    bl_idname = "github_class.open_file"
    bl_label = "Open File"
    bl_description = "Download and open the .blend file from this repository"

    def execute(self, context):
        props = context.scene.github_classroom
        client = get_github_client()

        if not client.is_authenticated():
            props.error_message = "Please sign in first"
            self.report({'ERROR'}, "Please sign in first")
            return {'CANCELLED'}

        if (props.active_repo_index < 0
                or props.active_repo_index >= len(props.github_repos)):
            self.report({'ERROR'}, "No repository selected")
            return {'CANCELLED'}

        repo_item = props.github_repos[props.active_repo_index]

        if not repo_item.has_blend_file:
            self.report({'ERROR'}, "No .blend file found in this repository")
            return {'CANCELLED'}

        props.status_message = "Downloading file..."
        props.error_message = ""

        # Download to temp directory
        temp_dir = tempfile.gettempdir()
        download_path = os.path.join(temp_dir, repo_item.blend_file_name)

        success, error = client.download_file(
            repo_item.owner, repo_item.repo_name,
            repo_item.blend_file_path, download_path
        )

        if success:
            # Save blend_file_name before open_mainfile frees the scene.
            # Do NOT access props or repo_item after open_mainfile.
            blend_file_name = repo_item.blend_file_name

            # Track working file for auto-push (students only)
            if props.role == 'STUDENT':
                client.set_working_file(
                    repo_item.owner,
                    repo_item.repo_name,
                    repo_item.blend_file_path
                )

            bpy.ops.wm.open_mainfile(filepath=download_path)
            # Scene properties are now freed; only use local variables
            self.report({'INFO'}, f"Opened {blend_file_name}")
        else:
            props.error_message = error
            self.report({'ERROR'}, error)

        return {'FINISHED'}


class GITHUB_OT_PushFile(Operator):
    """Save and push current file to GitHub"""
    bl_idname = "github_class.push_file"
    bl_label = "Save & Push to GitHub"
    bl_description = "Save your work and push it to your GitHub repository"

    def execute(self, context):
        props = context.scene.github_classroom
        client = get_github_client()

        if not client.is_authenticated():
            props.error_message = "Please sign in first"
            self.report({'ERROR'}, "Please sign in first")
            return {'CANCELLED'}

        working = client.get_working_file()
        if not working:
            props.error_message = (
                "No assignment file loaded. "
                "Click \"Open Assignment\" first to connect "
                "to your GitHub repository."
            )
            self.report({'ERROR'}, "No assignment file loaded")
            return {'CANCELLED'}

        if not bpy.data.filepath:
            self.report(
                {'ERROR'}, "Please save your file first (File > Save As)"
            )
            return {'CANCELLED'}

        # Save the current file
        bpy.ops.wm.save_mainfile()

        props.status_message = "Pushing to GitHub..."
        props.error_message = ""

        file_name = os.path.basename(bpy.data.filepath)
        success, error = client.upload_file(
            working['repo_owner'],
            working['repo_name'],
            working['file_path'],
            bpy.data.filepath,
            message=f"Update {file_name} from Blender"
        )

        if success:
            props.status_message = "Pushed to GitHub successfully!"
            self.report({'INFO'}, "Pushed to GitHub successfully!")
        else:
            props.error_message = error
            self.report({'ERROR'}, error)

        return {'FINISHED'}


class GITHUB_OT_ToggleAutoPush(Operator):
    """Toggle auto-push on save"""
    bl_idname = "github_class.toggle_auto_push"
    bl_label = "Toggle Auto-Push"
    bl_description = "Toggle whether saving automatically pushes to GitHub"

    def execute(self, context):
        client = get_github_client()
        client.set_auto_push(not client.auto_push)
        state = "enabled" if client.auto_push else "disabled"
        self.report({'INFO'}, f"Auto-push {state}")
        return {'FINISHED'}


class GITHUB_OT_Disconnect(Operator):
    """Disconnect current file from GitHub"""
    bl_idname = "github_class.disconnect"
    bl_label = "Disconnect"
    bl_description = "Stop tracking the current file for GitHub push"

    def execute(self, context):
        client = get_github_client()
        client.clear_working_file()
        props = context.scene.github_classroom
        props.status_message = "Disconnected from GitHub repository"
        self.report({'INFO'}, "Disconnected from GitHub")
        return {'FINISHED'}


class GITHUB_OT_SelectRepo(bpy.types.Operator):
    """Select a GitHub Classroom assignment repo"""
    bl_idname = "github_class.select_repo"
    bl_label = "Select Repo"

    repo_index: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.github_classroom
        props.active_repo_index = self.repo_index
        return {'FINISHED'}


# --- Save handler for auto-push ---

@bpy.app.handlers.persistent
def auto_push_on_save(dummy):
    """Automatically push to GitHub after saving (if enabled)"""
    client = get_github_client()

    if not client.is_authenticated() or not client.auto_push:
        return

    working = client.get_working_file()
    if not working:
        return

    filepath = bpy.data.filepath
    if not filepath:
        return

    file_name = os.path.basename(filepath)
    success, error = client.upload_file(
        working['repo_owner'],
        working['repo_name'],
        working['file_path'],
        filepath,
        message=f"Auto-save {file_name} from Blender"
    )

    # Update UI status if possible
    try:
        props = bpy.context.scene.github_classroom
        if success:
            props.status_message = "Auto-pushed to GitHub"
            props.error_message = ""
        else:
            props.error_message = (
                f"Auto-push failed: {error}. "
                f"Try manual push or check your connection."
            )
    except Exception:
        pass

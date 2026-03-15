"""
Operator classes for GitHub Classroom Blender add-on
"""

import bpy
import os
import tempfile
from bpy.types import Operator
from .github_client import get_github_client, AUTO_PUSH_ON_SAVE, AUTO_PUSH_ON_QUIT


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

            # Compute assignment grouping for teacher view
            if props.role == 'TEACHER':
                repo_names = [r.repo_name for r in props.github_repos]
                groups = client.compute_assignment_groups(repo_names)
                for item in props.github_repos:
                    item.assignment_name = groups.get(item.repo_name, '')

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

        # Use custom commit message if provided (advanced mode), else auto
        file_name = os.path.basename(bpy.data.filepath)
        message = props.commit_message.strip()
        if not message:
            message = f"Update {file_name} from Blender"

        success, error = client.upload_file(
            working['repo_owner'],
            working['repo_name'],
            working['file_path'],
            bpy.data.filepath,
            message=message
        )

        if success:
            props.status_message = "Pushed to GitHub successfully!"
            props.commit_message = ""
            self.report({'INFO'}, "Pushed to GitHub successfully!")
        else:
            props.error_message = error
            self.report({'ERROR'}, error)

        return {'FINISHED'}


class GITHUB_OT_SetAutoPushMode(Operator):
    """Set the auto-push mode"""
    bl_idname = "github_class.set_auto_push_mode"
    bl_label = "Set Auto-Push Mode"
    bl_description = "Choose when to automatically push to GitHub"

    mode: bpy.props.EnumProperty(
        items=[
            ('ON_SAVE', "On Save",
             "Automatically push when saving the file"),
            ('MANUAL', "Manual",
             "Only push when you click the button"),
            ('ON_QUIT', "On Quit",
             "Automatically push when closing Blender"),
        ]
    )

    def execute(self, context):
        client = get_github_client()
        client.set_auto_push_mode(self.mode)
        labels = {
            'ON_SAVE': 'On Save',
            'MANUAL': 'Manual',
            'ON_QUIT': 'On Quit',
        }
        self.report({'INFO'}, f"Auto-push set to: {labels[self.mode]}")
        return {'FINISHED'}


class GITHUB_OT_ToggleAdvancedMode(Operator):
    """Toggle between Simple and Advanced mode"""
    bl_idname = "github_class.toggle_advanced_mode"
    bl_label = "Show Advanced Options"
    bl_description = (
        "Toggle advanced options like role selection, "
        "commit messages, and auto-push settings"
    )

    def execute(self, context):
        client = get_github_client()
        client.advanced_mode = not client.advanced_mode
        client._save_settings()
        state = "enabled" if client.advanced_mode else "disabled"
        self.report({'INFO'}, f"Advanced mode {state}")
        return {'FINISHED'}


class GITHUB_OT_PullFromURL(Operator):
    """Pull a .blend file from a specific GitHub repository URL"""
    bl_idname = "github_class.pull_from_url"
    bl_label = "Pull from URL"
    bl_description = (
        "Download and open a .blend file from a GitHub repository URL"
    )

    def execute(self, context):
        props = context.scene.github_classroom
        client = get_github_client()

        if not client.is_authenticated():
            props.error_message = "Please sign in first"
            self.report({'ERROR'}, "Please sign in first")
            return {'CANCELLED'}

        url = props.repo_url.strip()
        if not url:
            props.error_message = "Please enter a repository URL"
            self.report({'ERROR'}, "Please enter a repository URL")
            return {'CANCELLED'}

        owner, repo = client.parse_repo_url(url)
        if not owner or not repo:
            props.error_message = (
                "Invalid repository URL. "
                "Use the format: https://github.com/owner/repo"
            )
            self.report({'ERROR'}, "Invalid repository URL")
            return {'CANCELLED'}

        props.status_message = "Searching for .blend files..."
        props.error_message = ""

        # Find .blend files in the repository
        success, blend_files, error = client.find_blend_files(owner, repo)
        if not success:
            props.error_message = error
            self.report({'ERROR'}, error)
            return {'CANCELLED'}

        if not blend_files:
            props.error_message = "No .blend file found in this repository"
            self.report({'ERROR'}, "No .blend file found in this repository")
            return {'CANCELLED'}

        # Download the first .blend file
        blend_file = blend_files[0]
        file_path = blend_file.get('path', '')
        file_name = blend_file.get('name', 'file.blend')

        props.status_message = f"Downloading {file_name}..."

        temp_dir = tempfile.gettempdir()
        download_path = os.path.join(temp_dir, file_name)

        success, error = client.download_file(
            owner, repo, file_path, download_path
        )

        if success:
            # Track working file for auto-push
            client.set_working_file(owner, repo, file_path)

            bpy.ops.wm.open_mainfile(filepath=download_path)
            # Scene properties are now freed; only use local variables
            self.report({'INFO'}, f"Opened {file_name} from {owner}/{repo}")
        else:
            props.error_message = error
            self.report({'ERROR'}, error)

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


class GITHUB_OT_ToggleAssignment(bpy.types.Operator):
    """Expand or collapse an assignment group in the teacher view"""
    bl_idname = "github_class.toggle_assignment"
    bl_label = "Toggle Assignment Group"

    assignment_name: bpy.props.StringProperty()

    def execute(self, context):
        client = get_github_client()
        if self.assignment_name in client.expanded_assignments:
            client.expanded_assignments.discard(self.assignment_name)
        else:
            client.expanded_assignments.add(self.assignment_name)
        return {'FINISHED'}


# --- Save handler for auto-push ---

@bpy.app.handlers.persistent
def auto_push_on_save(dummy):
    """Automatically push to GitHub after saving (if auto-push on save)"""
    client = get_github_client()

    if not client.is_authenticated():
        return
    if client.auto_push_mode != AUTO_PUSH_ON_SAVE:
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


# --- Quit handler for auto-push on quit ---

@bpy.app.handlers.persistent
def auto_push_on_quit(dummy):
    """Push to GitHub before loading a new file (on-quit mode)"""
    client = get_github_client()

    if not client.is_authenticated():
        return
    if client.auto_push_mode != AUTO_PUSH_ON_QUIT:
        return

    working = client.get_working_file()
    if not working:
        return

    try:
        filepath = bpy.data.filepath
        if not filepath:
            return

        file_name = os.path.basename(filepath)
        client.upload_file(
            working['repo_owner'],
            working['repo_name'],
            working['file_path'],
            filepath,
            message=f"Auto-save {file_name} from Blender (on quit)"
        )
    except Exception:
        pass

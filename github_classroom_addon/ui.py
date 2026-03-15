"""
UI panel classes for GitHub Classroom Blender add-on
Simplified interface for students (non-programmers) and teachers.
Simple mode hides advanced options; Advanced mode shows role selection,
commit messages, auto-push settings, and manual repo URL entry.
"""

import bpy
from bpy.types import Panel
from .github_client import get_github_client

MAX_LINE_LENGTH = 40


def wrap_text(text, layout, max_length=MAX_LINE_LENGTH):
    """Wrap long text into multiple lines for Blender UI"""
    words = text.split()
    line = ""
    for word in words:
        if len(line) + len(word) + 1 < max_length:
            line += word + " "
        else:
            if line:
                layout.label(text=line)
            line = word + " "
    if line:
        layout.label(text=line)


class GITHUB_PT_MainPanel(Panel):
    """Main GitHub Classroom panel in the 3D Viewport sidebar"""
    bl_label = "GitHub Classroom"
    bl_idname = "GITHUB_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Classroom'

    def draw(self, context):
        layout = self.layout
        props = context.scene.github_classroom
        client = get_github_client()
        advanced = client.advanced_mode

        # Advanced mode toggle
        row = layout.row()
        icon = 'CHECKBOX_HLT' if advanced else 'CHECKBOX_DEHLT'
        row.operator(
            "github_class.toggle_advanced_mode",
            text="Show Advanced Options", icon=icon
        )

        # Role selector (advanced mode only)
        if advanced:
            box = layout.box()
            box.label(text="I am a:", icon='USER')
            row = box.row(align=True)
            row.prop(props, "role", expand=True)

        # Authentication
        box = layout.box()
        if client.is_authenticated():
            row = box.row()
            row.label(
                text=f"Signed in as @{client.username}", icon='CHECKMARK'
            )
            box.operator("github_class.logout", icon='X')
        else:
            box.label(text="Sign In", icon='LOCKED')
            box.prop(props, "github_token", text="Token")
            box.operator("github_class.authenticate", icon='CHECKBOX_HLT')

        # Classroom Organization
        if client.is_authenticated():
            box = layout.box()
            box.label(text="Classroom", icon='COMMUNITY')
            box.prop(props, "github_org", text="Organization")
            if props.role == 'TEACHER':
                box.operator(
                    "github_class.refresh_repos",
                    text="Load Student Repos", icon='FILE_REFRESH'
                )
            else:
                box.operator(
                    "github_class.refresh_repos",
                    text="Load My Assignments", icon='FILE_REFRESH'
                )

        # Repository URL (advanced mode only)
        if advanced and client.is_authenticated():
            box = layout.box()
            box.label(text="Repository URL", icon='URL')
            box.prop(props, "repo_url", text="URL")
            box.operator(
                "github_class.pull_from_url",
                text="Pull from URL", icon='IMPORT'
            )

        # Working file status
        if client.is_authenticated():
            working = client.get_working_file()
            if working:
                box = layout.box()
                box.label(text="Current File", icon='FILE_BLEND')
                box.label(text=f"Repo: {working['repo_name']}")
                box.label(text=f"File: {working['file_path']}")

                # Commit message (advanced mode only)
                if advanced:
                    box.label(text="Commit Message:", icon='TEXT')
                    box.prop(props, "commit_message", text="")

                # Auto-push mode (advanced mode only)
                if advanced:
                    row = box.row(align=True)
                    row.label(text="Auto-Push:")
                    for mode, label in [('ON_SAVE', "On Save"),
                                        ('MANUAL', "Manual"),
                                        ('ON_QUIT', "On Quit")]:
                        op = row.operator(
                            "github_class.set_auto_push_mode",
                            text=label,
                            depress=(client.auto_push_mode == mode)
                        )
                        op.mode = mode

                # Manual push button
                box.operator("github_class.push_file", icon='EXPORT')

                # Disconnect
                box.operator("github_class.disconnect", icon='X')

        # Status messages
        if props.status_message:
            box = layout.box()
            box.label(text=props.status_message, icon='INFO')

        if props.error_message:
            box = layout.box()
            box.label(text="Error:", icon='ERROR')
            wrap_text(props.error_message, box)


class GITHUB_PT_ReposPanel(Panel):
    """Assignment repositories panel"""
    bl_label = "Repositories"
    bl_idname = "GITHUB_PT_repos_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Classroom'
    bl_parent_id = "GITHUB_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        props = context.scene.github_classroom
        client = get_github_client()
        return client.is_authenticated() and props.show_repos

    def draw(self, context):
        layout = self.layout
        props = context.scene.github_classroom
        client = get_github_client()

        if len(props.github_repos) == 0:
            layout.label(text="No repositories found", icon='INFO')
            return

        count = len(props.github_repos)
        if props.role == 'TEACHER':
            layout.label(
                text=f"{count} student repos", icon='FILE_FOLDER'
            )
        else:
            layout.label(
                text=f"{count} assignments", icon='FILE_FOLDER'
            )

        # Teacher mode: group repos by assignment name
        if props.role == 'TEACHER':
            self._draw_teacher_repos(layout, props, client)
        else:
            self._draw_student_repos(layout, props)

    def _draw_student_repos(self, layout, props):
        """Draw a flat list of student repos"""
        for i, repo in enumerate(props.github_repos):
            box = layout.box()
            self._draw_repo_item(box, props, repo, i)

    def _draw_teacher_repos(self, layout, props, client):
        """Draw repos grouped by assignment (teacher view)"""
        # Build ordered list of assignment groups
        assignment_order = []
        assignment_repos = {}
        seen = set()

        for i, repo in enumerate(props.github_repos):
            name = repo.assignment_name
            if name and name not in seen:
                seen.add(name)
                assignment_order.append(name)
            if name not in assignment_repos:
                assignment_repos[name] = []
            assignment_repos[name].append((i, repo))

        # Render grouped assignments first
        for assignment in assignment_order:
            repos = assignment_repos[assignment]
            is_expanded = assignment in client.expanded_assignments

            # Assignment group header
            header_box = layout.box()
            row = header_box.row()
            icon = 'TRIA_DOWN' if is_expanded else 'TRIA_RIGHT'
            op = row.operator(
                "github_class.toggle_assignment",
                text=f"{assignment} ({len(repos)})",
                icon=icon, emboss=False
            )
            op.assignment_name = assignment

            # Expanded: show repos inside
            if is_expanded:
                for idx, repo in repos:
                    # Show student name (repo name minus assignment prefix)
                    student_label = repo.repo_name
                    if repo.repo_name.startswith(assignment + '-'):
                        student_label = repo.repo_name[len(assignment) + 1:]

                    inner_box = header_box.box()
                    row = inner_box.row()
                    if idx == props.active_repo_index:
                        sel_icon = 'RADIOBUT_ON'
                    else:
                        sel_icon = 'RADIOBUT_OFF'
                    op = row.operator(
                        "github_class.select_repo",
                        text=student_label,
                        icon=sel_icon, emboss=False
                    )
                    op.repo_index = idx

                    if idx == props.active_repo_index:
                        self._draw_repo_details(inner_box, props, repo)

        # Render ungrouped repos (no assignment prefix)
        ungrouped = assignment_repos.get('', [])
        for idx, repo in ungrouped:
            box = layout.box()
            self._draw_repo_item(box, props, repo, idx)

    def _draw_repo_item(self, box, props, repo, index):
        """Draw a single repo entry with selection button"""
        row = box.row()
        if index == props.active_repo_index:
            icon = 'RADIOBUT_ON'
        else:
            icon = 'RADIOBUT_OFF'
        op = row.operator(
            "github_class.select_repo",
            text=repo.repo_name, icon=icon, emboss=False
        )
        op.repo_index = index

        if index == props.active_repo_index:
            self._draw_repo_details(box, props, repo)

    def _draw_repo_details(self, box, props, repo):
        """Draw details for a selected repo"""
        if repo.description:
            box.label(text=repo.description, icon='TEXT')

        if repo.updated_at:
            box.label(
                text=f"Updated: {repo.updated_at}", icon='TIME'
            )

        # .blend file indicator
        if repo.has_blend_file:
            box.label(
                text=f"File: {repo.blend_file_name}",
                icon='FILE_BLEND'
            )
            row = box.row()
            if props.role == 'TEACHER':
                row.operator(
                    "github_class.open_file",
                    text="Open for Review", icon='FILEBROWSER'
                )
            else:
                row.operator(
                    "github_class.open_file",
                    text="Open Assignment", icon='FILEBROWSER'
                )
        else:
            box.label(text="No .blend file found", icon='INFO')

        # Push button (students only)
        if props.role == 'STUDENT':
            box.separator()
            col = box.column()
            if repo.submitted:
                col.label(text="Submitted", icon='CHECKMARK')
                col.operator(
                    "github_class.push_file",
                    text="Resubmit", icon='EXPORT'
                )
            else:
                col.operator(
                    "github_class.push_file",
                    text="Save & Push", icon='EXPORT'
                )

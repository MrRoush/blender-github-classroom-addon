"""
Property classes for GitHub Classroom Blender add-on
"""

import bpy
from bpy.props import (
    StringProperty,
    IntProperty,
    BoolProperty,
    CollectionProperty,
    EnumProperty,
)
from bpy.types import PropertyGroup


class GitHubRepoItem(PropertyGroup):
    """Represents a GitHub Classroom assignment repository"""
    repo_name: StringProperty(name="Repository Name")
    full_name: StringProperty(name="Full Name")
    owner: StringProperty(name="Owner")
    description: StringProperty(name="Description")
    html_url: StringProperty(name="URL")
    has_blend_file: BoolProperty(name="Has Blend File", default=False)
    blend_file_path: StringProperty(name="Blend File Path")
    blend_file_name: StringProperty(name="Blend File Name")
    updated_at: StringProperty(name="Last Updated")
    submitted: BoolProperty(name="Submitted", default=False)
    assignment_name: StringProperty(
        name="Assignment Name",
        description="Assignment group name derived from repo naming convention",
        default=""
    )


class GitHubClassroomProperties(PropertyGroup):
    """Main property group for GitHub Classroom integration"""

    # Role selection (visible in advanced mode)
    role: EnumProperty(
        name="Role",
        description="Select your role",
        items=[
            ('STUDENT', "Student",
             "I am a student working on assignments"),
            ('TEACHER', "Teacher",
             "I am a teacher reviewing student work"),
        ],
        default='STUDENT',
    )

    # Authentication state
    is_authenticated: BoolProperty(
        name="Authenticated",
        description="Whether user is authenticated",
        default=False
    )

    github_token: StringProperty(
        name="GitHub Token",
        description="GitHub Personal Access Token",
        subtype='PASSWORD',
        default=""
    )

    github_org: StringProperty(
        name="Organization",
        description="GitHub Classroom organization name",
        default=""
    )

    github_username: StringProperty(
        name="GitHub Username",
        description="Authenticated GitHub username",
        default=""
    )

    # Repository list
    github_repos: CollectionProperty(type=GitHubRepoItem)
    active_repo_index: IntProperty(name="Active Repo", default=-1)

    # UI state
    show_repos: BoolProperty(
        name="Show Repos",
        description="Show GitHub repos list",
        default=False
    )

    # Commit message (advanced mode)
    commit_message: StringProperty(
        name="Commit Message",
        description="Optional commit message (auto-generates if left blank)",
        default=""
    )

    # Repository URL (advanced mode, for manual pull)
    repo_url: StringProperty(
        name="Repository URL",
        description="GitHub repository URL for manual pull",
        default=""
    )

    # Status messages
    status_message: StringProperty(
        name="Status",
        description="Current status message",
        default=""
    )

    error_message: StringProperty(
        name="Error",
        description="Current error message",
        default=""
    )

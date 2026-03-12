"""
Property classes for Classroom add-on (Google Classroom and GitHub Classroom)
"""

import bpy
from bpy.props import (
    StringProperty,
    IntProperty,
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    PointerProperty,
)
from bpy.types import PropertyGroup


# --- Google Classroom property groups ---

class CourseItem(PropertyGroup):
    """Represents a Google Classroom course"""
    course_id: StringProperty(name="Course ID")
    name: StringProperty(name="Course Name")
    section: StringProperty(name="Section")
    description: StringProperty(name="Description")
    room: StringProperty(name="Room")

class AssignmentItem(PropertyGroup):
    """Represents a Google Classroom assignment"""
    assignment_id: StringProperty(name="Assignment ID")
    course_work_id: StringProperty(name="CourseWork ID")
    title: StringProperty(name="Title")
    description: StringProperty(name="Description")
    due_date: StringProperty(name="Due Date")
    state: StringProperty(name="State")
    has_blend_file: BoolProperty(name="Has Blend File", default=False)
    blend_file_id: StringProperty(name="Blend File ID")
    blend_file_name: StringProperty(name="Blend File Name")
    submission_id: StringProperty(name="Submission ID")
    submission_state: StringProperty(name="Submission State")


# --- GitHub Classroom property groups ---

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


# --- Main property group ---

class GoogleClassroomProperties(PropertyGroup):
    """Main property group for classroom integration"""

    # Platform selection
    platform: EnumProperty(
        name="Platform",
        description="Choose your classroom platform",
        items=[
            ('GOOGLE', "Google Classroom",
             "Use Google Classroom (requires Google Cloud Console credentials)"),
            ('GITHUB', "GitHub Classroom",
             "Use GitHub Classroom (requires a GitHub Personal Access Token)"),
        ],
        default='GITHUB',
    )

    # Authentication state
    is_authenticated: BoolProperty(
        name="Authenticated",
        description="Whether user is authenticated",
        default=False
    )

    user_email: StringProperty(
        name="User Email",
        description="Email of authenticated user",
        default=""
    )

    # --- Google Classroom properties ---
    courses: CollectionProperty(type=CourseItem)
    active_course_index: IntProperty(name="Active Course", default=-1)

    assignments: CollectionProperty(type=AssignmentItem)
    active_assignment_index: IntProperty(name="Active Assignment", default=-1)

    # --- GitHub Classroom properties ---
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

    github_repos: CollectionProperty(type=GitHubRepoItem)
    active_repo_index: IntProperty(name="Active Repo", default=-1)

    # UI state
    show_courses: BoolProperty(
        name="Show Courses",
        description="Show courses list",
        default=False
    )

    show_assignments: BoolProperty(
        name="Show Assignments",
        description="Show assignments list",
        default=False
    )

    show_repos: BoolProperty(
        name="Show Repos",
        description="Show GitHub repos list",
        default=False
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

"""
Operator classes for Classroom add-on (Google Classroom and GitHub Classroom)
"""

import bpy
import os
import tempfile
from bpy.types import Operator
from .api_client import get_client
from .github_client import get_github_client


# ============================================================
# Google Classroom Operators
# ============================================================

class GCLASS_OT_Authenticate(Operator):
    """Authenticate with Google Classroom"""
    bl_idname = "gclass.authenticate"
    bl_label = "Sign In with Google"
    bl_description = "Authenticate with Google Classroom"
    
    def execute(self, context):
        props = context.scene.google_classroom
        client = get_client()
        
        props.status_message = "Authenticating..."
        props.error_message = ""
        
        success, message = client.authenticate()
        
        if success:
            props.is_authenticated = True
            props.status_message = "Successfully authenticated"
            email = client.get_user_email()
            if email:
                props.user_email = email
            
            # Auto-refresh courses after authentication
            bpy.ops.gclass.refresh_courses()
        else:
            props.is_authenticated = False
            props.error_message = message
            self.report({'ERROR'}, message)
        
        return {'FINISHED'}

class GCLASS_OT_Logout(Operator):
    """Logout from Google Classroom"""
    bl_idname = "gclass.logout"
    bl_label = "Sign Out"
    bl_description = "Sign out from Google Classroom"
    
    def execute(self, context):
        props = context.scene.google_classroom
        client = get_client()
        
        client.logout()
        props.is_authenticated = False
        props.user_email = ""
        props.courses.clear()
        props.assignments.clear()
        props.show_courses = False
        props.show_assignments = False
        props.status_message = "Signed out"
        props.error_message = ""
        
        return {'FINISHED'}

class GCLASS_OT_RefreshCourses(Operator):
    """Refresh courses list"""
    bl_idname = "gclass.refresh_courses"
    bl_label = "Refresh Courses"
    bl_description = "Refresh the list of courses"
    
    def execute(self, context):
        props = context.scene.google_classroom
        client = get_client()
        
        if not client.is_authenticated():
            props.error_message = "Not authenticated"
            self.report({'ERROR'}, "Please sign in first")
            return {'CANCELLED'}
        
        props.status_message = "Fetching courses..."
        props.error_message = ""
        
        success, courses, error = client.get_courses()
        
        if success:
            props.courses.clear()
            for course in courses:
                item = props.courses.add()
                item.course_id = course.get('id', '')
                item.name = course.get('name', 'Unnamed Course')
                item.section = course.get('section', '')
                item.description = course.get('descriptionHeading', '')
                item.room = course.get('room', '')
            
            props.show_courses = True
            props.status_message = f"Loaded {len(courses)} courses"
        else:
            props.error_message = error
            self.report({'ERROR'}, error)
        
        return {'FINISHED'}

class GCLASS_OT_RefreshAssignments(Operator):
    """Refresh assignments for selected course"""
    bl_idname = "gclass.refresh_assignments"
    bl_label = "Refresh Assignments"
    bl_description = "Refresh the list of assignments for the selected course"
    
    def execute(self, context):
        props = context.scene.google_classroom
        client = get_client()
        
        if not client.is_authenticated():
            props.error_message = "Not authenticated"
            self.report({'ERROR'}, "Please sign in first")
            return {'CANCELLED'}
        
        if props.active_course_index < 0 or props.active_course_index >= len(props.courses):
            self.report({'ERROR'}, "No course selected")
            return {'CANCELLED'}
        
        course = props.courses[props.active_course_index]
        props.status_message = f"Fetching assignments for {course.name}..."
        props.error_message = ""
        
        success, coursework_list, error = client.get_coursework(course.course_id)
        
        if success:
            props.assignments.clear()
            for cw in coursework_list:
                item = props.assignments.add()
                item.course_work_id = cw.get('id', '')
                item.title = cw.get('title', 'Untitled')
                item.description = cw.get('description', '')
                item.state = cw.get('state', '')
                
                # Check for due date
                if 'dueDate' in cw:
                    due = cw['dueDate']
                    due_time = cw.get('dueTime', {})
                    # Only format if all date components are present
                    if 'year' in due and 'month' in due and 'day' in due:
                        year = due['year']
                        month = str(due['month']).zfill(2)
                        day = str(due['day']).zfill(2)
                        hours = str(due_time.get('hours', 23)).zfill(2)
                        minutes = str(due_time.get('minutes', 59)).zfill(2)
                        item.due_date = f"{year}-{month}-{day} {hours}:{minutes}"
                
                # Check for .blend file attachments
                materials = cw.get('materials', [])
                for material in materials:
                    if 'driveFile' in material:
                        drive_file = material['driveFile']['driveFile']
                        title = drive_file.get('title', '')
                        if title.endswith('.blend'):
                            item.has_blend_file = True
                            item.blend_file_id = drive_file.get('id', '')
                            item.blend_file_name = title
                            break
                
                # Get submission info
                success_sub, submission, _ = client.get_student_submission(course.course_id, item.course_work_id)
                if success_sub and submission:
                    item.submission_id = submission.get('id', '')
                    item.submission_state = submission.get('state', '')
            
            props.show_assignments = True
            props.status_message = f"Loaded {len(coursework_list)} assignments"
        else:
            props.error_message = error
            self.report({'ERROR'}, error)
        
        return {'FINISHED'}

class GCLASS_OT_OpenAssignment(Operator):
    """Open assignment .blend file"""
    bl_idname = "gclass.open_assignment"
    bl_label = "Open Assignment File"
    bl_description = "Download and open the .blend file for this assignment"
    
    def execute(self, context):
        props = context.scene.google_classroom
        client = get_client()
        
        if not client.is_authenticated():
            props.error_message = "Not authenticated"
            self.report({'ERROR'}, "Please sign in first")
            return {'CANCELLED'}
        
        if props.active_assignment_index < 0 or props.active_assignment_index >= len(props.assignments):
            self.report({'ERROR'}, "No assignment selected")
            return {'CANCELLED'}
        
        assignment = props.assignments[props.active_assignment_index]
        
        if not assignment.has_blend_file:
            self.report({'ERROR'}, "This assignment has no .blend file")
            return {'CANCELLED'}
        
        props.status_message = "Downloading assignment file..."
        props.error_message = ""
        
        # Create temp directory for downloads
        temp_dir = tempfile.gettempdir()
        download_path = os.path.join(temp_dir, assignment.blend_file_name)
        
        success, error = client.download_drive_file(assignment.blend_file_id, download_path)
        
        if success:
            # Open the file in Blender
            bpy.ops.wm.open_mainfile(filepath=download_path)
            props.status_message = f"Opened {assignment.blend_file_name}"
        else:
            props.error_message = error
            self.report({'ERROR'}, error)
        
        return {'FINISHED'}

class GCLASS_OT_SubmitAssignment(Operator):
    """Submit assignment to Google Classroom"""
    bl_idname = "gclass.submit_assignment"
    bl_label = "Submit Assignment"
    bl_description = "Save current file and submit to Google Classroom"
    
    def execute(self, context):
        props = context.scene.google_classroom
        client = get_client()
        
        if not client.is_authenticated():
            props.error_message = "Not authenticated"
            self.report({'ERROR'}, "Please sign in first")
            return {'CANCELLED'}
        
        if props.active_course_index < 0 or props.active_course_index >= len(props.courses):
            self.report({'ERROR'}, "No course selected")
            return {'CANCELLED'}
        
        if props.active_assignment_index < 0 or props.active_assignment_index >= len(props.assignments):
            self.report({'ERROR'}, "No assignment selected")
            return {'CANCELLED'}
        
        course = props.courses[props.active_course_index]
        assignment = props.assignments[props.active_assignment_index]
        
        # Check if file is saved
        if not bpy.data.filepath:
            self.report({'ERROR'}, "Please save your file first")
            return {'CANCELLED'}
        
        # Save the current file
        bpy.ops.wm.save_mainfile()
        
        props.status_message = "Uploading submission..."
        props.error_message = ""
        
        # Upload the file
        success, error = client.upload_submission_file(
            course.course_id,
            assignment.course_work_id,
            bpy.data.filepath
        )
        
        if not success:
            props.error_message = error
            self.report({'ERROR'}, error)
            return {'CANCELLED'}
        
        # Mark as turned in
        success, error = client.submit_assignment(
            course.course_id,
            assignment.course_work_id
        )
        
        if success:
            props.status_message = "Assignment submitted successfully!"
            assignment.submission_state = "TURNED_IN"
            self.report({'INFO'}, "Assignment submitted successfully!")
        else:
            props.error_message = error
            self.report({'ERROR'}, error)
        
        return {'FINISHED'}


# ============================================================
# GitHub Classroom Operators
# ============================================================

class GITHUB_OT_Authenticate(Operator):
    """Authenticate with GitHub"""
    bl_idname = "github_class.authenticate"
    bl_label = "Sign In with GitHub"
    bl_description = "Authenticate with GitHub using a Personal Access Token"

    def execute(self, context):
        props = context.scene.google_classroom
        client = get_github_client()

        token = props.github_token
        props.status_message = "Authenticating with GitHub..."
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
        props = context.scene.google_classroom
        client = get_github_client()

        client.logout()
        props.is_authenticated = False
        props.github_username = ""
        props.github_token = ""
        props.github_repos.clear()
        props.show_repos = False
        props.status_message = "Signed out from GitHub"
        props.error_message = ""

        return {'FINISHED'}


class GITHUB_OT_RefreshRepos(Operator):
    """Refresh GitHub Classroom assignment repositories"""
    bl_idname = "github_class.refresh_repos"
    bl_label = "Refresh Assignments"
    bl_description = "Refresh the list of assignment repositories"

    def execute(self, context):
        props = context.scene.google_classroom
        client = get_github_client()

        if not client.is_authenticated():
            props.error_message = "Not authenticated"
            self.report({'ERROR'}, "Please sign in first")
            return {'CANCELLED'}

        if not props.github_org:
            props.error_message = "Please enter the organization name"
            self.report({'ERROR'}, "Organization name is required")
            return {'CANCELLED'}

        props.status_message = "Fetching assignment repos..."
        props.error_message = ""

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
            props.status_message = f"Loaded {len(repos)} assignment repos"
        else:
            props.error_message = error
            self.report({'ERROR'}, error)

        return {'FINISHED'}


class GITHUB_OT_OpenAssignment(Operator):
    """Open .blend file from GitHub Classroom assignment"""
    bl_idname = "github_class.open_assignment"
    bl_label = "Open Assignment File"
    bl_description = "Download and open the .blend file from this assignment repo"

    def execute(self, context):
        props = context.scene.google_classroom
        client = get_github_client()

        if not client.is_authenticated():
            props.error_message = "Not authenticated"
            self.report({'ERROR'}, "Please sign in first")
            return {'CANCELLED'}

        if props.active_repo_index < 0 or props.active_repo_index >= len(props.github_repos):
            self.report({'ERROR'}, "No assignment selected")
            return {'CANCELLED'}

        repo_item = props.github_repos[props.active_repo_index]

        if not repo_item.has_blend_file:
            self.report({'ERROR'}, "This assignment has no .blend file")
            return {'CANCELLED'}

        props.status_message = "Downloading assignment file..."
        props.error_message = ""

        # Download to temp directory
        temp_dir = tempfile.gettempdir()
        download_path = os.path.join(temp_dir, repo_item.blend_file_name)

        success, error = client.download_file(
            repo_item.owner, repo_item.repo_name,
            repo_item.blend_file_path, download_path
        )

        if success:
            bpy.ops.wm.open_mainfile(filepath=download_path)
            props.status_message = f"Opened {repo_item.blend_file_name}"
        else:
            props.error_message = error
            self.report({'ERROR'}, error)

        return {'FINISHED'}


class GITHUB_OT_SubmitAssignment(Operator):
    """Submit assignment to GitHub Classroom"""
    bl_idname = "github_class.submit_assignment"
    bl_label = "Submit Assignment"
    bl_description = "Save current file and push to GitHub Classroom"

    def execute(self, context):
        props = context.scene.google_classroom
        client = get_github_client()

        if not client.is_authenticated():
            props.error_message = "Not authenticated"
            self.report({'ERROR'}, "Please sign in first")
            return {'CANCELLED'}

        if props.active_repo_index < 0 or props.active_repo_index >= len(props.github_repos):
            self.report({'ERROR'}, "No assignment selected")
            return {'CANCELLED'}

        repo_item = props.github_repos[props.active_repo_index]

        # Check if file is saved
        if not bpy.data.filepath:
            self.report({'ERROR'}, "Please save your file first")
            return {'CANCELLED'}

        # Save the current file
        bpy.ops.wm.save_mainfile()

        props.status_message = "Uploading submission to GitHub..."
        props.error_message = ""

        # Determine the file path in the repo
        file_name = os.path.basename(bpy.data.filepath)
        repo_file_path = file_name
        if repo_item.blend_file_path:
            repo_file_path = repo_item.blend_file_path

        success, error = client.upload_file(
            repo_item.owner, repo_item.repo_name,
            repo_file_path, bpy.data.filepath,
            message=f"Submit {file_name} from Blender"
        )

        if success:
            props.status_message = "Assignment submitted successfully!"
            repo_item.submitted = True
            self.report({'INFO'}, "Assignment submitted to GitHub!")
        else:
            props.error_message = error
            self.report({'ERROR'}, error)

        return {'FINISHED'}

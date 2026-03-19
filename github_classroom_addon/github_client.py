"""
GitHub Classroom API client module
Handles authentication and API calls to GitHub for classroom integration.
Uses only Python standard library (no external dependencies required).
"""

import os
import json
import base64
import urllib.parse
import urllib.request
import urllib.error
from typing import Optional, List, Dict, Any, Tuple

try:
    import bpy as _bpy
except ImportError:
    _bpy = None

GITHUB_API_URL = "https://api.github.com"

# Auto-push mode constants
AUTO_PUSH_ON_SAVE = 'ON_SAVE'
AUTO_PUSH_MANUAL = 'MANUAL'
AUTO_PUSH_ON_QUIT = 'ON_QUIT'


class GitHubClassroomClient:
    """Client for interacting with GitHub for classroom assignments"""

    def __init__(self):
        self.token = None
        self.username = None
        self.config_dir = self._get_config_dir()
        self.token_file = os.path.join(self.config_dir, 'github_token.json')
        self.working_file_config = os.path.join(
            self.config_dir, 'working_file.json'
        )
        self.settings_file = os.path.join(self.config_dir, 'settings.json')
        self.working_file = None
        self.advanced_mode = False
        self.auto_push_mode = AUTO_PUSH_ON_SAVE
        self.upload_renders_on_complete = False
        self.expanded_assignments = set()
        self._load_settings()
        self._load_working_file()

    def _get_config_dir(self) -> str:
        """Get per-OS-user configuration directory for storing credentials"""
        if _bpy is not None:
            config_dir = os.path.join(_bpy.utils.resource_path('USER'), 'classroom_addon')
        else:
            config_dir = os.path.join(os.path.expanduser("~"), ".blender_classroom_addon")
        os.makedirs(config_dir, exist_ok=True)
        return config_dir

    def _make_request(self, endpoint: str, method: str = 'GET',
                      data: Optional[Dict] = None) -> Any:
        """Make an authenticated request to GitHub API"""
        url = f"{GITHUB_API_URL}{endpoint}"
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Blender-Classroom-Addon',
        }
        if data is not None:
            headers['Content-Type'] = 'application/json'

        req = urllib.request.Request(url, headers=headers, method=method)
        if data is not None:
            req.data = json.dumps(data).encode('utf-8')

        response = urllib.request.urlopen(req)
        body = response.read().decode('utf-8')
        if body:
            return json.loads(body)
        return None

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.token is not None and self.username is not None

    def authenticate(self, token: Optional[str] = None) -> Tuple[bool, str]:
        """
        Authenticate with GitHub using a Personal Access Token.
        Returns: (success, message)
        """
        try:
            # Try to load saved token if none provided
            if token is None and os.path.exists(self.token_file):
                with open(self.token_file, 'r') as f:
                    saved = json.load(f)
                    token = saved.get('token')

            if not token:
                return False, ("No token provided. Please enter your "
                               "GitHub Personal Access Token.")

            self.token = token

            # Verify token by getting user info
            user = self._make_request('/user')
            self.username = user.get('login')

            # Save token for next session
            with open(self.token_file, 'w') as f:
                json.dump({'token': token}, f)

            return True, f"Authenticated as {self.username}"

        except urllib.error.HTTPError as e:
            self.token = None
            self.username = None
            if e.code == 401:
                return False, "Invalid token. Please check your token."
            return False, f"Authentication failed: HTTP {e.code}"
        except Exception as e:
            self.token = None
            self.username = None
            return False, f"Authentication failed: {str(e)}"

    def logout(self):
        """Clear authentication and remove saved token"""
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
        self.token = None
        self.username = None
        self.clear_working_file()

    def get_repos(self, org_name: str) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Get assignment repos for the authenticated user in an organization.
        Used by students to see their own assignment repositories.
        Returns: (success, repos_list, error_message)
        """
        if not self.is_authenticated():
            return False, [], "Not authenticated"

        try:
            all_repos = []
            page = 1
            while True:
                repos = self._make_request(
                    f'/user/repos?per_page=100&page={page}'
                    f'&affiliation=collaborator,organization_member'
                    f'&sort=updated&direction=desc'
                )
                if not repos:
                    break
                all_repos.extend(repos)
                if len(repos) < 100:
                    break
                page += 1

            # Filter to repos in the specified organization, then to only
            # repos whose name contains the student's username
            # (GitHub Classroom names them {assignment}-{username}).
            org_lower = org_name.lower()
            username_lower = (self.username or '').lower()
            if not username_lower:
                return False, [], "Username not available; please re-authenticate"
            filtered = [
                r for r in all_repos
                if r.get('owner', {}).get('login', '').lower() == org_lower
                and username_lower in r.get('name', '').lower()
            ]

            return True, filtered, ""

        except urllib.error.HTTPError as e:
            return False, [], f"API error: HTTP {e.code}"
        except Exception as e:
            return False, [], f"Error fetching repos: {str(e)}"

    def get_org_repos(self, org_name: str) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Get ALL repos in an organization (for teachers).
        Teachers can see all student assignment repositories in the classroom org.
        Returns: (success, repos_list, error_message)
        """
        if not self.is_authenticated():
            return False, [], "Not authenticated"

        try:
            all_repos = []
            page = 1
            encoded_org = urllib.parse.quote(org_name, safe='')
            while True:
                repos = self._make_request(
                    f'/orgs/{encoded_org}/repos?per_page=100&page={page}'
                    f'&sort=updated&direction=desc'
                )
                if not repos:
                    break
                all_repos.extend(repos)
                if len(repos) < 100:
                    break
                page += 1

            return True, all_repos, ""

        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False, [], f"Organization '{org_name}' not found"
            return False, [], f"API error: HTTP {e.code}"
        except Exception as e:
            return False, [], f"Error fetching org repos: {str(e)}"

    def is_org_admin(self, org_name: str) -> Tuple[bool, str]:
        """
        Check if the authenticated user is an admin/owner of the organization.
        Returns: (is_admin, error_message)
        """
        if not self.is_authenticated():
            return False, "Not authenticated"

        try:
            encoded_org = urllib.parse.quote(org_name, safe='')
            encoded_username = urllib.parse.quote(self.username, safe='')
            membership = self._make_request(
                f'/orgs/{encoded_org}/memberships/{encoded_username}'
            )
            role = membership.get('role', '')
            if role == 'admin':
                return True, ""
            return False, (
                "Teacher access requires organization admin/owner privileges. "
                "Your account does not have admin access to this organization."
            )

        except urllib.error.HTTPError as e:
            if e.code in (403, 404):
                return False, (
                    "Teacher access requires organization admin/owner privileges. "
                    "Your account does not have admin access to this organization."
                )
            return False, f"Error checking organization membership: HTTP {e.code}"
        except Exception as e:
            return False, f"Error checking organization membership: {str(e)}"

    def find_blend_files(self, owner: str, repo: str,
                         path: str = '') -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Find .blend files in a repository.
        Returns: (success, blend_files_list, error_message)
        """
        if not self.is_authenticated():
            return False, [], "Not authenticated"

        try:
            encoded_path = urllib.parse.quote(path, safe='/')
            encoded_owner = urllib.parse.quote(owner, safe='')
            encoded_repo = urllib.parse.quote(repo, safe='')
            endpoint = f'/repos/{encoded_owner}/{encoded_repo}/contents/{encoded_path}'
            contents = self._make_request(endpoint)

            blend_files = []
            if isinstance(contents, list):
                for item in contents:
                    if item.get('name', '').endswith('.blend'):
                        blend_files.append(item)
            elif isinstance(contents, dict):
                if contents.get('name', '').endswith('.blend'):
                    blend_files.append(contents)

            return True, blend_files, ""

        except urllib.error.HTTPError as e:
            if e.code == 404:
                return True, [], ""
            return False, [], f"API error: HTTP {e.code}"
        except Exception as e:
            return False, [], f"Error finding files: {str(e)}"

    def download_file(self, owner: str, repo: str, file_path: str,
                      destination: str) -> Tuple[bool, str]:
        """
        Download a file from a GitHub repository.
        Returns: (success, error_message)
        """
        if not self.is_authenticated():
            return False, "Not authenticated"

        try:
            # Get file info to obtain the download URL
            encoded_path = urllib.parse.quote(file_path, safe='/')
            encoded_owner = urllib.parse.quote(owner, safe='')
            encoded_repo = urllib.parse.quote(repo, safe='')
            endpoint = f'/repos/{encoded_owner}/{encoded_repo}/contents/{encoded_path}'
            file_info = self._make_request(endpoint)

            download_url = file_info.get('download_url')
            if not download_url:
                return False, "No download URL available for this file"

            # Download the file with authentication
            req = urllib.request.Request(download_url)
            req.add_header('Authorization', f'token {self.token}')
            req.add_header('User-Agent', 'Blender-Classroom-Addon')

            with urllib.request.urlopen(req) as response:
                with open(destination, 'wb') as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)

            return True, ""

        except urllib.error.HTTPError as e:
            return False, f"Download error: HTTP {e.code}"
        except Exception as e:
            return False, f"Error downloading file: {str(e)}"

    def upload_file(self, owner: str, repo: str, file_path: str,
                    local_path: str,
                    message: str = "Save from Blender") -> Tuple[bool, str]:
        """
        Upload or update a file in a GitHub repository (creates a commit).
        Returns: (success, error_message)
        """
        if not self.is_authenticated():
            return False, "Not authenticated"

        try:
            # Read the local file and base64 encode it
            with open(local_path, 'rb') as f:
                content = base64.b64encode(f.read()).decode('utf-8')

            # Check if file already exists to get its SHA (needed for updates)
            sha = None
            encoded_path = urllib.parse.quote(file_path, safe='/')
            encoded_owner = urllib.parse.quote(owner, safe='')
            encoded_repo = urllib.parse.quote(repo, safe='')
            try:
                existing = self._make_request(
                    f'/repos/{encoded_owner}/{encoded_repo}/contents/{encoded_path}'
                )
                sha = existing.get('sha')
            except urllib.error.HTTPError:
                pass

            # Create or update the file
            committer_name = self.username or 'Blender User'
            committer_id = self.username or 'blender'
            data = {
                'message': message,
                'content': content,
                'committer': {
                    'name': committer_name,
                    'email': f'{committer_id}@users.noreply.github.com',
                },
            }
            if sha:
                data['sha'] = sha

            self._make_request(
                f'/repos/{encoded_owner}/{encoded_repo}/contents/{encoded_path}',
                method='PUT',
                data=data
            )

            return True, ""

        except urllib.error.HTTPError as e:
            return False, f"Upload error: HTTP {e.code}"
        except Exception as e:
            return False, f"Error uploading file: {str(e)}"

    # --- Settings management ---

    def _load_settings(self):
        """Load addon settings from config"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    self.advanced_mode = data.get('advanced_mode', False)
                    self.auto_push_mode = data.get(
                        'auto_push_mode', AUTO_PUSH_ON_SAVE
                    )
                    self.upload_renders_on_complete = data.get(
                        'upload_renders_on_complete', False
                    )
            except (json.JSONDecodeError, IOError):
                pass

    def _save_settings(self):
        """Save addon settings to config"""
        data = {
            'advanced_mode': self.advanced_mode,
            'auto_push_mode': self.auto_push_mode,
            'upload_renders_on_complete': self.upload_renders_on_complete,
        }
        with open(self.settings_file, 'w') as f:
            json.dump(data, f)

    def set_auto_push_mode(self, mode: str):
        """Set auto-push mode: ON_SAVE, MANUAL, or ON_QUIT"""
        self.auto_push_mode = mode
        self._save_settings()

    def set_upload_renders_on_complete(self, value: bool):
        """Enable or disable automatic render upload on render complete"""
        self.upload_renders_on_complete = value
        self._save_settings()

    # --- Working file management (for auto-push on save) ---

    def set_working_file(self, repo_owner: str, repo_name: str,
                         file_path: str):
        """Set the current working file info for auto-push"""
        self.working_file = {
            'repo_owner': repo_owner,
            'repo_name': repo_name,
            'file_path': file_path,
        }
        self._save_working_file()

    def get_working_file(self) -> Optional[Dict[str, str]]:
        """Get the current working file info"""
        return self.working_file

    def clear_working_file(self):
        """Clear the current working file info"""
        self.working_file = None
        if os.path.exists(self.working_file_config):
            os.remove(self.working_file_config)

    def _save_working_file(self):
        """Save working file info to config"""
        if self.working_file:
            with open(self.working_file_config, 'w') as f:
                json.dump(self.working_file, f)

    def _load_working_file(self):
        """Load working file info from config"""
        if os.path.exists(self.working_file_config):
            try:
                with open(self.working_file_config, 'r') as f:
                    data = json.load(f)
                    # Backward compat: migrate auto_push bool to mode
                    if 'auto_push' in data:
                        old_val = data.pop('auto_push')
                        if old_val:
                            self.auto_push_mode = AUTO_PUSH_ON_SAVE
                        else:
                            self.auto_push_mode = AUTO_PUSH_MANUAL
                        self._save_settings()
                    self.working_file = data if data else None
            except (json.JSONDecodeError, IOError):
                self.working_file = None

    # --- URL parsing ---

    @staticmethod
    def parse_repo_url(url: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse a GitHub URL into (owner, repo). Returns (None, None) on failure."""
        url = url.strip().rstrip('/')
        if url.endswith('.git'):
            url = url[:-4]

        # Use proper URL parsing to avoid substring matching issues
        if '://' not in url:
            url = 'https://' + url
        parsed = urllib.parse.urlparse(url)
        if parsed.hostname != 'github.com':
            return None, None

        # Extract path components (e.g. /owner/repo/...)
        path_parts = [p for p in parsed.path.split('/') if p]
        if len(path_parts) >= 2 and path_parts[0] and path_parts[1]:
            return path_parts[0], path_parts[1]
        return None, None

    # --- Assignment grouping (for teacher view) ---

    @staticmethod
    def compute_assignment_groups(
        repo_names: List[str],
    ) -> Dict[str, str]:
        """
        Compute assignment grouping for teacher view.
        Uses the GitHub Classroom naming convention: {assignment}-{username}
        Returns a dict mapping repo_name -> assignment_name.
        Repos that don't match any group get an empty assignment_name.
        """
        # Count how many repos share each possible hyphen-delimited prefix
        prefix_counts: Dict[str, int] = {}
        for name in repo_names:
            parts = name.split('-')
            for i in range(1, len(parts)):
                prefix = '-'.join(parts[:i])
                prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1

        # For each repo, find the longest prefix shared with at least
        # one other repo. That prefix is the assignment name.
        result: Dict[str, str] = {}
        for name in repo_names:
            parts = name.split('-')
            best_prefix = ''
            for i in range(len(parts) - 1, 0, -1):
                prefix = '-'.join(parts[:i])
                if prefix_counts.get(prefix, 0) >= 2:
                    best_prefix = prefix
                    break
            result[name] = best_prefix

        return result


# Global client instance
_github_client_instance = None


def get_github_client() -> GitHubClassroomClient:
    """Get or create the global GitHub client instance"""
    global _github_client_instance
    if _github_client_instance is None:
        _github_client_instance = GitHubClassroomClient()
    return _github_client_instance

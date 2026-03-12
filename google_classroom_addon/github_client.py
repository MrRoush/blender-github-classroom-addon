"""
GitHub Classroom API client module
Handles authentication and API calls to GitHub for classroom integration
"""

import os
import json
import base64
import urllib.request
import urllib.error
from typing import Optional, List, Dict, Any, Tuple

GITHUB_API_URL = "https://api.github.com"


class GitHubClassroomClient:
    """Client for interacting with GitHub for classroom assignments"""

    def __init__(self):
        self.token = None
        self.username = None
        self.config_dir = self._get_config_dir()
        self.token_file = os.path.join(self.config_dir, 'github_token.json')

    def _get_config_dir(self) -> str:
        """Get configuration directory for storing credentials"""
        addon_dir = os.path.dirname(os.path.realpath(__file__))
        config_dir = os.path.join(addon_dir, 'config')
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
        Authenticate with GitHub using a Personal Access Token
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
                return False, "Invalid token. Please check your Personal Access Token."
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

    def get_repos(self, org_name: str) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Get assignment repos for the authenticated user in an organization.
        GitHub Classroom creates repos with the student's username in the name.
        Returns: (success, repos_list, error_message)
        """
        if not self.is_authenticated():
            return False, [], "Not authenticated"

        try:
            # Get repos the user has access to as collaborator or org member
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

            # Filter to repos in the specified organization
            org_lower = org_name.lower()
            filtered = [
                r for r in all_repos
                if r.get('owner', {}).get('login', '').lower() == org_lower
            ]

            return True, filtered, ""

        except urllib.error.HTTPError as e:
            return False, [], f"API error: HTTP {e.code}"
        except Exception as e:
            return False, [], f"Error fetching repos: {str(e)}"

    def find_blend_files(self, owner: str, repo: str,
                         path: str = '') -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Find .blend files in a repository
        Returns: (success, blend_files_list, error_message)
        """
        if not self.is_authenticated():
            return False, [], "Not authenticated"

        try:
            endpoint = f'/repos/{owner}/{repo}/contents/{path}'
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
        Download a file from a GitHub repository
        Returns: (success, error_message)
        """
        if not self.is_authenticated():
            return False, "Not authenticated"

        try:
            # Get file info to obtain the download URL
            endpoint = f'/repos/{owner}/{repo}/contents/{file_path}'
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
                    message: str = "Submit assignment from Blender") -> Tuple[bool, str]:
        """
        Upload or update a file in a GitHub repository (creates a commit)
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
            try:
                existing = self._make_request(
                    f'/repos/{owner}/{repo}/contents/{file_path}'
                )
                sha = existing.get('sha')
            except urllib.error.HTTPError:
                pass

            # Create or update the file
            data = {
                'message': message,
                'content': content,
                'committer': {
                    'name': self.username or 'Blender User',
                    'email': f'{self.username or "blender"}@users.noreply.github.com',
                },
            }
            if sha:
                data['sha'] = sha

            self._make_request(
                f'/repos/{owner}/{repo}/contents/{file_path}',
                method='PUT',
                data=data
            )

            return True, ""

        except urllib.error.HTTPError as e:
            return False, f"Upload error: HTTP {e.code}"
        except Exception as e:
            return False, f"Error uploading file: {str(e)}"


# Global client instance
_github_client_instance = None


def get_github_client() -> GitHubClassroomClient:
    """Get or create the global GitHub client instance"""
    global _github_client_instance
    if _github_client_instance is None:
        _github_client_instance = GitHubClassroomClient()
    return _github_client_instance

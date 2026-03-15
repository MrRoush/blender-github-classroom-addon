# Changelog

All notable changes to the GitHub Classroom Blender Add-on will be documented in this file.

## [3.0.0] - 2026-03-15

### Added
- **Simple/Advanced mode toggle**: New toggle at the top of the panel controls UI complexity.
  Simple mode hides advanced options for a cleaner student experience.
- **Advanced mode features**:
  - **Role selector** (Student/Teacher) — only visible in advanced mode
  - **Custom commit messages** — optional text field (auto-generates if left blank)
  - **Auto-push mode selector** — choose between On Save, Manual, or On Quit
  - **Repository URL input** — manually enter a GitHub repo URL and pull .blend files
  - **Pull from URL button** — download and open .blend files from any repo URL
- **Teacher assignment grouping**: In teacher mode, repositories are grouped by assignment
  name with collapsible folders. Uses GitHub Classroom naming convention
  ({assignment}-{username}) to detect groups automatically.
- **On Quit auto-push mode**: New option to push changes when closing Blender
  (via load_pre handler)
- **Settings persistence**: Advanced mode and auto-push mode saved in settings.json

### Changed
- Default UI is now Simple mode (student-focused, auto-push on save)
- Auto-push toggle replaced with three-mode selector (On Save / Manual / On Quit)
- Working file status section now visible for all authenticated users with a working file
  (previously student-only)
- Version bumped to 3.0.0

### Removed
- `GITHUB_OT_ToggleAutoPush` operator (replaced by `GITHUB_OT_SetAutoPushMode`)

### Compatibility
- Backward-compatible with v2.0.0 working_file.json format (auto_push bool migrated)
- Blender 4.5 LTS or later
- GitHub API v3
- Python 3.11+ (included with Blender)

## [2.0.0] - 2025-01-15

### Changed
- **Converted from Google Classroom to GitHub Classroom only**
- Renamed add-on from "Classroom Integration" to "GitHub Classroom"
- Renamed package from `google_classroom_addon` to `github_classroom_addon`
- Simplified UI for non-programmer students (art/animation students)
- Removed platform toggle (GitHub Classroom is now the only platform)

### Added
- **Student/Teacher role selector** for role-specific workflows
- **Auto-push on save**: Student work is automatically pushed to GitHub when saving (Ctrl+S)
- **Teacher repository browsing**: Teachers can see all student repos in the org for grading
- **Working file tracking**: Addon remembers which repo/file you're working on
- **Toggle auto-push**: Students can enable/disable auto-push from the UI
- **Disconnect button**: Students can disconnect from the current repo

### Removed
- Google Classroom integration (api_client.py)
- Google OAuth credentials template and setup
- Python dependency requirements (requirements.txt) — addon now uses only stdlib
- Dependency installation helper (install_dependencies.py)
- Platform selection toggle (Google/GitHub)
- Google Classroom courses and assignments panels

### Security
- Local-only token storage (GitHub Personal Access Token)
- Working file config stored locally
- No external Python dependencies required

### Compatibility
- Blender 4.5 LTS or later
- GitHub API v3
- Python 3.11+ (included with Blender)

## [1.0.0] - 2024-12-23

### Added
- Initial release with Google Classroom and GitHub Classroom support

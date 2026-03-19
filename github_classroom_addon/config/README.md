# Configuration Directory

This directory is part of the add-on source and contains only documentation.

Credential and state files are stored **per OS user account** so that students
sharing the same computer cannot access each other's tokens or work.

## Storage Location

The actual config files are written to the current OS user's personal directory:

- **When running inside Blender**: `<Blender user data>/classroom_addon/`
  - Windows: `%APPDATA%\Blender Foundation\Blender\<version>\classroom_addon\`
  - Linux: `~/.config/blender/<version>/classroom_addon/`
  - macOS: `~/Library/Application Support/Blender/<version>/classroom_addon/`
- **Fallback (e.g., unit tests)**: `~/.blender_classroom_addon/`

## Files

### `github_token.json`
- Created automatically when you sign in with your GitHub Personal Access Token
- Contains your saved token so you don't need to sign in every time
- **Do not share this file** — it contains your authentication credentials
- To remove it, click **Sign Out** in the add-on, or delete the file manually

### `working_file.json`
- Created automatically when you open a .blend file from a repository
- Tracks which repository and file you're working on for auto-push
- Safe to delete if you want to disconnect from a repository

### `settings.json`
- Stores add-on preferences (advanced mode, auto-push mode, etc.)
- Safe to delete; defaults will be restored on next launch

## Getting a GitHub Personal Access Token

1. Go to **GitHub.com** → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **Generate new token (classic)**
3. Give it a name like "Blender Classroom"
4. Select the **repo** scope (full control of repositories)
5. Click **Generate token**
6. **Copy the token** — you won't be able to see it again!
7. Paste the token into the add-on's "Token" field

## Security

- Each OS user account has its own separate token file in their home directory
- When a student logs out of the computer, the next student who logs in will **not** be auto-authenticated as the previous student
- Token and working file data are listed in `.gitignore` and will not be uploaded to GitHub
- If you suspect your token has been compromised, revoke it on GitHub and generate a new one

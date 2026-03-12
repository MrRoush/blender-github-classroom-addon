# Configuration Directory

This directory stores your authentication credentials and tokens.

## Google Classroom Setup

### credentials.json
Your OAuth 2.0 client credentials from Google Cloud Console.

**How to get this file:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable Google Classroom API and Drive API
3. Create OAuth 2.0 credentials (Desktop app type)
4. Download the JSON file
5. Rename it to `credentials.json`
6. Place it in this directory

**Template:** See `credentials.json.template` for the expected format.

### token.pickle
Automatically created after first successful Google authentication. Contains your access and refresh tokens.

## GitHub Classroom Setup

GitHub Classroom **does not** require Google Cloud Console access.

### github_token.json
Automatically created after first successful GitHub authentication. Contains your Personal Access Token.

**How to create a GitHub Personal Access Token:**
1. Go to [GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)](https://github.com/settings/tokens)
2. Click **Generate new token (classic)**
3. Give it a descriptive name (e.g., "Blender Classroom Add-on")
4. Select the **repo** scope (Full control of private repositories)
5. Click **Generate token**
6. Copy the token and paste it into the add-on's Token field in Blender

**Note:** The token is entered in Blender's sidebar panel and saved automatically.

## Security Notes

- **Never commit credentials.json, token.pickle, or github_token.json to version control**
- These files are listed in .gitignore
- Keep credentials.json secure but it can be shared with your class
- Each user's token.pickle / github_token.json is unique to their account
- Students can revoke GitHub token access anytime via GitHub Settings
- Students can revoke Google access anytime via Google Account settings

## File Locations

When add-on is installed in Blender:
- Windows: `%APPDATA%\Blender Foundation\Blender\4.5\scripts\addons\google_classroom_addon\config\`
- macOS: `~/Library/Application Support/Blender/4.5/scripts/addons/google_classroom_addon/config/`
- Linux: `~/.config/blender/4.5/scripts/addons/google_classroom_addon/config/`

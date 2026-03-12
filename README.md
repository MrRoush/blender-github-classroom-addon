# Blender Classroom Add-on

A Blender 4.5 LTS add-on that integrates **Google Classroom** and **GitHub Classroom** directly into Blender, making it easy for students to access assignments, download .blend files, and submit completed work without leaving the 3D environment.

## Overview

This add-on is designed for computer animation classes that use Blender. It supports two classroom platforms:

### Google Classroom
- Requires Google Cloud Console access for OAuth credentials
- Viewing Google Classroom assignments directly in Blender
- Downloading starter .blend files attached to assignments
- Submitting completed assignments back to Google Classroom
- Tracking assignment status and due dates

### GitHub Classroom (No Cloud Console Required)
- Uses a GitHub Personal Access Token — **no admin or cloud console access needed**
- Viewing GitHub Classroom assignment repositories in Blender
- Downloading starter .blend files from assignment repos
- Submitting completed work by pushing to the assignment repo
- Works with any GitHub Classroom organization

## Quick Start

### GitHub Classroom (Recommended if you lack Google Cloud Console access)

1. Install the add-on in Blender (Edit > Preferences > Add-ons)
2. Open the **Classroom** sidebar panel (View3D > Sidebar > Classroom)
3. Select **GitHub Classroom** as the platform
4. Create a [GitHub Personal Access Token](https://github.com/settings/tokens) with the **repo** scope
5. Enter your token and sign in
6. Enter your classroom organization name
7. Browse assignment repos and open/submit .blend files

### Google Classroom

1. Install Python dependencies into Blender's Python environment
2. Install the add-on in Blender (Edit > Preferences > Add-ons)
3. Set up Google API credentials (see [INSTALL_GUIDE.md](INSTALL_GUIDE.md))
4. Select **Google Classroom** as the platform
5. Sign in with your Google account
6. Browse courses and assignments

## Documentation

For detailed installation and setup instructions, see [INSTALL_GUIDE.md](INSTALL_GUIDE.md)

## Features

### For Students
- 📚 View active courses / assignment repos
- 📝 Browse assignments with due dates
- 📥 Download .blend assignment files with one click
- 📤 Submit completed work directly from Blender
- ✅ Track submission status

### For Teachers
- Easy distribution of starter files
- Streamlined assignment collection
- Works with existing Google Classroom or GitHub Classroom workflow
- GitHub Classroom requires no special cloud admin access

## Requirements

- Blender 4.5 LTS or later
- Internet connection
- **For GitHub Classroom:** A GitHub account and Personal Access Token
- **For Google Classroom:** Google Classroom account and Google Cloud project with API credentials

## Project Structure

```
google_classroom_addon/
├── __init__.py              # Add-on entry point
├── properties.py            # Blender property definitions
├── operators.py             # User action handlers (Google + GitHub)
├── ui.py                    # UI panel definitions (Google + GitHub)
├── api_client.py            # Google Classroom API client
├── github_client.py         # GitHub Classroom API client
├── requirements.txt         # Python dependencies (Google mode only)
├── install_dependencies.py  # Dependency installer helper
└── config/
    ├── credentials.json.template  # Google OAuth credentials template
    └── README.md                  # Configuration guide
```

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## License

This project is provided as-is for educational purposes. Please ensure compliance with your institution's policies, Google's Terms of Service, and GitHub's Terms of Service.

## Support

For detailed documentation, troubleshooting, and setup instructions, see [INSTALL_GUIDE.md](INSTALL_GUIDE.md)

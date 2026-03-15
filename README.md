# Blender GitHub Classroom Add-on

A Blender 4.5 LTS add-on that integrates **GitHub Classroom** directly into Blender, making it easy for students to pull assignment .blend files, work on them, and push their changes back — all without leaving the 3D environment. Teachers can also use the add-on to pull student files for review and grading.

## Overview

This add-on is designed for animation and 3D art courses that use Blender. It connects to **GitHub Classroom** using a simple Personal Access Token — no complex setup or cloud admin access required.

The add-on features a **Simple/Advanced mode** toggle:
- **Simple mode** (default): A clean, student-focused interface with auto-push on save
- **Advanced mode**: Additional options for power users — role switching, custom commit messages, auto-push mode selection, and manual repository URL entry

### For Students
- 📥 **Pull** your assignment .blend file from your GitHub Classroom repository
- 🎨 Work on your project in Blender as usual
- 📤 **Auto-push** your changes to GitHub every time you save (or push manually)
- ✏️ **Custom commit messages** (advanced mode) — describe your changes
- 🔗 **Pull from URL** (advanced mode) — open any repo by pasting its GitHub URL
- No programming knowledge required — just enter your token and go!

### For Teachers
- 📂 **Browse** all student repositories in your GitHub Classroom organization
- 📁 **Assignment grouping** — repos sorted by assignment name with collapsible folders
- 📥 **Pull** any student's .blend file to review their progress
- Grade work by opening student files directly in Blender
- Monitor student progress throughout projects

## Quick Start

### Students

1. Install the add-on in Blender (Edit → Preferences → Add-ons → Install)
2. Open the **Classroom** sidebar panel (press N in the 3D Viewport → Classroom tab)
3. Create a [GitHub Personal Access Token](https://github.com/settings/tokens) with the **repo** scope
4. Enter your token and click **Sign In**
5. Enter your classroom organization name and click **Load My Assignments**
6. Select a repository and click **Open Assignment** to download and open your .blend file
7. Work on your project — your changes are **automatically pushed to GitHub when you save**!

### Teachers

1. Install the add-on in Blender (Edit → Preferences → Add-ons → Install)
2. Open the **Classroom** sidebar panel (press N in the 3D Viewport → Classroom tab)
3. Enable **Show Advanced Options** and select **Teacher** as your role
4. Sign in with your GitHub Personal Access Token
5. Enter your classroom organization name and click **Load Student Repos**
6. Expand an assignment folder and select a student's repository
7. Click **Open for Review** to download and open the student's .blend file

## Requirements

- Blender 4.5 LTS or later
- Internet connection
- A GitHub account and [Personal Access Token](https://github.com/settings/tokens) with the **repo** scope
- **No external Python dependencies required** — uses only Python standard library

## Documentation

- [INSTALL_GUIDE.md](INSTALL_GUIDE.md) — Detailed installation instructions
- [TEACHER_GUIDE.md](TEACHER_GUIDE.md) — Teacher setup and grading workflow
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) — Daily usage quick reference
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Common issues and solutions

## Project Structure

```
github_classroom_addon/
├── __init__.py          # Add-on entry point and registration
├── properties.py        # Blender property definitions
├── operators.py         # User action handlers and save handler
├── ui.py                # UI panel definitions
├── github_client.py     # GitHub API client (stdlib only)
└── config/
    └── README.md        # Configuration guide
```

## How It Works

1. **Authentication**: Students and teachers sign in with a GitHub Personal Access Token
2. **Repository Listing**: Students see their own assignment repos; teachers see all repos in the organization grouped by assignment
3. **File Operations**: .blend files are downloaded from GitHub and opened in Blender
4. **Auto-Push**: When students save their work (Ctrl+S), changes are automatically pushed back to their GitHub repository (default behavior; can be changed to manual or on-quit in advanced mode)
5. **Teacher Review**: Teachers can pull any student's file to review progress and grade work

## Advanced Mode

Enable **Show Advanced Options** to access additional features:

| Feature | Description |
|---------|-------------|
| **Role Selector** | Switch between Student and Teacher modes |
| **Commit Message** | Write a custom message describing your changes |
| **Auto-Push Mode** | Choose: On Save (default), Manual, or On Quit |
| **Repository URL** | Enter a GitHub repo URL to pull from directly |
| **Pull from URL** | Download a .blend file from any GitHub repository |

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## License

This project is provided as-is for educational purposes. Please ensure compliance with your institution's policies and GitHub's Terms of Service.

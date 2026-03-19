# Troubleshooting Guide

Common issues and solutions for the GitHub Classroom Blender Add-on.

## Installation Issues

### Problem: Add-on doesn't appear in preferences

**Solution:**
1. Make sure you installed the folder, not a single file
2. Check the folder name is `github_classroom_addon`
3. Look in the **System** category
4. Restart Blender

### Problem: Add-on fails to enable

**Solution:**
1. Open Blender's system console (Window > Toggle System Console on Windows)
2. Look for Python error messages
3. Ensure you're running Blender 4.5 or later
4. Try reinstalling the add-on

## Authentication Issues

### Problem: "No token provided"

**Solution:**
1. Create a Personal Access Token at [github.com/settings/tokens](https://github.com/settings/tokens)
2. Select the **repo** scope when creating the token
3. Copy the token and paste it into the Token field
4. Click Sign In

### Problem: "Invalid token"

**Causes:**
- Token was typed incorrectly
- Token has expired
- Token was revoked
- Token doesn't have the **repo** scope

**Solution:**
1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Check if your token is still active
3. If not, create a new one with the **repo** scope
4. Copy and paste carefully (no extra spaces)

### Problem: "Authentication failed"

**Solution:**
1. Check your internet connection
2. Verify GitHub isn't experiencing an outage
3. Try signing out and back in
4. Delete the token file (`github_classroom_addon/config/github_token.json`) and re-authenticate

### Problem: SSL Certificate Verification Error (Blender 4.2+ on macOS or managed Windows)

**Error message:**
```
Authentication failed: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1006)>
```

**Cause:**
Blender bundles its own Python interpreter, which does not automatically use the system's SSL certificate store. On macOS and some managed school/lab Windows machines running Blender 4.2 or later, Python cannot verify GitHub's SSL certificate using the default settings.

**Fix:**
This error has been resolved in the add-on (v3.0.0 and later). The add-on now creates a proper SSL context using `ssl.create_default_context()` for all network requests. If you are seeing this error, make sure you are using the latest version of the add-on.

If the error persists after updating, you can also install the `certifi` package into Blender's Python to provide a bundled certificate store:
1. Find Blender's bundled Python executable (e.g., `<blender_install_dir>/python/bin/python3` on Linux/macOS, or `<blender_install_dir>\python\python.exe` on Windows)
2. Run from a terminal: `"<path_to_blender_python>" -m pip install certifi`
3. Restart Blender and try again

## Usage Issues

### Problem: No repositories found

**Solution:**
1. Verify the organization name is correct (case-sensitive)
2. Students: Make sure you've accepted the GitHub Classroom assignment
3. Teachers: Make sure you're an owner/member of the organization
4. Try clicking "Load My Assignments" or "Load Student Repos" again

### Problem: "No .blend file found" in a repository

**Solution:**
1. The repository may not have a .blend file yet
2. Check that the template repo includes a .blend file in the root directory
3. The add-on only checks the root directory of the repository

### Problem: Can't open assignment file

**Causes:**
- No internet connection
- File permissions issue
- Insufficient disk space

**Solution:**
1. Check internet connection
2. Verify you have permission to access the repository
3. Check free disk space in temp directory
4. Try downloading the file manually from GitHub

### Problem: Auto-push not working

**Causes:**
- Auto-push is disabled
- File wasn't opened from the add-on
- Not authenticated

**Solution:**
1. Check that auto-push is enabled (checkbox in the Classroom panel)
2. Open the file from the add-on (not File > Open)
3. Verify you're signed in
4. Check internet connection
5. Try a manual push with "Save & Push to GitHub"

### Problem: "Upload error" when pushing

**Solution:**
1. Check internet connection
2. Verify you have write access to the repository
3. File may be too large for GitHub's API (limit: 100MB per file)
4. Try pushing again — it may be a temporary network issue

## Performance Issues

### Problem: Slow to load repositories

**Solution:**
- This is normal for organizations with many repositories
- Each repo is checked for .blend files, which adds time
- Try on a faster internet connection

### Problem: Blender freezes during operation

**Causes:**
- Large file download/upload
- Slow network
- API timeout

**Solution:**
- Wait for the operation to complete
- Check network connection
- Close and restart Blender if truly frozen

## Data Issues

### Problem: Working file disconnected after reopening Blender

**Solution:**
- This can happen if Blender was closed unexpectedly
- Simply open the file from the add-on again
- The add-on saves working file state in `config/working_file.json`

### Problem: Repositories not showing latest changes

**Solution:**
- Click "Load My Assignments" or "Load Student Repos" to refresh
- Repository data is fetched fresh each time you load

## Network Issues

### Problem: "API error" messages

**Solution:**
1. Check internet connection
2. Verify GitHub services aren't experiencing issues
3. Check if GitHub is blocked by your network/firewall
4. Try again in a few minutes

### Problem: Timeout errors

**Solution:**
1. Check your internet speed
2. Try on a different network
3. Large files take longer to upload/download

## Advanced Troubleshooting

### Enable Blender's Python Console

1. Window > Toggle System Console (Windows)
2. Check console for error messages
3. Look for Python tracebacks

### Reset Add-on Completely

1. Sign out from add-on
2. Disable and remove add-on in Blender preferences
3. Delete the `github_classroom_addon` folder from Blender's addons directory
4. Delete config files (`github_token.json`, `working_file.json`)
5. Reinstall from scratch

### Check GitHub API Status

- [GitHub Status](https://www.githubstatus.com/) — Check if GitHub is experiencing issues

## Still Having Issues?

If none of these solutions work:

1. **Check existing GitHub issues**: Someone may have had the same problem
2. **Create a new issue** with:
   - Blender version
   - Operating system
   - Error messages
   - Steps to reproduce
3. **Ask your teacher** — They may be able to help troubleshoot

## Getting Help

- GitHub Issues: [Report a bug](https://github.com/MrRoush/blender-addon/issues)
- Documentation: Check [INSTALL_GUIDE.md](INSTALL_GUIDE.md) and [TEACHER_GUIDE.md](TEACHER_GUIDE.md)

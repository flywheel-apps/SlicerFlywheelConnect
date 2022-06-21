# Flywheel Connect Known Issues

## Reloading Saved MRML File Across Users
The .mrml file can reference multiple files.  These files may be a part of another user's directory structure (.e.g. /home/{user1}/FlywheelIO/... vs. /Users/{user1}/FlywheelIO).

When the mrml file is loaded without the accompanying file existing on the file system, Slicer will crash.

### Potential Solutions
- use relative references.
- Check the mrml file before attempting to load.
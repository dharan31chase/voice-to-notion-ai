# Staging Folder

This folder is used for temporary storage of audio files during transcription processing.

## Purpose
- Copy MP3 files from USB recorder to fast local SSD storage
- Eliminates USB I/O bottleneck during transcription
- Files are automatically cleaned up after successful archiving

## Safety
- Original files remain on USB until successful archive
- Only deleted after confirmation of archive completion
- Recovery-friendly: If process crashes, files remain on USB

## Maintenance
- Automatically cleaned after each successful run
- Manual cleanup: Delete all files in this folder when no processing is active

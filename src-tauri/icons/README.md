# Hearthlink Native Icons

This directory contains the application icons for the Hearthlink Native Windows installer.

## Required Files:
- `32x32.png` - Small icon (32x32 pixels)
- `128x128.png` - Standard icon (128x128 pixels)  
- `128x128@2x.png` - High-DPI icon (256x256 pixels)
- `icon.ico` - Windows ICO format (multi-resolution)
- `icon.icns` - macOS icon format (for future cross-platform support)

## Current Status:
These are placeholder icons. Replace with actual Hearthlink branding assets before final production release.

## Icon Requirements:
- PNG files should be square and properly sized
- ICO file should contain multiple resolutions (16x16, 32x32, 48x48, 64x64, 128x128, 256x256)
- Icons should be optimized for clarity at all sizes
- Recommended: Use transparent backgrounds where appropriate

## Automated Generation:
You can generate these icons from a single high-resolution source (512x512 or larger) using tools like:
- ImageMagick: `convert source.png -resize 32x32 32x32.png`
- Online converters: favicon.io, realfavicongenerator.net
- Design tools: Figma, Photoshop, GIMP
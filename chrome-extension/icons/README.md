# Extension Icons

This directory should contain three PNG icons:

- `icon16.png` - 16x16px (toolbar icon)
- `icon48.png` - 48x48px (extension management page)
- `icon128.png` - 128x128px (Chrome Web Store)

## Temporary Solution

For testing purposes, you can use any PNG images renamed to these filenames.

Create simple colored squares using any image editor or online tool:
- https://placeholder.com/
- Or use Paint/GIMP to create solid color squares

## Suggested Design

- Background: Brain/memory theme
- Colors: Blue (#007bff) and white
- Simple, recognizable icon
- Should work well at small sizes

## Quick Generation

Using ImageMagick (if installed):
```bash
convert -size 16x16 xc:#007bff icon16.png
convert -size 48x48 xc:#007bff icon48.png
convert -size 128x128 xc:#007bff icon128.png
```

Or download placeholder images:
```bash
curl https://via.placeholder.com/16/007bff/ffffff?text=M -o icon16.png
curl https://via.placeholder.com/48/007bff/ffffff?text=M -o icon48.png
curl https://via.placeholder.com/128/007bff/ffffff?text=M -o icon128.png
```

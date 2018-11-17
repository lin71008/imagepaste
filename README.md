Ima![](README/README0.png)gePaste
==========

Simple plugin for insert image from clipboard at the cursor position.

# Installation

In Sublime press `Ctrl+Shift+P` -> `Package Control: Install Package` -> `ImagePaste`

## for Windows

```bash
python3 -m pip install Pillow
```

## for Linux 

```bash
sudo apt install xclip
```

# Usage

```json
[
	{
	    "caption": "ImagePaste: Paste Image From Clipboard",
	    "command": "image_paste"
	},
	{
	    "caption": "ImagePreview: Preview Markdown Images",
	    "command": "image_preview"
	}
]
```

Take a screenshot, then press `Ctrl+V` to paste it.
It will save a png file to subdirectory (you can specify it in `imagepaste.sublime-settings`) and insert the file path in the current cursor position.

#TODO

- [x] Rewrite old code
- [x] Paste PNG from clipboard
- [ ] Add Linux support
- [ ] Preview image in markdown
- [ ] Paste GIF from clipboard

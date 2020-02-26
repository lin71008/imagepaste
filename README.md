ImagePaste
==========

Sublime plugin to insert image from clipboard at the cursor position.
Forked from https://github.com/uhx/imagepaste

* Supports OSX (through `pngpaste`)
* Supports Linux (through `xclip`)
* Upstream supported Win32 too, but it hasn't been tested.

# Requirements

## Windows

Depends on `Pillow`, which should be bundled.

## Linux

Install `xclip` through your favourite manager.

## OS X

Depends on [`pngpaste`](https://github.com/jcsalterego/pngpaste)

```
brew install pngpaste
```

Change the location of executable in `imagepaste.sublime-settings` if neccessary.

# Installation

Through Package Control:

`Ctrl+Shift+P` -> `Package Control: Add Repository` -> `https://github.com/lukauskas/imagepaste`

Then:

`Ctrl+Shift+P` -> `Package Control: Install Package` -> `imagepaste`

# Usage

Script overrides ctrl+v (or cmd+v on mac os x) to paste image into selected folder.
By default script writes to the directory 'images' in the current path, but this can be modified in

`imagepaste.sublime-settings`

Script will automatically insert appropriate markdown.

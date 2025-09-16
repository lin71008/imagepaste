import sublime
import sublime_plugin
import os
import sys
import re
import datetime

from imagepaste.utils import os_appropriate_utils

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)', text) ]

class ImagePasteBase(object):
    def __init__(self, *args, **kwgs):
        super(ImagePasteBase, self).__init__(*args, **kwgs)
        self.settings = sublime.load_settings('imagepaste.sublime-settings')

        # get the image save dirname
        self.image_directory = self.settings.get('image_directory_name', None)
        self.paste_absolute_path = self.settings.get('paste_absolute_path', False)

        if not self.image_directory:
            self.image_directory = None

    def paste_absolute(self):
        return self.paste_absolute_path

    def get_current_filename(self):
        '''
        returns filename without extension
        '''
        fullpath, extension = os.path.splitext(self.view.file_name())

        basename = os.path.basename(fullpath)

        return basename

    def get_current_dir(self):
        return os.path.dirname(self.view.file_name())

    def get_image_directory(self):
        ''' relative path to image directory '''
        root_dir = self.image_directory

        subdir_name = self.get_current_filename()

        # sanitize the name a bit
        subdir_name = re.sub('[^a-zA-Z0-9]+', '_', subdir_name)

        if root_dir:
            return os.path.join(root_dir, subdir_name)
        else:
            return subdir_name

    def get_image_abs_directory(self):
        ''' full path to image directory '''
        return os.path.join(self.get_current_dir(), self.get_image_directory())

    def get_image_path(self):
        abs_directory = self.get_image_abs_directory()
        rel_directory = self.get_image_directory()

        now = datetime.datetime.now()

        filename = '{0:%Y}{0:%m}{0:%d}{0:%H}{0:%M}{0:%S}.png'.format(now)

        abs_path = os.path.join(abs_directory, filename)
        rel_path = os.path.join(rel_directory, filename)

        return abs_path, rel_path

class ImagePasteCommand(ImagePasteBase, sublime_plugin.TextCommand):
    def __init__(self, *args, **kwgs):
        super(ImagePasteCommand, self).__init__(*args, **kwgs)
        self.image_data = None
        self.image_path = ''

        self.os_utils = os_appropriate_utils(self.settings)

    def run(self, edit):
        view = self.view
        try:
            image_data = self.os_utils.get_clipboard_image()
        except Exception:
            # Fallback to normal paste
            view.run_command('paste')
            raise

        if image_data is None:
            # as normal Ctrl+V
            view.run_command('paste')
            return

        if self.image_data != image_data:
            image_abs_path, image_rel_path = self.save_image(image_data)

            if self.paste_absolute():
                image_path = image_abs_path
            else:
                image_path = image_rel_path

            if not image_path:
                return

            # fix image path for html
            image_path = image_path.replace('\\', '/')
            self.image_path = image_path
            self.image_data = image_data

        selections = view.sel()

        if not selections:
            return
        # get the cursor
        selection_pos = selections[0].begin()

        if view.scope_name(selection_pos).startswith('text.html.markdown'):
            view.insert(edit, selection_pos, '![pasted-image]({})'.format(self.image_path))
        else:
            view.insert(edit, selection_pos, '{}'.format(self.image_path))

    def save_image(self, data):
        image_dir = self.get_image_abs_directory()

        if not os.path.lexists(image_dir):
            os.makedirs(image_dir)

        abs_path, rel_path = self.get_image_path()

        with open(abs_path, 'wb') as f:
            f.write(data)

            return abs_path, rel_path

        return None, None

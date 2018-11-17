import sublime
import sublime_plugin
import os
import sys
import re
from imp import reload
import datetime

from imagepaste.utils import __osutils__

reload(sys)

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

        return os.path.basename(fullpath)

    def get_current_dir(self):
        return os.path.dirname(self.view.file_name())

    def get_image_directory(self):
        ''' relative path to image directory '''
        subdir_name = self.image_directory

        if not subdir_name:
            subdir_name = self.get_current_filename()

        return  subdir_name

    def get_image_abs_directory(self):
        ''' full path to image directory '''
        return os.path.join(self.get_current_dir(), self.get_image_directory())

    def get_image_path(self):
        abs_directory = self.get_image_abs_directory()
        rel_directory = self.get_image_directory()

        now = datetime.datetime.now()

        filename = '{0:%H}-{0:%M}-{0:%S} {0:%d}-{0:%m}-{0:%y}.png'.format(now)

        abs_path = os.path.join(abs_directory, filename)
        rel_path = os.path.join(rel_directory, filename)

        return abs_path, rel_path

__osutils__.get_clipboard_image

class ImagePasteCommand(ImagePasteBase, sublime_plugin.TextCommand):
    def __init__(self, *args, **kwgs):
        super(ImagePasteCommand, self).__init__(*args, **kwgs)
        self.image_data = None
        self.image_path = ''

    def run(self, edit):
        view = self.view

        image_data = __osutils__.get_clipboard_image()
        if not image_data:
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
            image_path = image_path.replace('\\', '/').replace(' ', '%20')
            self.image_path = image_path
            self.image_data = image_data

        selections = view.sel()

        if not selections:
            return
        # get the cursor
        selection_pos = selections[0].begin()

        if view.scope_name(selection_pos).startswith('text.html.markdown'):
            view.insert(edit, selection_pos, '![]({})'.format(self.image_path))
        else:
            view.insert(edit, selection_pos, '{}'.format(self.image_path))

    def save_image(self, data):
        image_dir = self.get_image_abs_directory()

        if not os.path.lexists(image_dir):
            os.mkdir(image_dir)

        abs_path, rel_path = self.get_image_path()

        with open(abs_path, 'wb') as f:
            f.write(data)

            return abs_path, rel_path

        return None, None

# class ImagePreviewCommand(ImageCommand, sublime_plugin.TextCommand):
#   def __init__(self, *args):
#   #   self.view = view
#       super(ImagePreviewCommand, self).__init__(*args)        
#       # self.phantom_set = sublime.PhantomSet(self.view)
#       self.displayed = False

#   def get_line(self):
#       v = self.view
#       rows, _ = v.rowcol(v.size())
#       for row in range(rows+1):
#           pt = v.text_point(row, 0)
#           tp_line = v.line(pt)
#           line = v.substr(tp_line)
#           yield tp_line, line
#       raise StopIteration

#   def run(self, edit):
#       print("run phantom")
#       view = self.view
#       dirname = os.path.dirname(__file__)
#       for tp, line in self.get_line():
#           m=re.search(r'!\[([^\]]*)\]\(([^)]*)\)', line)
#           if m:
#               name, file1 = m.group(1), m.group(2)
#               message = ""
#               file2 = os.path.join(os.path.dirname(view.file_name()), file1)
#               # print("%s = %s" % (name, file1))
#               region = tp

#               command = ['/usr/bin/python3', os.path.join(dirname, 'bin/imageutil.py'), 'size']
#               command.append(file2)

#               out = self.run_command(" ".join(command))
#               widthstr, heightstr = out.split(',')

#               message = '''<body>
#               <img width="%s" height="%s" src="file://%s"></img>
#               </body>''' % (widthstr, heightstr, file2)
#               if len(name) == 0:
#                   name = file1

#               print("message %s" % message)
#               if not self.displayed:
#                   self.view.add_phantom(name, region, message, sublime.LAYOUT_BLOCK)
#               else:
#                   self.view.erase_phantoms(name)

#       self.displayed = not self.displayed
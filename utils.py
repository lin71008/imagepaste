import os
import sys
import subprocess
import shutil
from io import BytesIO

PLATFORM = sys.platform

PLATFORMS_SUPPORTING_PILLOW = ['win32']

if PLATFORM in PLATFORMS_SUPPORTING_PILLOW:
    # Use the version of Pillow distributed with package
    package_file = os.path.normpath(os.path.abspath(__file__))
    package_path = os.path.dirname(package_file)
    lib_path =  os.path.join(package_path, "lib-{}".format(PLATFORM))

    if not os.path.is_directory(lib_path):
        raise NotImplementedError('Pillow distribution for {!r} is missing'.format(PLATFORM))

    if lib_path not in sys.path:
        sys.path.append(lib_path)

    from PIL import ImageGrab, Image, ImageFile
    ImageFile.LOAD_TRUNCATED_IMAGES = True

class UtilitiesBase(object):
    def __init__(self, executable_location=None, *args, **kwgs):
        self.executable_location = executable_location
        super(UtilitiesBase, self).__init__(*args, **kwgs)

    def get_clipboard_image(self):
        '''
        Grabs screenshot from clipboard
        This function will work differently on linux and windows
        Return: bytes or None
        '''
        raise NotImplementedError("Please Implement this method")

    def handle_errors(self, errs):
        if errs:
            raise Exception(errs)


    def run_command(self, command):
        '''
        Runs command and returns it stdout or None
        '''


        proc = subprocess.Popen(command, shell=False,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env=os.environ)

        try:
            outs, errs = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()

        self.handle_errors(errs)
        return outs

class PillowBasedPaste(UtilitiesBase):
    def get_clipboard_image(self):
        im = ImageGrab.grabclipboard()

        if not im:
            return None

        with BytesIO() as output:
            im.save(output, 'PNG')

            return output.getvalue()

class XclipBasedPaste(UtilitiesBase):
    def get_clipboard_image(self):

        if self.executable_location is None:
            raise Exception('no executable')

        image = self.run_command([self.executable_location, '-se', 'c', '-t', 'image/png', '-o'])

        if not image:
            return None

        return image

class PngpasteBasedPaste(UtilitiesBase):
    def get_clipboard_image(self):

        if self.executable_location is None:
            raise Exception('no executable')


        image = self.run_command([self.executable_location, '-'])

        if not image:
            return None

        return image

    def handle_errors(self, errs):
        if errs:
            if errs == b'pngpaste: No image data found on the clipboard, or could not convert!\n':
                return
            else:
                raise Exception(errs)


def os_appropriate_utils(settings):
    if PLATFORM in PLATFORMS_SUPPORTING_PILLOW:
        return PillowBasedPaste()
    elif PLATFORM == 'linux':
        return XclipBasedPaste(executable_location=settings.get('xclip_executable'))
    elif PLATFORM == 'darwin':
        return PngpasteBasedPaste(executable_location=settings.get('pngpaste_executable'))
    else:
        raise NotImplementedError('Unsupported platform {!r}'.format(PLATFORM))

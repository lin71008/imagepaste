import os
import sys
import subprocess
import shutil
from io import BytesIO

IS_LINUX = sys.platform != 'win32'

if not IS_LINUX:
    package_file = os.path.normpath(os.path.abspath(__file__))
    package_path = os.path.dirname(package_file)
    lib_path =  os.path.join(package_path, "lib")

    if lib_path not in sys.path:
        sys.path.append(lib_path)

    from PIL import ImageGrab
    from PIL import ImageFile
    from PIL import Image

    ImageFile.LOAD_TRUNCATED_IMAGES = True

class UtilitiesBase(object):
    def __init__(self, *args, **kwgs):
        super(UtilitiesBase, self).__init__(*args, **kwgs)

    def get_clipboard_image(self):
        '''
        Grabs screenshot from clipboard
        This function will work differently on linux and windows
        Return: bytes or None
        '''
        raise NotImplementedError("Please Implement this method")

    def get_image_size(self):
        raise NotImplementedError("Please Implement this method")

    def run_command(self, command):
        '''
        Runs command and returns it stdout or None
        '''

        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ)
        
        try:
            outs, errs = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()

        if errs:
            raise Exception(errs)

        return outs

class WinUtils(UtilitiesBase):
    def get_clipboard_image(self):
        im = ImageGrab.grabclipboard()

        if not im:
            return None

        with BytesIO() as output:
            im.save(output, 'PNG')

            return output.getvalue()

    def get_image_size(self, data):
        image = Image.open(BytesIO(data))

        return image.width, image.height

class LinuxUtils(UtilitiesBase):
    def get_clipboard_image(self):
        # TODO: replace xclip with some python library (which i cant find)
        #       or implement own code to grab image from clipboard
        image = self.run_command('xclip -se c -t image/png -o')

        if not image:
            return None

        return image

if IS_LINUX:
    __osutils__ = LinuxUtils()
else:
    __osutils__ = WinUtils()
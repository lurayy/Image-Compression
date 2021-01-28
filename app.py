import pyguetzli
from PIL import Image
import os
import glob
from pathlib import Path
import io
import datetime
import threading
import time


THREAD_LIMIT = 5
LOCATION = '/home/lurayy/mandala/compress/files'

ACTIVE_COMPRESSIONS = 0
COMPLETE_COUNT = 0
TOTAL_COUNT = 0
IMAGES = []
LOG = None

class Compressor(threading.Thread):

    def __init__(self):
        super(Compressor, self).__init__()
        global LOG
        self.log = LOG
        global IMAGES
        self.image = IMAGES.pop()
    
    def run(self):
        try:
            global ACTIVE_COMPRESSIONS
            global COMPLETE_COUNT
            self.log.write(f'Compressing : {self.image}\n')
            ACTIVE_COMPRESSIONS = ACTIVE_COMPRESSIONS + 1 
            im = Image.open(self.image)
            os.remove(self.image)
            im = im.convert('RGB')
            img_byte = io.BytesIO()
            im.save(img_byte, format='JPEG')
            img_byte = img_byte.getvalue()
            optimized_jpeg = pyguetzli.process_jpeg_bytes(img_byte)
            im = Image.open(io.BytesIO(optimized_jpeg))
            im.save(self.image,optimize=True, quality=90)
            cmd = f'python3 src/crunch.py {self.image}'
            os.system(cmd)
            os.remove(self.image)
            ACTIVE_COMPRESSIONS = ACTIVE_COMPRESSIONS - 1
            COMPLETE_COUNT = COMPLETE_COUNT + 1 
        except Exception as exp:
            self.log.write('error on : '+str(self.image)+'  error : '+str(exp)+'\n')

class CompressionSystem():
    def __init__(self, log):
        self.log = log

    def start(self, url):
        global IMAGES
        self.log.write('Finding all images . . . \n')
        IMAGES = set(Path(url).rglob("*.[pP][nN][gG]")).union(set(Path(url).rglob("*.[jJ][pP][gG]")).union(set(Path(url).rglob("*.[jJ][pP][eE][gG]"))))
        self.log.write(f'{len(IMAGES)} images found.\n')
        self.log.write('Starting Compression Process . . .\n')
        TOTAL_COUNT = len(IMAGES)
        self.start_thread()

        images = set(Path(url).rglob("*.[pP][nN][gG]")).union(set(Path(url).rglob("*.[jJ][pP][gG]")).union(set(Path(url).rglob("*.[jJ][pP][eE][gG]"))))
        self.log.write('Compression Complete, Cleaning up . . .\n')
        self.clean_up(images)
        return True
    
    def start_thread(self):
        global IMAGES
        run = True
        while run:
            if self.can_run():
                thread_s = Compressor()
                thread_s.start()
            if len(IMAGES) == 0:
                run = False

    def can_run(self):
        if ACTIVE_COMPRESSIONS < THREAD_LIMIT:
            return True
        else:
            return False

    def clean_up(self, images):
        i = 0
        self.log.write('\n')
        self.log.write('\n')
        self.log.write('Starting Cleaning process\n')
        for image in images:
            self.log.write(f'Total Cleaned : {i} , {float(i/len(images)*100)}Cleaning : {image}\n')
            new_name = (str(image).replace('-crunch', ''))
            os.rename(image, new_name)
            i = i + 1
    
if __name__ == "__main__":
    try:
        LOG = open('logs/'+str(datetime.datetime.now()), 'w')
        compress = CompressionSystem(LOG)
        compress.start(LOCATION)
    except Exception as exp:
        LOG.write(str(exp)+'\n')
    finally:
        LOG.close()
        
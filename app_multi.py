import pyguetzli
from PIL import Image
import os
import glob
from pathlib import Path
import io
import datetime
import threading
import time


THREAD_LIMIT = 10
# LOCATION = '/home/ubuntu/torona/Image-Compression/media'
LOCATION = '/home/lurayy/mandala/compress/temp'
ACTIVE_COMPRESSIONS = 0
COMPLETE_COUNT = 0
TOTAL_COUNT = 0
IMAGES = []
LOG = None
DATE = str(datetime.datetime.now())


def log(msg):
    with open('logs/'+str(DATE), 'a+') as f:
        f.write(msg + '\n')

class Compressor(threading.Thread):

    def __init__(self):
        super(Compressor, self).__init__()
        global IMAGES
        self.image = IMAGES.pop()
    
    def run(self):
        im = None
        try:
            global ACTIVE_COMPRESSIONS
            global COMPLETE_COUNT
            print('Compressing : ',self.image)
            log(f'Compressing : {self.image}\n')
            ACTIVE_COMPRESSIONS = ACTIVE_COMPRESSIONS + 1 
            im = Image.open(self.image)
            im = im.convert('RGB')
            img_byte = io.BytesIO()
            im.save(img_byte, format='JPEG')
            img_byte = img_byte.getvalue()
            log('Using pyguetzli : ', self.image)
            optimized_jpeg = pyguetzli.process_jpeg_bytes(img_byte)
            im = Image.open(io.BytesIO(optimized_jpeg))
            im.save(self.image,optimize=True, quality=90)
            ext = str(self.image).split('.')
            ext = ext[len(ext)-1]
            if str(ext).lower() == "png":
                log('Using crnch : ',self.image )
                cmd = f'python3 src/crunch.py {self.image}'
                os.system(cmd)
                os.remove(self.image)
            ACTIVE_COMPRESSIONS = ACTIVE_COMPRESSIONS - 1
            COMPLETE_COUNT = COMPLETE_COUNT + 1
        except Exception as exp:
            if im:
                im.save(self.image,optimize=True, quality=100)
            ACTIVE_COMPRESSIONS = ACTIVE_COMPRESSIONS - 1
            log('error on : '+str(self.image)+'  error : '+str(exp)+'\n')

class CompressionSystem():

    def start(self, url):
        global IMAGES
        log('Finding all images . . . \n')
        IMAGES = set(Path(url).rglob("*.[pP][nN][gG]")).union(set(Path(url).rglob("*.[jJ][pP][gG]")).union(set(Path(url).rglob("*.[jJ][pP][eE][gG]"))))
        log(f'{len(IMAGES)} images found.\n')
        log('Starting Compression Process . . .\n')
        TOTAL_COUNT = len(IMAGES)
        self.start_thread()

        images = set(Path(url).rglob("*.[pP][nN][gG]")).union(set(Path(url).rglob("*.[jJ][pP][gG]")).union(set(Path(url).rglob("*.[jJ][pP][eE][gG]"))))
        log('Compression Complete, Cleaning up . . .\n')
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
                if ACTIVE_COMPRESSIONS == 0:
                    run = False

    def can_run(self):
        if ACTIVE_COMPRESSIONS < THREAD_LIMIT:
            return True
        else:
            return False

    def clean_up(self, images):
        i = 0
        log('Starting Cleaning process\n')
        for image in images:
            log(f'Total Cleaned : {i} , {float(i/len(images)*100)}Cleaning : {image}\n')
            new_name = (str(image).replace('-crunch', ''))
            os.rename(image, new_name)
            i = i + 1
        print('clean up complete')
    
if __name__ == "__main__":
    try:
        compress = CompressionSystem()
        compress.start(LOCATION)
    except Exception as exp:
        log(str(exp)+'\n')



import pyguetzli
from PIL import Image
import os
import glob
from pathlib import Path
import io
import datetime
import threading
import time


THREAD_LIMIT = 2
# LOCATION = '/home/ubuntu/torona/Image-Compression/media'
LOCATION = '/home/lurayy/mandala/compress/temp'
ACTIVE_COMPRESSIONS = 0
COMPLETE_COUNT = 0
TOTAL_COUNT = 0
IMAGES = []
LOG = None
DATE = str(datetime.datetime.now())


def log(msg):
    with open('logs/'+str(DATE)+'/main.log', 'a+') as f:
        f.write(msg + '\n')


def error_log(msg):
    with open('logs/'+str(DATE)+'/error.log', 'a+') as f:
        f.write(msg + '\n')

class Compressor(threading.Thread):

    def __init__(self):
        super(Compressor, self).__init__()
        global IMAGES
        self.image = IMAGES.pop()
    
    def run(self):
        global COMPLETE_COUNT
        global TOTAL_COUNT
        im = None
        try:
            global ACTIVE_COMPRESSIONS
            log(f'Compressing : {self.image}')
            ACTIVE_COMPRESSIONS = ACTIVE_COMPRESSIONS + 1 
            im = Image.open(self.image)
            im = im.convert('RGB')
            img_byte = io.BytesIO()
            im.save(img_byte, format='JPEG')
            img_byte = img_byte.getvalue()
            optimized_jpeg = pyguetzli.process_jpeg_bytes(img_byte)
            im = Image.open(io.BytesIO(optimized_jpeg))
            im.save(self.image,optimize=True, quality=90)
            ext = str(self.image).split('.')
            ext = ext[len(ext)-1]
            if str(ext).lower() == "png":
                log(f'Using crnch : {self.image}' )
                cmd = f'python3 src/crunch.py {self.image}'
                os.system(cmd)
                os.remove(self.image)
            ACTIVE_COMPRESSIONS = ACTIVE_COMPRESSIONS - 1
            COMPLETE_COUNT = COMPLETE_COUNT + 1
            log(f'Compression Complete : {self.image}')
            log(f'--------------  {COMPLETE_COUNT/TOTAL_COUNT*100 } % -------------------')
        except Exception as exp:
            if im:
                im.save(self.image,optimize=True, quality=100)
            ACTIVE_COMPRESSIONS = ACTIVE_COMPRESSIONS - 1
            error_log('error on : '+str(self.image)+'  error : '+str(exp)+'')

class CompressionSystem():

    def start(self, url):
        global IMAGES
        global TOTAL_COUNT
        log('Finding all images . . . ')
        IMAGES = set(Path(url).rglob("*.[pP][nN][gG]")).union(set(Path(url).rglob("*.[jJ][pP][gG]")).union(set(Path(url).rglob("*.[jJ][pP][eE][gG]"))))
        log(f'{len(IMAGES)} images found.')
        log('Starting Compression Process . . .')
        TOTAL_COUNT = len(IMAGES)
        self.start_thread()

        images = set(Path(url).rglob("*.[pP][nN][gG]")).union(set(Path(url).rglob("*.[jJ][pP][gG]")).union(set(Path(url).rglob("*.[jJ][pP][eE][gG]"))))
        log('Compression Complete, Cleaning up . . .')
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
        log('Starting Cleaning process')
        for image in images:
            log(f'Total Cleaned : {i} , {float(i/len(images)*100)}Cleaning : {image}\n')
            new_name = (str(image).replace('-crunch', ''))
            os.rename(image, new_name)
            i = i + 1
        print('clean up complete')
    
if __name__ == "__main__":
    os.mkdir('logs/'+str(DATE))
    try:
        compress = CompressionSystem()
        compress.start(LOCATION)
    except Exception as exp:
        error_log(str(exp)+'\n')



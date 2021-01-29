import pyguetzli
from PIL import Image
import os
import glob
from pathlib import Path
import io
import datetime
import threading
import time

DATE = datetime.datetime.now()

def log(msg):
    with open('logs/log_'+str(DATE), 'a+') as f:
        f.write(msg + '\n')

def error_log(msg):
    with open('logs/error_'+str(DATE), 'a+') as f:
        f.write(msg + '\n')

# LOCATION = '/home/ubuntu/torona/Image-Compression/media'
LOCATION = '/home/lurayy/mandala/compress/temp'

IMAGES = []
LOG = None

class CompressionSystem():

    def start(self, url):
        global IMAGES
        log('Finding all images . . . \n')
        IMAGES = set(Path(url).rglob("*.[pP][nN][gG]")).union(set(Path(url).rglob("*.[jJ][pP][gG]")).union(set(Path(url).rglob("*.[jJ][pP][eE][gG]"))))
        log(f'{len(IMAGES)} images found.\n')
        log('Starting Compression Process . . .\n')
        self.start_thread()

        images = set(Path(url).rglob("*.[pP][nN][gG]")).union(set(Path(url).rglob("*.[jJ][pP][gG]")).union(set(Path(url).rglob("*.[jJ][pP][eE][gG]"))))
        log('Compression Complete, Cleaning up . . .\n')
        self.clean_up(images)
        return True
    
    def start_thread(self):
        global IMAGES
        run = True
        i = 0
        for image in IMAGES:
            print(f'{i/len(IMAGES)*100} % Done\n')
            log(f'{i/len(IMAGES)*100} % Done\n')
            self.compress(image)
            i = i + 1

    def compress(self, image):
        im = None
        try:
            log(f'Compressing : {image}\n')
            print(f'Compressing : {image}\n')
            im = Image.open(image)
            os.remove(image)
            im = im.convert('RGB')
            img_byte = io.BytesIO()
            im.save(img_byte, format='JPEG')
            img_byte = img_byte.getvalue()
            optimized_jpeg = pyguetzli.process_jpeg_bytes(img_byte)
            im = Image.open(io.BytesIO(optimized_jpeg))
            im.save(image,optimize=True, quality=90)
            ext = str(image).split('.')
            ext = ext[len(ext)-1]
            if str(ext).lower() == "png":
                cmd = f'python3 src/crunch.py {image}'
                os.system(cmd)
                os.remove(image)
            log(f'Compression Successful {image}')
        except Exception as exp:
            if im:
                im.save(image,optimize=True, quality=100)
            error_log('error on : '+str(image)+'  error : '+str(exp)+'\n')

    def clean_up(self, images):
        i = 0
        log('\n')
        log('\n')
        log('Starting Cleaning process\n')
        for image in images:
            log(f'Total Cleaned : {i} , {float(i/len(images)*100)}Cleaning : {image}\n')
            new_name = (str(image).replace('-crunch', ''))
            os.rename(image, new_name)
            i = i + 1
    
if __name__ == "__main__":
    try:
        compress = CompressionSystem()
        compress.start(LOCATION)
    except Exception as exp:
        error_log(str(exp)+'\n')
from math import log, trunc, ceil
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS
import os
from os import walk
from os.path import abspath
from io import BytesIO

def get_filenames(dir):
    return [abspath(f) for f in next(walk(dir))[2]]

def get_metadata(filename):
    try:
        with Image.open(filename) as f:
            metadata = f.getexif()
            return {TAGS.get(k,k):v for k,v in metadata.items() }
    except UnidentifiedImageError:
        return None
    except FileNotFoundError:
        return None

def create_new_name(metadata, tags, sep):
    return sep.join(list([metadata.get(t, '_') for t in tags]))

def process_files(files):
    d = dict()
    for f in files:
        new_name = get_new_image_name(f)
        if new_name in d:
            d[new_name].append(os.path.abspath(f))
        else:
            d[new_name] = [os.path.abspath(f)]
    d.pop(None, None)
    if d:
        for k, value in d.items():
            print(k, value)
            n = len(value)
            if n == 1:
                ext = value[0][-3:]
                os.rename(value[0], f'{k}.{ext}')
            else:
                dig_amount = trunc(log(n, 10))
                for i, v in enumerate(value, 1):
                     ext = v[-3:]
                     zeroes = '0'*(dig_amount - trunc(log(i, 10)))
                     os.rename(v, f'{k}-{zeroes}{i}.{ext}')

def get_new_image_name(filename):
    try:
        im = Image.open(filename)
        exif_raw = im.getexif()
        tags = (271, 272, 306)
        exif_info = [exif_raw.get(el, None) for el in tags]
        if exif_info[2]:
            exif_info[2] = exif_info[2].replace(':', '').replace(' ', '_')
        str_info = (el if el else '_' for el in exif_info)
        new_name = '_'.join(str_info)
        if new_name == '_____':
            return None
        else:
            return new_name
    except UnidentifiedImageError:
        return None
    except FileNotFoundError:
        return None

def find_null_byte(s):
    return s.encode('utf_8').find(b'\x00')

def get_exif_info(filename):
    try:
        im = Image.open(filename)
        exif_raw = im.getexif()
        for k,v in exif_raw.items():
            print(f'{k}\t{v}')
        tags = (271, 272, 306)
        mcd_raw = (list(exif_raw.get(t) for t in tags))
        mcd = [el[:find_null_byte(el)] if find_null_byte(el) != -1 else el for el in mcd_raw] 
#       mcd = [el.split(b'\x00')[0] for el in mcd_raw]
        s = '_'.join(mcd)
#       s = '_'.join(list(exif_raw.get(t) for t in tags))
        print(s)
        print(s.encode('utf_8').split(b'\x00'))
    except UnidentifiedImageError:
        return None
    except FileNotFoundError:
        return None



if __name__ == '__main__':
    target_dir='.'
    print(f'Processing directory <{os.path.abspath(target_dir)}>')
#   process_files(next(os.walk(target_dir))[2])
#   get_exif_info('GOPR0201.JPG')
    files = get_filenames(target_dir)
    tags = ['Make', 'Model', 'DateTime']
    for f in files:
        metadata = get_metadata(f)
        if metadata:
            print(f, ' - ', create_new_name(metadata, tags, '_'))

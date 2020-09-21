import piexif
import os
import pytesseract
from PIL import Image, ImageFilter
import stat
import re
import glob


def split(list_of_strings, split_on_num):
    out = []
    for element in list_of_strings:
        while len(element) > split_on_num:
            out.append(element[:split_on_num])
            element = element[split_on_num:]
        if len(element) > 0:
            out.append(element)
    return out


def trim_list(list_of_strings, max_length):
    out = []
    for i in list_of_strings:
        if len(i) > max_length:
            i = i[:(len(i) // max_length) * max_length]
        out.append(i)
    return out


# setting Path
pytesseract.pytesseract.tesseract_cmd = r'D:\Coding\ImgPy\Tesseract\tesseract.exe'

# user variables
folder_path = r""
blur = False
grayscale = False
text_to_find = ''

os.chdir(folder_path)
file_list = glob.glob('*.jpg')
for image_path in file_list:
    print(image_path)
    exif_dict = piexif.load(image_path)
    comment_asci = []
    img = Image.open(image_path)
    if grayscale:
        img = img.convert("L")
    if blur:
        img = img.filter(ImageFilter.GaussianBlur(radius=1))
    os.chmod(image_path, stat.S_IWRITE)
    img.save(image_path)
    # ocr
    ocr_text = pytesseract.image_to_string(Image.open(image_path), lang='eng', config="-c tessedit_char_whitelist"
                                                                                      "=NO.no1234567890()")
    # process text given by ocr
    ocr_text = ocr_text.lower()
    ocr_text = ocr_text[:-1]
    ocr_text = ocr_text.replace(" ", "")
    ocr_text = ocr_text.strip()
    ocr_text = ocr_text.splitlines()
    comment = ''
    # iterate through lines
    for line in ocr_text:
        # check if text_to_find is in the line
        if text_to_find in line:
            index = line.index(text_to_find[0])
            line = re.sub(r'\([^)]*\)', '', line)
            line = line[index:]
            comment += line + "\n"
    comment = re.sub('[()a-zA-Z.]', '', comment)
    comment = comment.strip()
    comment = comment.splitlines()
    comment = split(comment, 6)
    comment = trim_list(comment, 6)
    comment = "\n".join(comment)
    print(comment)
    # convert into ascii
    for char in comment:
        ascii_char = ord(char)
        comment_asci.append(ascii_char)
        comment_asci.append(0)
    comment_asci.append(0)
    comment_asci.append(0)
    comment_asci = tuple(comment_asci)
    # set it as property in file
    exif_dict['0th'][piexif.ImageIFD.XPComment] = comment_asci
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, image_path)

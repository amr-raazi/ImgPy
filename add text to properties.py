import piexif
import os
import pytesseract
from PIL import Image, ImageFilter
import stat
import re

# setting Path
pytesseract.pytesseract.tesseract_cmd = r'D:\Coding\ImgPy\Tesseract\tesseract.exe'

# user variables
folder_path = r"D:\Coding\ImgPy\photos"
blur = False
grayscale = False
text_to_find = ''
file_list = os.listdir(folder_path)
os.chdir(folder_path)
for image_path in file_list:
    # store exif data
    exif_dict = piexif.load(image_path)
    comment_asci = []
    # open and process file for ocr
    img = Image.open(image_path)
    if grayscale:
        img = img.convert("L")
    if blur:
        img = img.filter(ImageFilter.GaussianBlur(radius=1))
    os.chmod(image_path, stat.S_IWRITE)
    img.save(image_path)
    # ocr
    ocr_text = pytesseract.image_to_string(Image.open(image_path), lang='eng', config="-c tessedit_char_whitelist"
                                                                                      "=ITEMNO.itemno.1234567890")
    # process text given by ocr
    # remove last bad char
    ocr_text = ocr_text[:-1]
    # remove spaces
    ocr_text = ocr_text.replace(" ", "")
    # strip leading and trailing blanks
    ocr_text = ocr_text.strip()
    # split lines into list
    ocr_text = ocr_text.splitlines()
    comment = ''
    # iterate through lines
    for line in ocr_text:
        # check if text_to_find is in the line
        if text_to_find in line:
            # add from text_to_find's first letter
            index = line.index(text_to_find[0])
            line = line[index:]
            # add line from text_to_find's first letter in line
            comment += line + ","
    # remove some chars using regex
    comment = re.sub('[a-zA-Z .]', '', comment)
    print(comment)
    # convert into ascii
    for i in comment:
        asci = ord(i)
        comment_asci.append(asci)
        comment_asci.append(0)
    comment_asci.append(0)
    comment_asci.append(0)
    # convert into tuple
    comment_asci = tuple(comment_asci)
    # set it as property in file
    exif_dict['0th'][piexif.ImageIFD.XPKeywords] = comment_asci
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, image_path)

import cmd
from email.mime import image
from importlib.resources import path
from re import T
import pdf2image
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import io
import os
import shutil
import re
#from hunspell import Hunspell
#spellChecker = Hunspell('ar', hunspell_data_dir='.' + os.path.sep+ 'hunspell-ar_3.1' + os.path.sep)

def pdf_to_txt(pdf_file):
    pathDir,pathName = os.path.split(pdf_file)
    pathName = pathName + "_ext"
    extFullPath = pathDir + os.path.sep + pathName
    print(extFullPath)
 
    if(os.path.exists(extFullPath)):
        shutil.rmtree(extFullPath)
    
    if(not os.path.exists(extFullPath)):
        os.mkdir(extFullPath)
    
    '''
    with io.open(pdf_file,'rb') as myFile:
        btArr = myFile.read()
    images = pdf2image.convert_from_bytes(btArr)#,output_folder=extFullPath)
    '''
    print('getting pdf info ')
    infoFile = pdf2image.pdfinfo_from_path(pdf_file)
    
    print(infoFile)
    #lastPage = (3 if int(infoFile["Pages"]) > 3 else infoFile["Pages"] )
    #images = pdf2image.convert_from_path(pdf_file,last_page=lastPage)#,output_folder=extFullPath)
    print('start converting pdf to images in ',extFullPath + os.path.sep)
    cmdLine = 'pdftoppm '
    #cmdLine = cmdLine + '-l ' + str(lastPage) + ' '
    cmdLine = cmdLine  +'"' +pdf_file+'"' + ' '
    cmdLine = cmdLine  + '"' + extFullPath + os.path.sep + '"'


    stream = os.popen(cmdLine)
    output = stream.read()
    if "error" in output.lower():
        raise Exception(output)
    
    imageNames =  os.listdir(extFullPath)
    imageNames.sort()
    
    indx = 1

    out_str = '<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8" /></head><body>'

    for strImage in imageNames:
        if(".ppm" in strImage.lower()):
            #start extract ocr
            print('extracting page no ',str(indx),' from ',str(infoFile["Pages"]))
            fName = extFullPath + os.path.sep + strImage
            
            img = Image.open(fName,'r')
            extracted = ocr_core(img)
            if(re.sub('[ \n\r\t]+','',extracted) != ''):
                extracted = re.sub('[ \t]+',' ',extracted)
                extracted = re.sub('[\r]+','',extracted)
                extracted = re.sub('[\n]+','\n',extracted)
                out_str = out_str + extracted + '\n'
            indx+=1

    out_str = re.sub('[\n]+','<br />',out_str)        
    out_str = out_str + '</body></html>'
    with io.open(pdf_file + '.html','w') as outFile :
        outFile.write(out_str)
    if(os.path.exists(extFullPath)):
        shutil.rmtree(extFullPath)
    return


def pdf_to_img(pdf_file):
    
    pathDir,pathName = os.path.split(pdf_file)
    pathName = pathName + "_ext"
    extFullPath = pathDir + os.path.sep + pathName
    print(extFullPath)
 
    if(os.path.exists(extFullPath)):
        shutil.rmtree(extFullPath)
    
    if(not os.path.exists(extFullPath)):
        os.mkdir(extFullPath)
    
    '''
    with io.open(pdf_file,'rb') as myFile:
        btArr = myFile.read()
    images = pdf2image.convert_from_bytes(btArr)#,output_folder=extFullPath)
    '''
    infoFile = pdf2image.pdfinfo_from_path(pdf_file)
    
    print(infoFile)
    #lastPage = (3 if int(infoFile["Pages"]) > 3 else infoFile["Pages"] )
    #images = pdf2image.convert_from_path(pdf_file,last_page=lastPage)#,output_folder=extFullPath)
    
    cmdLine = 'pdftoppm '
    #cmdLine = cmdLine + '-l ' + str(lastPage) + ' '
    cmdLine = cmdLine  +'"' +pdf_file+'"' + ' '
    cmdLine = cmdLine  + '"' + extFullPath + os.path.sep + '"'


    stream = os.popen(cmdLine)
    output = stream.read()
    if "error" in output.lower():
        raise Exception(output)
    
    imageNames =  os.listdir(extFullPath)
    imageNames.sort()
    images = []
    for strImage in imageNames:
        if(".ppm" in strImage.lower()):
            fName = extFullPath + os.path.sep + strImage
            
            images.append(Image.open(fName,'r'))
            

    if(os.path.exists(extFullPath)):
        shutil.rmtree(extFullPath)
    return images


def ocr_core(file):
    text = pytesseract.image_to_string(file,lang="ara")#,config="--oem 1")
    return text


def print_pages(pdf_file):
    pdf_to_txt(pdf_file)
    '''
    images = pdf_to_img(pdf_file)
    out_str = '<!DOCTYPE html><html lang="en" dir="rtl"><head><meta charset="utf-8" /></head><body>'
    for pg, img in enumerate(images):
        
        out_str = out_str + ocr_core(img).replace('\n','<br />') + '<br />' 
    
    out_str = out_str + '</body></html>'
    with io.open(pdf_file + '.html','w') as outFile :
        outFile.write(out_str)
    '''


print_pages('<path to pdf>')
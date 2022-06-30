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
import argparse


from hunspell import Hunspell


def pdf_to_txt(pdf_file,allowSpell):
    spellChecker = None
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
            if allowSpell:
                if spellChecker is None :
                    spellChecker = Hunspell('ar', hunspell_data_dir='.' + os.path.sep+ 'hunspell-ar_3.1' + os.path.sep)
                print ('start spell check : ')
                words = re.split('[ \n\r\t]+',extracted)
                for word in words:
                    if (re.sub('[ \n\r\t]+','',word) != ''):
                        #found word
                        tes = spellChecker.spell(word)
                        if not tes:
                            suggessions = spellChecker.suggest(word)
                            print ('found wrong spelling : ' , word , suggessions)
                
                
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





def ocr_core(file):
    text = pytesseract.image_to_string(file,lang="ara")#,config="--oem 1")
    return text


def print_pages(pdf_file,allowSpell):
    pdf_to_txt(pdf_file,allowSpell)
    


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Take filename and is apply hanspell or not.')
    parser.add_argument('--filename',   required = True,
                    help='full path of the pdf file')
    parser.add_argument('--allowSpell',default=False,type=bool,
                    required=False,
                    help='run spell check on result text')

    args = parser.parse_args()
    print_pages(args.filename,args.allowSpell)



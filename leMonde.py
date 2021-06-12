import random
import re
from urllib.request import urlopen
import os
import time

from ebooklib import epub

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#%%
def getTextIfExists(parent,className):
    elemL = parent.find_elements_by_class_name(className)
    if not not elemL:
        string = elemL[0].get_attribute("innerHTML")
    else:
        string = ''
    return string

def cleanString(string):
    string = string.replace('&nbsp;',' ')

    cleanIt =  re.compile('<span class="italic">(.*?)</span>')
    string = re.sub(cleanIt,r'<i>\1</i>',string)

    cleanSpan =  re.compile('<span .*?>(.*?)</span>')
    string = re.sub(cleanSpan,r'\1',string)

    cleanDiv = re.compile('<div .*?>(.*?)</div>')
    string = re.sub(cleanDiv,r'\1',string)

    cleanLieu = re.compile('<lieu .*?>(.*?)</lieu>')
    string = re.sub(cleanLieu,r'<p><b>\1</b></p>',string)

    cleanh2 = re.compile('<h2(.*)?>(.*?)</h2>')
    string = re.sub(cleanh2,r'<h3>\2</h3>',string)

    cleanr = re.compile('<renvoipage(.*)?>.*?</renvoipage>')
    string = re.sub(cleanr, '', string)

    cleanr = re.compile('<content(.*)?>(.*?)</content>')
    string = re.sub(cleanr, r'\2', string)
    cleanr = re.compile('<surtitre-texte>(.*)?>(.*?)</surtitre-texte>')
    string = re.sub(cleanr, r'\2', string)

    cleanids = re.compile('id=\".{1,20}\"')
    string = re.sub(cleanids,r'',string)

    return string

def getImageIfExists(parent):
    legString = ''
    src = ''
    child1  = parent.find_elements_by_class_name("alb-image-slider-container")
    if not not child1:
        img = child1[0].find_element_by_tag_name("img")
        src = img.get_attribute("src")
        # urllib.request.urlretrieve(src, folder+"img{}.jpg".format(imgID))
        legend = child1[0].find_elements_by_class_name("alb-slide-image-capture")
        if not not legend:
            legString = legend[0].get_attribute("innerHTML")
    return src, legString

def loadParamDico(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        txt = file.read()
        file.close()
    lines = txt.split('\n')
    dico = {}
    for stri in lines:
        if stri[:1]=='#' or not stri.strip():
            pass
        else:
            a=stri.split(':',1)
            dico[a[0][:-1]] = a[1][1:]
    return dico

def writeDico(dico,filename):
    txt = "# Calibre installation folder:\n"+\
          "calibreFolder : {}\n\n".format(dico['calibreFolder'])+\
          "# Identifiant Le Monde\n"+\
          "email : {}\n\n".format(dico['email'])+\
          "# Server email\n"+\
          "smtp : {}\n".format(dico['smtp'])+\
          "port : {}\n".format(dico['port'])+\
          "senderEmail : {}\n".format(dico['senderEmail'])+\
          "recieverEmail : {}\n\n".format(dico['recieverEmail'])+\
          "# Mot de passe: laisser vide la premiere fois\n"+\
          "#   LE MONDE\n"+\
          "mdp : {}\n".format(dico['mdp'])+\
          "#   SMTP\n"+\
          "mdpSMTP : {}\n".format(dico['mdpSMTP'])
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(txt)
        file.close()
    return

def encode(key, string):
    encoded_chars = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr(ord(string[i]) + ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = ''.join(encoded_chars)
    return encoded_string

def decode(key, string):
    encoded_chars = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr((ord(string[i]) - ord(key_c) + 256) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = ''.join(encoded_chars)
    return encoded_string

def main():
    paramPERSO = loadParamDico('PARAMETRES.txt')
    key = 'ewffew987498thtyfbgnzarew'
    write = False
    if ('mdp' not in paramPERSO) or (not paramPERSO['mdp']):
        paramPERSO['mdp'] = encode(key,input('Entrer votre mot de passe le Monde : '))
        write = True
    if ('mdpSMTP' not in paramPERSO) or (not paramPERSO['mdpSMTP']):
        paramPERSO['mdpSMTP'] = encode(key,input('Entrer votre mot de passe SMTP : '))
        write = True
    if write:
        writeDico(paramPERSO,'PARAMETRES.txt')

    path = r'Driver/geckodriver'
    driver = webdriver.Firefox(executable_path = path)

    driver.get('https://journal.lemonde.fr/')
    time.sleep(4+0.5*random.random())
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'main-image-wrapper')))
    elem = driver.find_element_by_class_name("main-label")
    date = elem.get_attribute("innerHTML")

    mainTitle = "Le Monde du "+date

    EditionName = mainTitle.replace(' ','_')

    if not os.path.exists("LeMonde/"+EditionName+".epub"):
        overViewImage  = driver.find_element_by_class_name("main-image-wrapper")
        img = overViewImage.find_element_by_tag_name("img")
        srcCover = img.get_attribute("src")

        elem = driver.find_element_by_class_name("main-button-wrapper")
        elem.click()

        time.sleep(5+0.5*random.random())

        elemL = driver.find_elements_by_id("connection_mail")
        if not not elemL:
            elemL[0].send_keys(paramPERSO['email'])

            elem = driver.find_element_by_id("connection_password")
            elem.send_keys(decode(key, paramPERSO['mdp']))

            elem = driver.find_elements_by_tag_name('label')
            for e in elem:
                if e.get_attribute('for') == 'connection_stay_connected':
                    e.click()

            elem = driver.find_element_by_id("connection_save")
            elem.click()

        time.sleep(3+0.5*random.random())
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'swiper-slide-page-click')))

        elem = driver.find_element_by_class_name("swiper-slide-page-click-container")
        el = elem.find_element_by_class_name("swiper-slide-page-click")
        el.click()

        time.sleep(2+0.5*random.random())
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'alb-nav-previous')))

        elem = driver.find_element_by_class_name("alb-nav-previous")
        getBack = True
        while getBack:
            if 'inactive' in elem.get_attribute('class'):
                getBack = False
            else:
                elem.click()
                time.sleep(0.5+0.5*random.random())
                elem = driver.find_element_by_class_name("alb-nav-previous")

        book = epub.EpubBook()
        book.set_identifier(time.strftime('%Y%m%d'))
        book.set_title(mainTitle)
        book.set_language('fr')
        book.add_author('Le Monde')

        book.set_cover("cover.jpg", urlopen(srcCover).read())

        bookItems = []

        elem = driver.find_element_by_class_name("alb-nav-next")
        getForward = True
        numId = 0
        imgID = 0
        while getForward:
            if 'inactive' in elem.get_attribute('class'):
                getForward = False
            else:
                parent = driver.find_element_by_css_selector("div[class='swiper-slide alb-slide swiper-slide-active']")
                title   = getTextIfExists(parent,"alb-article-title")
                authors = getTextIfExists(parent,"alb-article-author")
                intro   = getTextIfExists(parent,"alb-article-introduction")
                content = getTextIfExists(parent,"alb-article-content")

                src,legString = getImageIfExists(parent)
                if not not src:
                    image = '<img src=\"img{}.jpg\" alt=\"image\">'.format(imgID) + \
                            '<p><i>'+cleanString(legString)+'</i></p>'
                else:
                    image = ''

                titleCleaned = cleanString(title)
                cleanp = re.compile('<p(.*)?>(.*?)</p>')
                titleCleaned = re.sub(cleanp,r'\2',titleCleaned)

                bookItems.append(epub.EpubHtml(title=titleCleaned, file_name='Article{}.xhtml'.format(numId), lang='fr'))
                bookItems[-1].content = '<h1>'+titleCleaned+'</h1>'+cleanString(authors)+image+cleanString(intro)+cleanString(content)
                if not not image:
                    ei = epub.EpubImage()
                    ei.file_name = "img{}.jpg".format(imgID)
                    ei.media_type = 'image/jpeg'
                    b = bytearray(urlopen(src).read())
                    ei.content = b
                    book.add_item(ei)
                    imgID+=1

                numId += 1

                elem.click()
                time.sleep(0.5+0.5*random.random())
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'alb-nav-next')))
                elem = driver.find_element_by_class_name("alb-nav-next")

        for c in bookItems:
            book.add_item(c)

        book.toc = bookItems
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        book.spine = ['nav']+bookItems
        epub.write_epub("LeMonde/"+EditionName+".epub", book)
    else:
        print("Une version 'epub' du monde d'aujourd'hui existe déjà: {}".format(EditionName))
    driver.quit()

    if not os.path.exists("LeMonde/"+EditionName+".mobi"):
        print("Conversion du fichier {}.epub en fichier mobi".format(EditionName))
        os.system('"{0}/ebook-convert.exe" {1}/{2}.epub {1}/{2}.mobi'.format(paramPERSO['calibreFolder'],os.getcwd().replace('\\','/'),"LeMonde/"+EditionName))
        time.sleep(4)
    else:
        print("Une version 'mobi' du monde d'aujourd'hui existe déjà: {}".format(EditionName))

    message = MIMEMultipart()
    message["From"] = paramPERSO['senderEmail']
    message["To"] = paramPERSO['recieverEmail']
    message["Subject"] = "Convert"

    message.attach(MIMEText("", "plain"))
    filename = "LeMonde/"+EditionName+".mobi"

    with open(filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename=\"'+EditionName+'.mobi\"') # the filename cannot be too long
    message.attach(part)
    text = message.as_string()

    # Create a secure SSL context
    context = ssl.create_default_context()
    print("Envoi de l'email...")
    with smtplib.SMTP_SSL(paramPERSO['smtp'], paramPERSO['port'], context=context) as server:
        server.login(paramPERSO['senderEmail'], decode(key, paramPERSO['mdpSMTP']))
        server.sendmail(paramPERSO['senderEmail'], paramPERSO['recieverEmail'], text)
    time.sleep(10)
    return

# pyinstaller --onefile leMonde.py
if __name__ == "__main__":
    main()
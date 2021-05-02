import requests
from bs4 import BeautifulSoup
import urllib.parse as urlparse
from urllib.parse import parse_qs
from PyPDF2 import PdfFileMerger
import os
import time


def getpagehtml(url): # get page html
    html = requests.get(url)
    soup = BeautifulSoup(html.text, "html.parser")
    return soup


def get_pdf(url, filename): # get and save pdf
    r = requests.get(url, allow_redirects=True)
    open(filename+".pdf", "wb").write(r.content)
    if os.stat(filename+".pdf").st_size < 10000:
        os.remove(filename+".pdf")
        r = requests.get(url, allow_redirects=True)
        open(filename+".pdf", "wb").write(r.content)



def fullview_check(pagehtml): # check if fullview is available
    if pagehtml.find_all("div", {"class": "alert alert-info alert-block"}) == []:
        if pagehtml.find_all("a", {"class": "page-pdf-link"}):
            # print("Full View is available.")
            return True
        else:
            # print("PDF is not found.")
            return False
    else:
        # print("Full View is not available.")
        return False


        def npages(pagehtml): # count item's number of pages
            npages = int(pagehtml.find("span", {"data-slot": "total-seq"}).get_text())
            return npages


        def save_and_merge(item_url):
            # get html of item page
            pagehtml = getpagehtml(item_url)
            # if fullview is available, download and merge all pages
            if fullview_check(pagehtml):
                npages = npages(pagehtml)
                # get item id
                    id = pagehtml.find("a", {"class": "page-pdf-link"})["href"]
                    parsed = urlparse.urlparse(id)
                    id = parse_qs(parsed.query)['id'][0]
                    print("Item ID: "+id)
                    # create empty list of pages that will be merged
                    pages = []
                    # save every page as pdf
                    for i in range(1, npages+1):
                        time.sleep(1)
                        get_pdf("https://babel.hathitrust.org/cgi/imgsrv/download/pdf?id="+id+";orient=0;size=100;seq="+str(i)+";attachment=0", "page"+str(i))
                              # filter broken files by size
                              size = os.stat("page"+str(i)+".pdf").st_size
                              # if less than 10000 bytes, then supposedly broken
                              while size < 10000:
                                  print("Size of file is less than 10000 bytes, so it must be broken, repeating.")
                                  os.remove("page"+str(i)+".pdf")
                                  get_pdf("https://babel.hathitrust.org/cgi/imgsrv/download/pdf?id="+id+";orient=0;size=100;seq="+str(i)+";attachment=0", "page"+str(i))
                                  size = os.stat("page"+str(i)+".pdf").st_size
                                  time.sleep(1)
                              # append filename of the page to the list
                              pages.append("page"+str(i)+".pdf")
                              print(str(i)+"/"+str(npages)+" pages downloaded.", end="\r", flush=True)
                                # merge files into one pdf
                                print("Merging pages into one file.")
                                merger = PdfFileMerger()
                                for pdf in pages:
                                    merger.append(pdf)
                                merger.write(id+".pdf")
                                merger.close()
                                print("File "+id+".pdf "+"is done.")
                                for page in pages:
                                    os.remove(page)
                            else:
                                  print("Full View is not available.")


if __name__ == '__main__':
    url = input("Item URL: ")
    save_and_merge(url)

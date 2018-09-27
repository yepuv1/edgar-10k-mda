from __future__ import print_function
import argparse
import codecs
import csv
from glob import glob
import os
import re
import sys
import unicodedata

from bs4 import BeautifulSoup
from pathos.pools import ProcessPool
from pathos.helpers import cpu_count
import requests

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

SEC_GOV_URL = 'https://www.sec.gov/Archives'

class Form10k(object):
    def __init__(self):
        pass

    def _process_text(self, text):
        """
            Preprocess Text
        """
        text = unicodedata.normalize("NFKD", text) # Normalize
        text = '\n'.join(text.splitlines()) # Let python take care of unicode break lines

        # Convert to upper
        text = text.upper() # Convert to upper

        # Take care of breaklines & whitespaces combinations due to beautifulsoup parsing
        text = re.sub(r'[ ]+\n', '\n', text)
        text = re.sub(r'\n[ ]+', '\n', text)
        text = re.sub(r'\n+', '\n', text)

        # To find MDA section, reformat item headers
        text = text.replace('\n.\n','.\n') # Move Period to beginning

        text = text.replace('\nI\nTEM','\nITEM')
        text = text.replace('\nITEM\n','\nITEM ')
        text = text.replace('\nITEM  ','\nITEM ')

        text = text.replace(':\n','.\n')

        # Math symbols for clearer looks
        text = text.replace('$\n','$')
        text = text.replace('\n%','%')

        # Reformat
        text = text.replace('\n','\n\n') # Reformat by additional breakline

        return text

    def download(self, index_path, txt_dir, txt_err_dir):
        # Save to txt dir
        self.txt_dir = txt_dir
        self.txt_err_dir = txt_err_dir

        if not os.path.exists(self.txt_dir):
            os.makedirs(self.txt_dir)

        if not os.path.exists(self.txt_err_dir):
            os.makedirs(self.txt_err_dir)

        # Count Total Urls to Process
        with open(index_path,'r') as fin:
            num_urls = sum(1 for line in fin)

        def iter_path_generator(index_path):

            with open(index_path,'r') as fin:
                reader = csv.reader(fin,delimiter=',',quotechar='\"',quoting=csv.QUOTE_ALL)
                for url_idx, row in enumerate(reader,1):
                    form_type, company_name, cik, date_filed, filename, symbol = row
                    url = os.path.join(SEC_GOV_URL,filename).replace("\\","/")
                    yield (url_idx, url, cik, symbol)

        def download_job(obj):
            url_idx, url, cik, symbol = obj

            fname = '_'.join(url.split('/')[-2:])

            fname, ext = os.path.splitext(fname)
            htmlname = fname + '.html'

            text_path = os.path.join(self.txt_dir,fname + '.txt')
            text_err_path = os.path.join(self.txt_err_dir,fname + '.txt')

            if os.path.exists(text_path):
                print("Already exists, skipping {}...".format(url))
                #sys.stdout.write("\033[K")
            else:
                print("Total: {}, Downloading & Parsing: {}-{}...".format(num_urls, url_idx, symbol))
                #sys.stdout.write("\033[K")
                try:
                    r = requests.get(url)
                    try:
                        # Parse html with Beautiful Soup
                        soup = BeautifulSoup( r.content, "html.parser" )
                        text = soup.get_text("\n")

                        # Process Text
                        text = self._process_text(text)
                        text_path = os.path.join(self.txt_dir,fname + '.txt')

                        # Write to file
                        with codecs.open(text_path,'w',encoding='utf-8') as fout:
                            fout.write(text)
                    except BaseException as e:
                        print("ERROR: parsing failed.: {}: {}: {}".format(url, cik, symbol))
                        # Write to file
                        with codecs.open(text_err_path,'w',encoding='utf-8') as ferr:
                            ferr.write(r.text)
                except BaseException as eb:
                    print("ERROR: download failed.: {}: {}: {}".format(url, cik, symbol))

                

        ncpus = cpu_count() if cpu_count() <= 8 else 8;
        pool = ProcessPool( ncpus )
        pool.map( download_job,
                    iter_path_generator(index_path) )

def main():
    parser = argparse.ArgumentParser("Download Edgar Form 10k according to index")
    parser.add_argument('--index_path',type=str)
    parser.add_argument('--txt_dir',type=str,default='./data/txt')
    parser.add_argument('--txt_err_dir',type=str,default='./data/txt_err')
    args = parser.parse_args()

    index_path = args.index_path

    # Download 10k forms, parse html and preprocess text
    form10k = Form10k()
    form10k.download(index_path=index_path, txt_dir=args.txt_dir, txt_err_dir=args.txt_err_dir)


if __name__ == "__main__":
    main()
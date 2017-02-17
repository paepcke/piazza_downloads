'''
Created on Jan 24, 2017

@author: paepcke
'''

import os
import urllib2
import cookielib
import sqlite3

from bs4 import BeautifulSoup
from urllib2 import URLError


class PiazzaDownloader(object):
    '''
    Class that knows how to download Piazza exports.
    '''


    def __init__(self, piazza_html_page_file):
        '''
        Constructor
        '''
        
        self.get_cookies('/Users/paepcke/Library/Application Support/Firefox/Profiles/7ibwxfso.default/cookies.sqlite')
        url_opener = self.get_piazza_opener()
        
        good_links = self.get_export_links(piazza_html_page_file)
        dirname = os.path.dirname(piazza_html_page_file)
        for link in good_links:
            try:
                #http_resp = urllib2.urlopen(link['href'])
                http_resp = url_opener.open(link['href'])
                if http_resp.code != 200:
                    raise URLError("Non-200 HTTP response")
            except URLError as e:
                raise URLError("Cannot download link %s from Piazza (%s)" % (link, `e`))

            zip_file = http_resp.read()
            try:
                with open(os.path.join(dirname, "oneLink.zip"), 'w') as file_obj:
                    file_obj.write(zip_file)
            except Exception as e:
                raise IOError("Cannot write file from link %s (%s" % (link, `e`))
            
    def get_piazza_opener(self):
        return urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_jar))
            
 
    def get_cookies(self, cookies_sqlite_file):
        
        self.cookie_jar = cookielib.CookieJar()
        
        con = sqlite3.connect(cookies_sqlite_file)
        cur = con.cursor()
        cur.execute("SELECT host, path, isSecure, expiry, name, value FROM moz_cookies")
        for item in cur.fetchall():
            c = cookielib.Cookie(0, item[4], item[5],
                None, False,
                item[0], item[0].startswith('.'), item[0].startswith('.'),
                item[1], False,
                item[2],
                item[3], item[3]=="",
                None, None, {})
            print c
            self.cookie_jar.set_cookie(c)    
    
    def get_export_page(self):
        pass
    
    def get_export_links(self, file_name):
        '''
        Takes a file name. Expects file to 
        contain an HTML page from the Piazza
        export site. Parses the HTML, and finds
        links that are actual download links.
        Returns array of links.
        '''
        
        try:
            with open(file_name, 'r') as file_pointer:
                page = file_pointer.read()
        except IOError as e:
            raise(IOError, "The file %s is not available (%s)." % (file_name, `e`))
        
        soup = BeautifulSoup(page)
        good_links = []
        for link in soup.find_all('a'):
            if str(link).find('download_class') == -1:
                continue
            #print(link)
            good_links.append(link)
        return good_links            

if __name__ == '__main__':
    downloader = PiazzaDownloader('/users/paepcke/tmp/piazzaLinksFall2011.html')

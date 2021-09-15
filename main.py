#!/usr/bin/python3
from bs4 import BeautifulSoup
import requests
import requests.exceptions
import urllib.parse
import re


def is_valid_url(url):
    parsed = urllib.parse.urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme) and (parsed.scheme == "http" or parsed.scheme == "https")


def get_links(url):
    urls = set()
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    for a in soup.findAll("a"):
        link = a.attrs.get("href")
        link = urllib.parse.urljoin(url, link)
        if is_valid_url(link):
            urls.add(link)
    return list(urls)


class Harvester:

    def __init__(self, domain, limit=10):
        self.emails = set()
        self.links = []
        self.domain = domain
        self.limit = limit
        self.urls = ['https://www.google.com/search?num=100&start=0&hl=en&q=%22%40{domain}%22'.format(domain=domain), 'http://search.yahoo.com/search?p=%22%40{domain}%22&n=100&start=1'.format(domain=domain)]

    def extract_emails(self,url):
      try:
        response = requests.get(url)
        new_emails = set(re.findall(r'[a-z0-9\.\-+_]+@+{}'.format(self.domain), response.text, re.I))
        self.emails.update(new_emails)
      except:
         print("[-] Could not extract email from url")


    def is_limit_reached(self):
        if len(self.emails) >= self.limit:
            print("[-] Email harvest limit reached : {}".format(self.limit))
            return True
        return False

    def crawl(self):
        print("[+] crawling search engines...")
        for url in self.urls:
          print("[+] processing url...")
          self.extract_emails(url)
          self.links = self.links + get_links(url)
          if self.is_limit_reached():
            return self.emails
        print("[+] Extracted {} emails".format(len(self.emails)))
        print("[+] Found {} links form search result".format(len(self.links)))
        print("[+] processing search result links...")
        for link in self.links:
            print("[+] processing url...")
            self.extract_emails(link)
            if self.is_limit_reached():
              return self.emails
        print("[+] Extracted {} emails".format(len(self.emails)))
        return self.emails


d = input("enter domain: ")
l = int(input("enter email limit: "))
harvester = Harvester(d, l)

all_emails = harvester.crawl()
filename = "emails.txt"
try:
    print("[+] Saving result to emails.txt")
    with open(filename, 'w') as out_file:
        for email in all_emails:
            try:
                out_file.write(email + "\n")
            except Exception as e:
                print("[-] Exception: " + email + e)
except Exception as e:
    print("[-] Error saving file: " + e)
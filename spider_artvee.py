#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
###################################################################################
#                                  Artvee Web Spider
#                                   spider_artvee.py
#                                     
# Author: David S. Brown
# Licensed under GPL3 21 Mar 2022
###################################################################################

'''
Release 22 Mar 2022: 

This program spiders through the high resolution images from the public domain website 
artvee.com and downloads them to the path you specify. The images are stored under a 
subdirectory for each category from the Artvee categories. This program works as of 
this date, but of course, websites change and beautifulSoup may need some tweaks to
its find inputs if the website changes.
           
Slava Ukraini! - Ukraine has retaken a city today. 
'''

from bs4 import BeautifulSoup
import os
import re
import requests
import argparse
import sys
import math
import csv

# Global Defaults
VERBOSE = 0
# Artvee catagories
CATEGORIES = ["abstract", "animals", "botanical", "drawings", "fashion", "figurative", "historical", \
                "illustration",  "japanese-art", "landscape",  \
                "mythology", "posters",  "religion",  "still-life", ]


# Uses soup to get the download link for the image, writes the image to a file 
def download_images(image_source, image_index, title, category, data_path):
    """ image_source (list): links to the image download buttons, use the second one [1] which is the high def link
        image_index (int): the current image out of the <perpage> thumbnails on the page
        title (str): artwork name 
    """
    image_request = requests.get(image_source[image_index].get("href"))
    image_bsoup = BeautifulSoup(image_request.content, "html.parser")
    image_link = image_bsoup.find_all("a", {"class" : "prem-link gr btn dis snax-action snax-action-add-to-collection snax-action-add-to-collection-downloads"})[1].get("href")
    image_name = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip() + ".jpg"         # clean up name
    image_category = os.path.join(data_path, category)                                                         #
    if not (os.path.isdir(image_category)):                                                                    # make image category sub directory if needed
        os.mkdir(image_category) 
    image_path = os.path.join(image_category, image_name)

    # if we have previously downloaded the file, then skip it. But still write to the cvs because past runs have
    # been unreliable. You can always sort out duplicates.
    if not os.path.exists(image_path):
        with open(image_path, "wb") as image_file:
            image_file.write(requests.get(image_link).content)
            image_file.close()
        if VERBOSE > 1: print("Wrote: ",image_path)

# For every page in the website getthumbnails and description of images in a list to download 
# and write description to the cvs file.
def spider_images(url, category, data_path, csv_path):
    """ url (str): URL for the category (c) pages
        category (str): The category used in the url
        data_path (str): The path where the csv, category tree and images will be written
        csv_path (str) : the name and path of the cvs file
    """

    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    thumbnails = soup.find_all("div", {"class" : re.compile("product-grid-item product woodmart-hover-tiled*")})
    image_source = soup.find_all("a", {"class" : "product-image-link linko"})
    image_index = 0

    for thumbnail in thumbnails:
        desc = []

        #Formatted in nested if-statements to prevent receiving an error for a missing element/class (None type)
        title = thumbnail.find("h3", class_="product-title")
        try:
            if (title.find("a") != None):
                title = title.get_text()
                desc.append(title)
        except:
            title = "Untitled"
            desc.append(title)

        artist_desc = thumbnail.find("div", class_="woodmart-product-brands-links")
        try:
            artist_desc = artist_desc.get_text()
            desc.append(artist_desc)
        except:
            artist_desc = "Unknown"
            desc.append(artist_desc)

        if VERBOSE > 1: print(desc)
        download_images(image_source, image_index, title, category, data_path)

        with open(csv_path, "a", newline = "", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(desc)
        f.close()

        image_index += 1

# iterate through the pages of <perpage> pictures each and download them all, if restarting
# you can tell it to start at page start_page
def process_pages(category,data_path,perpage,start_page,csv_path):
    """ category   : one of the artvee fixed categories
        start_page : skip the first pages and start downloading at page: start_page
        csv_path   : the name and path of the cvs file
    """
    if start_page is None: start_page = 1

    # Count the number of pages we will need to process for this category
    url = "https://artvee.com/c/%s/page/1/?per_page=%d" % (category,perpage)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find("p", class_="woocommerce-result-count").text.strip("results").strip()
    items = re.findall(r'\d+', results)[0]
    if VERBOSE>0: print("Number of items %s"%items)
    no_pages = math.floor(int(items) / perpage)
    if (int(items) % perpage > 0):
        no_pages += 1
    if VERBOSE>0: print("Number of pages %s"%no_pages)

    # process the pages one by one
    for p in range(start_page, no_pages + 1):
        # https://artvee.com/c/abstract/page/1/?per_page=perpage
        print("Currently looking at: %s, page %d" % (category, p))
        url = "https://artvee.com/c/%s/page/%d/?per_page=%d" % (category, p, perpage)
        if VERBOSE > 1: print(url)
        spider_images(url, category, data_path, csv_path)

if __name__ == "__main__":
    # Create Arguments
    parser = argparse.ArgumentParser(
        description='Scan web site artvee and stores high resolution images at the location specified only one category per instance'
    )
    # Count of verbose flags such as: arg_parse.py -v, arg_parse.py -vv, arg_parse.py -vvv, etc
    parser.add_argument("-v", "--verbose", action="count", default=0, help="increase output verbosity, use multiple -vvv >= 3=Debug")
    parser.add_argument('-c','--category', help="Required: Scan this category. Possible categories are: "+",".join(CATEGORIES))
    parser.add_argument('-d','--datapath', help="Required: The path to the location where the image files are written")
    parser.add_argument('-p','--startpage', default=1, help="The page within category to start the downloads from, default=1")
    parser.add_argument('-n','--perpage', default=32, help="The number of images per page on artvee, default is 32")
    parser.add_argument('-l','--log', default="artvee.csv", help="A CSV file with a log of all images downloaded, default:artvee.csv")
    args = parser.parse_args()
    VERBOSE= args.verbose

    # Prints help if required arguments datapath or category are missing
    if args.datapath is None or args.category is None:
        parser.print_help()
        sys.exit(1)

    if args.category not in CATEGORIES:
        print("Category must be one of: %s"%",".join(CATEGORIES))
        sys.exit(1)

    data_path = args.datapath
    csv_path  = os.path.join(data_path, args.category, args.log)
    if os.path.exists(csv_path) is None:
        with open(csv_path, "w",  newline = "", encoding="utf-8") as f:
            headers = ["Title", "Artist", "Category"]
            writer = csv.writer(f)
            writer.writerow(headers)
        f.close()

    if args.category is None:
        for category in CATEGORIES:
            process_pages(args.category,data_path,args.perpage,args.startpage,csv_path)
    else:
        process_pages(args.category,data_path,args.perpage,args.startpage,csv_path)

# Artvee Web Spider

*spider_artvee.py*

    usage: spider_artvee.py [-h] [-v] [-c CATEGORY] [-d DATAPATH] [-p STARTPAGE] [-n PERPAGE] [-l LOG]

Scan web site artvee and stores high resolution images at the location specified only one category per instance

Arguments:

      -h, --help            show this help message and exit
      -v, --verbose         increase output verbosity, use multiple -vvv >= 3=Debug
      -c CATEGORY, --category CATEGORY
                            Required: Scan this category. Possible categories are: abstract,animals,botanical,drawings,fashion,figurative,historical,illustration,japanese-
                            art,landscape,mythology,posters,religion,still-life
      -d DATAPATH, --datapath DATAPATH
                            Required: The path to the location where the image files are written
      -p STARTPAGE, --startpage STARTPAGE
                            The page within category to start the downloads from, default=1
      -n PERPAGE, --perpage PERPAGE
                            The number of images per page on artvee, default is 32
      -l LOG, --log LOG     A CSV file with a log of all images downloaded, default:artvee.csv



**Release** 22 Mar 2022:

This program crawls through the high resolution images from the public domain website
artvee.com and downloads them to the path you specify. The images are stored under a
subdirectory for each category from the Artvee categories. This program works as of
this date, but of course, websites change and beautifulSoup may need some tweaks to
its find inputs if the website changes.


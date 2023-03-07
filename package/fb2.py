"""This module contains all functions to create fb2 file from rss feed data"""

from package.create_html import is_valid_url_image
from package.create_html import create_list_of_feeds
from package.RssFeed import Feed
import logging
import sys
from pathlib import Path
import base64
import requests


def create_fb2(feeds_source, path, limit=0):
    """
        The function creates fb2 file from data contain feeds.
        Params:
            feeds_source: list of dictionaries with rss feed data or 1 dictionary with rss feed data.
            path: full path to directory where fb2 file will be saved.
            limit: (optional): quantity of news from each feed to write to html file (if limit is not set then
                               all news will be displayed)
        """
    logging.debug(f"Start 'create_fb2' function.")

    file_name = "rss_reader_book.fb2"
    full_path = Path(path) / file_name
    logging.debug(f"Start 'create_fb2' function.")
    cover_image_url = "http://booknerdalert.com/wp-content/uploads/2020/07/BookNews-tablet-print-1-768x632.jpg"

    # create feeds_list
    feeds_list = create_list_of_feeds(feeds_source)

    try:
        # slice data for limited output
        if limit > 0:
            for feed in feeds_list:
                feed['items'] = feed['items'][:limit]

        output = (
            """
            <?xml version="1.0" encoding="UTF-8"?>
            <FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0" xmlns:l="http://www.w3.org/1999/xlink">
            <coverpage><image l:href="#cover.png"/></coverpage>
            <body>
            """)
        pictures = ""  # variable for storing images in binary format
        image_num = 0  # number for each image in the document

        for feed in feeds_list:
            # create feed title and start section for it
            output += f"<section><title><strong>Feed: {feed['Feed title']}</strong></title>\n"
            for item in feed['items']:
                for key in item.keys():
                    # add title for each item
                    if key == "title":
                        output += f"<section><title><strong>{item[key]}</strong></title>"
                    # add images
                    elif is_valid_url_image(item[key]):
                        # Get image encoded to base64 as text from url
                        encoded_image = get_as_base64_text(item[key])
                        output += (f"<p><strong>{key.capitalize()}:</strong></p>\n" 
                                   f"<image l:href=\"#_{image_num}.jpg\"/>")
                        pictures += f"<binary content-type=\"image/jpeg\" " \
                                    f"id=\"_{image_num}.jpg\">{encoded_image}</binary>"
                        image_num += 1
                    # add links
                    elif key == "link":
                        output += f"<p><strong>{key.capitalize()}</strong>: " \
                                  f"<a l:href='{item[key]}'>{item[key]}</a></p>\n"
                    # add all other item elements that are not empty
                    elif item[key] != "":
                        output += f"<p><strong>{key.capitalize()}</strong>: {item[key]}</p>\n"
                output += f"\n{'*' * 50}\n"  # add line for visual separation of items
                output += "</section>"  # finish section for item in feed
            output += "</section>"  # finish section for feed
        output += "</body>"
        cover_image = f"<binary content-type=\"image/png\" " \
                      f"id=\"cover.png\">{get_as_base64_text(cover_image_url)}</binary>"
        output += cover_image
        output += pictures
        output += "</FictionBook>"
        # save file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(output)
        logging.debug(f"{file_name } file created. File path: '{path}'")

    except TypeError as exc:
        print(exc)
        print("There is no data for this source.")
        sys.exit()
    except FileNotFoundError:
        print("Invalid directory you specified with args.to_fb2")
        sys.exit()
    except PermissionError as exc:
        print(exc)
        sys.exit()
    else:
        logging.debug(f"No exception raised in 'create fb2' function")


def get_as_base64_text(url):
    """
    Function converting image from web url to binary base64 encoded format as text without b and ' symbols.
    args:
        url - web url that contains image
    """
    binary_data = base64.b64encode(requests.get(url).content)
    return str(binary_data).replace("b'", "").replace("'", "")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    new_feed = Feed("https://tech.onliner.by/feed")
    new_feed2 = Feed("https://3dnews.ru/hardware-news/rss")
    new_feed3 = Feed("https://news.yahoo.com/rss/")
    data_list = [new_feed.get_dict(), new_feed3.get_dict()]
    create_fb2(new_feed3.get_dict(), "C:/Users/PS/Desktop/123", 5)

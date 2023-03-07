"""This module contains all functions to create html file from rss feed"""
from package.RssFeed import Feed
import mimetypes
import logging
import sys
import os
from pathlib import Path
import requests


def create_html(feeds_source, path, limit=0):
    """
    The function creates html web page from feeds stored in database or feeds loaded from web link.
    Params:
        feeds_source: list of dictionaries with rss feed data or 1 dictionary with rss feed data.
        path: full path to directory to save html file.
        limit: (optional): quantity of news from each feed to write to html file (if limit is not set then
                      all news will be displayed)
    """
    logging.debug(f"Start 'create_html' function.")
    file_name = "rss_feed.html"
    full_path = Path(path) / file_name

    # create feeds_list
    feeds_list = create_list_of_feeds(feeds_source)

    try:
        # slice data for limited output
        if limit > 0:
            for feed in feeds_list:
                feed['items'] = feed['items'][:limit]
        output = "<!DOCTYPE html>\n<html>\n<body>\n"

        # create table of content
        output += "<h1>Feeds:\n</h1>"
        for feed in feeds_list:
            output += f"<h2>\n<a href='#{feed['Feed title']}'> {feed['Feed title']} </a>\n</h2>"
        output += f"\n{'*' * 50}\n"  # add line for visual separation

        # create main part of html
        for feed in feeds_list:
            output += f"<h2 id='{feed['Feed title']}'>Feed: {feed['Feed title']}</h2>\n"
            for item in feed['items']:
                for key in item.keys():
                    # add title for each item
                    if key == "title":
                        output += f"<h3><b><u>{key.capitalize()}</b>: {item[key]}</u></h3>\n"
                    # add links
                    elif key == "link":
                        output += f"<p><b>{key.capitalize()}</b>: " \
                                  f"<a href='{item[key]}'>{item[key]}</a></p>\n"
                    # add images
                    elif is_valid_url_image(item[key]):
                        output += f"<p><b>{key.capitalize()}:</b></p>\n" \
                                  f"<img src='{item[key]}' alt='image' width='300' height='200'>" \
                                  f'<br>'
                    # add all other non empty elements
                    elif item[key] != "":
                        output += f"<p><b>{key.capitalize()}</b>: {item[key]}</p>\n"
                output += f"\n{'*' * 50}\n"  # add line for visual separation
        output += "</body>\n</html>"

        # save file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(output)
        logging.debug(f"Html file created. File path: '{path}")

    except TypeError:
        print("There is no data for this source.")
        sys.exit()
    except FileNotFoundError:
        print("Invalid directory you specified with args.to_html")
        sys.exit()
    except PermissionError as exc:
        print(exc)
        sys.exit()
    else:
        logging.debug(f"No exception raised in 'create html' function")


def create_list_of_feeds(data):
    """
    This function make list of feeds from different types of input data
    Args:
        data: list of dictionaries or 1 dictionary with feeds data
    """
    if isinstance(data, dict):
        logging.debug(f"Received feeds type - 'dict'")
        return [data]
    elif isinstance(data, list):
        logging.debug(f"Received feeds type - 'list'")
        return data


def is_valid_url_image(url):
    """Check if web url contain image and exists on internet"""
    mimetype, encoding = mimetypes.guess_type(url)

    # can't read mimetype for images from yahoo web storage that starts with https://s.yimg.com/
    return (mimetype and mimetype.startswith('image')) or "https://s.yimg.com/" in url


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    new_feed = Feed("https://tech.onliner.by/feed")
    new_feed2 = Feed("https://3dnews.ru/hardware-news/rss")
    new_feed3 = Feed("https://news.yahoo.com/rss/")
    data_list = [new_feed.get_dict(), new_feed2.get_dict(), new_feed3.get_dict()]
    create_html(data_list, "C:/Users/PS/Desktop/123")

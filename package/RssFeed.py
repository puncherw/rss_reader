"""
This module contains classes and functions for running rss_reader program.
Classes:
Feed  - contains all attributes and methods to manipulate data from rss feed.
NotRssLink  - exception class to handle urls that do not contains rss feed data.
NoNewsFound -  exception occurs when news were not found by the date
"""

import json
import os.path
import requests
from bs4 import BeautifulSoup, Tag
import warnings
from datetime import datetime
from dateutil.parser import parse
import logging
import sys
import pkg_resources
from pathlib import Path


class Feed:
    """
    A class to represent rss feed.

    Attributes
    ----------
    req : requests.models.Response
        `Response <Response>` object, which contains a server's response to an HTTP request
    soup : bs4.BeautifulSoup
        data structure representing a parsed XML document for url of rss feed
    feed_title : str
        Title of the rss feed
    feed_items : bs4.element.ResultSet
        contains all data of 'item' elements
    news_count : int
        count of news in rss feed

    Methods
    -------
    get_dict(limit=0):
        Returns dictionary with 2 keys 'feed_title' and 'items'.
        'items' contains list if dictionaries for each rss news"
    get_json_from_feed(limit=0):
        This method returns news from the feed in json format.
    get_text_from_feed(limit=0):
        This method returns human-readable text with news from rss feed.
    html_to_text(input):
        This method checks if string has HTML tags, and returns clean text without tags.
    """

    def __init__(self, rss_url):
        """
        Constructs all the necessary attributes for the Feed object.

        Parameters
        ----------
        rss_url : url link
            url link to rss feed

        Attributes
        ----------

        req : requests.models.Response
            `Response <Response>` object, which contains a server's response to an HTTP request
        soup : bs4.BeautifulSoup
            data structure representing a parsed XML document for url of rss feed
        feed_title : str
            Title of the rss feed
        feed_items : bs4.element.ResultSet
            contains all data of 'item' elements
        news_count : int
            count of news in rss feed
        source: url
            url of rss feed
        """

        try:
            self.source = rss_url.rstrip("/")
            self.req = requests.get(rss_url)
            self.soup = BeautifulSoup(self.req.content, "xml")
            if not self.soup.find("rss"):
                raise NotRssLink(f"The source '{rss_url}' do not contain rss feed data")
            self.feed_title = self.soup.find("title").text
            self.feed_items = self.soup.findAll('item')
            self.news_count = len(self.feed_items)
            logging.debug(f"New Feed object '{self.feed_title}' created. "
                          f"Total news count in the feed: {self.news_count} ")

        except requests.exceptions.MissingSchema as exc:
            print(exc)
            sys.exit()
        except requests.exceptions.InvalidSchema as exc:
            print(exc)
            sys.exit()
        except requests.exceptions.ConnectionError as exc:
            print(exc)
            sys.exit()
        except NotRssLink as exc:
            print(exc)
            sys.exit()

    @staticmethod
    def html_to_text(input):
        """
        Cleaning text from html tags.

        Parameters: input (str): string data
        Returns: String without html tags

        """
        # need warning filter because some tag items consists only urls, what leads to warning from bs4
        warnings.filterwarnings("ignore", category=UserWarning, module='bs4')
        soup = BeautifulSoup(input, "html.parser")
        if bool(soup.find()):
            return soup.get_text().replace("&nbsp", "").replace("&laquo;", "").replace("&raquo;", "")
        else:
            return input.replace("&nbsp", "").replace("&laquo;", "").replace("&raquo;", "")

    def get_dict(self, limit=0):
        """
        This method returns dictionary with title and items from Feed object.
        limit (optional argument) - quantity of news to display (if limit is not set then include all news )
        """
        logging.debug(f"Function 'get_dict' started. Limit: {limit}")

        feed_dict = {"Feed title": self.feed_title, "Source": self.source}
        items_list = []

        for item in self.feed_items:
            item_dict = {}
            for el in item:
                # skip non Tag elements of soup
                if not isinstance(el, Tag):
                    continue
                else:
                    # get data from elements that contains text
                    if el.text:
                        item_dict[el.name] = Feed.html_to_text(el.text)
                    # get data from elements that contains url
                    elif el.get('url'):
                        item_dict[el.name] = el.get("url")
            items_list.append(item_dict)
        # sorting items by date
        sorted_items = sorted(items_list, key=lambda x: parse(x['pubDate']), reverse=True)
        # slice data for limited output
        if limit > 0:
            feed_dict['items'] = sorted_items[:limit]
        else:
            feed_dict['items'] = sorted_items

        return feed_dict

    def print_json_from_feed(self, limit=0):
        """
        This method returns news from source feed in json format.
        limit (optional argument)  - quantity of news to display (if limit is not set then all news will be displayed)
        """
        logging.debug(f"Function 'print_json_from_feed' started.")

        result_json = json.dumps(self.get_dict(limit), ensure_ascii=False, indent=3)
        logging.debug(f"Creating of json completed. Count of news in json output: "
                      f"{limit if self.news_count > limit > 0 else self.news_count}")
        print(result_json)

    def print_text_from_feed(self, limit=0):
        """
        This method returns human-readable news from rss feed.
        limit (optional argument) - quantity of news to display
                                    (if limit is not set then all news will be displayed)
        """
        logging.debug(f"Function 'print_text_from_feed' started.")

        feed_dict = self.get_dict(limit)

        output = f"\nFeed: {self.feed_title}\n" + "_" * (len(self.feed_title) + 6) + "\n\n"
        for item in feed_dict['items']:
            for key in item.keys():
                if item[key] != "":
                    output += f"{key.capitalize()}: {item[key]}\n"
            output += f"\n{'*'*80}\n"
        logging.debug(f"Creating of text completed. Count of news in text output: "
                      f"{limit if self.news_count > limit > 0 else self.news_count}")
        print(output)

    def write_to_database(self, file_name):
        """
        Write new items to storage file.
        Args:
            file_name: path to storage file
        """
        logging.debug(f"Starting 'write_to_database' function for Feed instance '{self.feed_title}'")
        storage_path = pkg_resources.resource_filename(__name__, file_name)
        # create storage file
        if not os.path.exists(storage_path):
            with open(storage_path, "w") as json_file:
                json.dump([self.get_dict()], json_file)
                logging.debug(f"Created storage.json. "
                              f"Data from '{self.feed_title}' added to storage.json. "
                              f"Count of news added:{self.news_count}")
        # update storage file if it already exist
        else:
            logging.debug(f"storage.json already exists")
            try:
                with open(storage_path, "r") as json_file:
                    feed_list = json.load(json_file)
                feeds_sources = [feed['Source'] for feed in feed_list]
                logging.debug(f"Data from following feeds sources already in the storage: {feeds_sources}")

                # for new source add full dictionary to database.
                if self.source not in feeds_sources:
                    feed_list.append(self.get_dict())
                    logging.debug(f"Data from '{self.source}' is not in the storage.")
                    logging.debug(f"All news from '{self.get_dict()['Feed title']}' added to the storage.")

                # for source that already in storage adding only new items
                else:
                    logging.debug(f"Data from source '{self.source}' are already in the storage.")
                    for feed in feed_list:
                        if feed['Source'] == self.source:
                            logging.debug(f"Start checking feed '{feed['Feed title']}' "
                                          f"if there are new items in it.")
                            # create list of unique identifiers for items that already in the storage
                            stored_feed_guids = []
                            for item in feed['items']:
                                stored_feed_guids.append(item['guid'])
                            # check each web item if it's guid not in the storage
                            for new_item in self.get_dict()['items']:
                                if new_item['guid'] not in stored_feed_guids:
                                    feed['items'].append(new_item)
                                    logging.debug(f"New item '{new_item['title']}' added to the storage.")
            except json.decoder.JSONDecodeError:
                print(f"No data in the file '{path}'")
                # if file is empty add full dictionary to it
                with open(storage_path, "w") as json_file:
                    json.dump([self.get_dict()], json_file)
                logging.debug(f"Data from '{self.feed_title}' added to storage.json. "
                              f"Count of news added:{self.news_count}")
            # save storage file
            with open(storage_path, "w") as json_file:
                json.dump(feed_list, json_file)

    @staticmethod
    def read_from_database(date, file_name, source=None,):
        """
        This function read data from database and returns data filtered by date and source"
        If source is not not set, then it returns list of dictionaries from all sources with data filtered by date.
        args:
            date: date in "%Y%m%d" format (Example: 20211027).
            file_name: name of storage file.
            source: feed url, for which we wand to get data.
        """
        logging.debug(f"Starting 'read_from_database' function with params: date={date},source={source}")
        # create relative path to storage
        storage_path = pkg_resources.resource_filename(__name__, file_name)

        # get all feeds from storage
        try:
            with open(storage_path, "r") as json_file:
                feeds_list = json.load(json_file)
            logging.debug(f"Data from '{storage_path}' read")
            logging.debug(f"Feeds in database: '{[feed['Feed title'] for feed in feeds_list]}'")
        except json.decoder.JSONDecodeError:
            print(f"No data in the file '{storage_path}'.")
            sys.exit()
        except FileNotFoundError:
            print("No storage detected. Please run rss_reader with source argument first to create storage.")
            sys.exit()

        # get news by date for all sources
        try:
            if not source:
                output_list = []
                for feed in feeds_list:
                    items_on_date = []

                    for item in feed['items']:
                        if parse(item['pubDate']).date() == datetime.strptime(date, "%Y%m%d").date():
                            items_on_date.append(item)

                    sorted_items = sorted(items_on_date,
                                          key=lambda x: parse(x['pubDate']),
                                          reverse=True)
                    logging.debug(f"The feed '{feed['Feed title']}' has {len(items_on_date)} "
                                  f"items on the date - {datetime.strptime(date, '%Y%m%d').date()}.")
                    if items_on_date:
                        new_dict = {
                            "Feed title": feed["Feed title"],
                            "Source": feed["Source"],
                            "items": sorted_items,
                        }
                        output_list.append(new_dict)
                        logging.debug(f"List with {len(output_list)} feeds created.")
                if output_list:
                    return output_list
                else:
                    raise NoNewsFound(f"No news were found in storage for all feeds "
                                      f"on the date {datetime.strptime(date, '%Y%m%d').date()} ")
        except NoNewsFound as exc:
            print(exc)
            sys.exit()

        # get news by source and date
        try:
            for feed in feeds_list:
                if feed["Source"] == source:
                    items_on_date = []
                    number_of_news_this_date = 0
                    for item in feed['items']:
                        if parse(item['pubDate']).date() == datetime.strptime(date, "%Y%m%d").date():
                            items_on_date.append(item)
                            number_of_news_this_date += 1
                    logging.debug(f"Number of news for requested date:{number_of_news_this_date}")
                    if number_of_news_this_date == 0:
                        raise NoNewsFound(f"No news were found in storage for feed '{feed['Feed title']}' "
                                          f"on the date {datetime.strptime(date, '%Y%m%d').date()} ")
                    sorted_items = sorted(items_on_date,
                                          key=lambda x: parse(x['pubDate']),
                                          reverse=True)
                    new_dict = {
                        "Feed title": feed["Feed title"],
                        "Source": feed["Source"],
                        "items": sorted_items,
                    }
                    logging.debug(f"Feed '{new_dict['Feed title']}' received from storage."
                                  f"The Feed contain {len(new_dict['items'])} items.")
                    return [new_dict]
        except NoNewsFound as exc:
            print(exc)
            sys.exit()

    @staticmethod
    def print_data_json(feed_list, limit=0):
        """
        This method prints news from list of feeds.
        args:
            feed_list: list of feeds received from storage.
            limit (optional): quantity of news from each feed to display (if limit is not set then
                              all news will be displayed)
        """
        logging.debug(f"Function 'print_data_json' started. Input data type: {type(feed_list)}")
        try:
            if limit > 0:
                for feed in feed_list:
                    feed['items'] = feed['items'][:limit]
            print(json.dumps(feed_list, ensure_ascii=False, indent=3))
        except TypeError:
            print("There is no data for this source in the storage.")
            sys.exit()

    @staticmethod
    def get_text_from_storage(feed_list, limit=0):
        """
        This method prints news from feeds list in human-readable format.
        feed_list: list of feeds received from storage.
        limit (optional): quantity of news from each feed to display (if limit is not set then
                          all news will be displayed)
        """
        logging.debug(f"Function 'get_text_from_storage' started. Input data type: {type(feed_list)}")

        try:
            if limit > 0:
                for feed in feed_list:
                    feed['items'] = feed['items'][:limit]
            output = ""
            for feed in feed_list:
                output += f"\nFeed: {feed['Feed title']}\n" + "-" * 80 + "\n"
                for item in feed['items']:
                    for key in item.keys():
                        if item[key] != "":
                            output += f"{key.capitalize()}: {item[key]}\n"
                    output += f"\n{'*' * 80}\n"
            return output

        except TypeError:
            print("There is no data for this source in the storage.")
            sys.exit()

    def __str__(self):
        return f"Rss feed {self.feed_title}"


class NotRssLink(Exception):
    """Exception class for urls that do not contain rss data"""


class NoNewsFound(Exception):
    """Exception occurs when news were not found by the date"""

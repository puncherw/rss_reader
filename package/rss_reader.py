"""This module contains main code to run rss_reader command-line program."""

from package.RssFeed import Feed
from package.create_html import create_html
from package.fb2 import create_fb2
import argparse
import logging
from datetime import datetime
from pathlib import Path

parser = argparse.ArgumentParser(description="Get news from rss feed")
parser.add_argument("--version", action="version", version="Rss reader version 4.0")
parser.add_argument("--limit", default=0, type=int, help="Limit of news to display.")
parser.add_argument("--json", action="store_true", help="Print result as JSON in stdout.")
parser.add_argument("--verbose", action="store_true", help="Outputs verbose status messages.")
parser.add_argument("--date", type=str, help="Publishing date of news to display.")
parser.add_argument("--to_html", type=str, help="Create html file with news from rss feed.")
parser.add_argument("--to_fb2", type=str, help="Create fb2 file with news from rss feed.")
parser.add_argument("source", type=str, nargs="?", help="Rss feed url", default=None)
args = parser.parse_args()


def main():
    """
    Main function to run rss_reader command-line program.
    """
    date_format = "%Y%m%d"
    storage_file = "storage.json"

    # remove dash for correct storing used sources when loading data from database
    if args.source:
        args.source = args.source.rstrip("/")

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    if not args.source and not args.date:
        logging.debug(f"Args.source: {args.source}")
        logging.debug(f"Args.date: {args.date}")
        print("At least one arguments are required: source or date.")
        print("usage: rss_reader [-h] [--version] [--limit LIMIT] [--json] [--verbose] "
              "[--date DATE] [--to_html TO_HTML] [--to_fb2 TO_FB2] [source]")

    elif args.source and not args.date:
        logging.debug(f"Args.source: {args.source}")
        logging.debug(f"Args.date: {args.date}")

        new_feed = Feed(args.source)
        new_feed.write_to_database(storage_file)

        # create files using data from url
        if args.to_html:
            create_html(feeds_source=new_feed.get_dict(),
                        path=args.to_html,
                        limit=args.limit)
        if args.to_fb2:
            create_fb2(feeds_source=new_feed.get_dict(),
                       path=args.to_fb2,
                       limit=args.limit)

        # output to stdout
        if args.json:
            new_feed.print_json_from_feed(args.limit)
        else:
            new_feed.print_text_from_feed(args.limit)

    elif not args.source and args.date:
        logging.debug(f"Args.source: {args.source}")
        logging.debug(f"Args.date: {args.date}")

        # date validation
        if not is_valid_date(args.date, date_format):
            return
        else:
            logging.debug(f"Arg.date '{args.date}' is correct.")

        # get data from storage file
        feeds_from_database = Feed.read_from_database(date=args.date, file_name=storage_file, source=args.source)

        # create html using data from storage file
        if args.to_html:
            create_html(feeds_source=feeds_from_database,
                        path=args.to_html,
                        limit=args.limit)

        # create fb2 using data from storage file
        if args.to_fb2:
            create_fb2(feeds_source=feeds_from_database,
                       path=args.to_fb2,
                       limit=args.limit)

        # print to stdout
        if args.json:
            Feed.print_data_json(feeds_from_database, args.limit)
        else:
            print(Feed.get_text_from_storage(feeds_from_database, args.limit))

    elif args.source and args.date:
        logging.debug(f"Args.source: {args.source}")
        logging.debug(f"Args.date: {args.date}")

        # date validation
        if not is_valid_date(args.date, date_format):
            return
        else:
            logging.debug(f"Arg.date '{args.date}' is correct.")

        # get data from storage file
        feeds_from_database = Feed.read_from_database(date=args.date, file_name=storage_file, source=args.source)

        # create html using data from storage file for exact source
        if args.to_html:
            create_html(feeds_source=feeds_from_database,
                        path=args.to_html,
                        limit=args.limit)

        # create fb2 using data from storage file for exact source
        if args.to_fb2:
            create_fb2(feeds_source=feeds_from_database,
                       path=args.to_fb2,
                       limit=args.limit)

        # print to stdout using data from storage file for exact source
        if args.json:
            print(Feed.print_data_json(feeds_from_database, args.limit))
        else:
            print(Feed.get_text_from_storage(feeds_from_database, args.limit))


def is_valid_date(date_string, format):
    """
    Validation of date string format. Returns True if format is matching.
    Arguments:
        date_string - string that suppose to contain date. Example: 20201019 or 2021-10-11
        format - format of date as in datetime library. Example: %Y%m%d or %Y-%m-%d
    """
    try:
        datetime.strptime(date_string, format)
    except ValueError:
        print(f"String {date_string} is incorrect date. Correct format %Y%m%d (Example: 20211021)")
        return False
    else:
        return True



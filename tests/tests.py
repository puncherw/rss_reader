""" This module contains unit tests for rss_reader functionality """

import unittest
from package.RssFeed import Feed, NotRssLink
from package.create_html import is_valid_url_image
from package.create_html import create_list_of_feeds
from package.fb2 import create_fb2
from package.create_html import create_html
from package.rss_reader import is_valid_date
from dateutil.parser import parse
import requests


class RssReaderTests(unittest.TestCase):
    """Base class to run unit tests for rss reader program"""

    def test_link(self):
        """Testing exception handling if bad url"""
        with self.assertRaises(SystemExit):
            Feed("https://people.onliner.by/")
        with self.assertRaises(SystemExit):
            Feed("123")
        with self.assertRaises(SystemExit):
            Feed("http://abc")
        with self.assertRaises(SystemExit):
            Feed("ttps://people.onliner.by/feed")

    def test_html_items(self):
        """Testing of Feed static method html_to_text"""

        data = '<p><a href="https://people.onliner.by/2021/10/18/pod-permyu-shestiklassnik-ustroil-' \
               'strelbu-v-shkole-ego-obezvredil-direktor"><img ' \
               'src="https://content.onliner.by/news/thumbnail/30c6fa769b41f2ad455106e98ec8283d.jpeg" alt="" ' \
               '/></a></p><p>Ученик устроил стрельбу в школе.</a></p>'
        self.assertEqual(Feed.html_to_text(data), "Ученик устроил стрельбу в школе.")

    def test_descending_by_date(self):
        """Testing if all items is sorted descending by pubDate."""

        def is_descending(lst):
            """
            This function accepts list as argument and checks if all elements
            in the list are in descending order.
            """
            i = 1
            while i < len(lst):
                if lst[i] > lst[i - 1]:
                    return False
                i += 1
            else:
                return True

        def get_pubDates_list(rss_dict):
            """Get list of pubDates from items in rss feed"""
            pubDates = []
            for item in rss_dict['items']:
                pubDates.append(item['pubDate'])
            return pubDates

        onl_feed = Feed("https://people.onliner.by/feed")
        yahoo_feed = Feed("https://news.yahoo.com/rss/")
        lenta_feed = Feed("https://lenta.ru/rss/news")

        self.assertEqual(is_descending([parse(x) for x in get_pubDates_list(onl_feed.get_dict())]), True)
        self.assertEqual(is_descending([parse(x) for x in get_pubDates_list(yahoo_feed.get_dict())]), True)
        self.assertEqual(is_descending([parse(x) for x in get_pubDates_list(lenta_feed.get_dict())]), True)

    def test_date_validation(self):
        """Test function date_is_valid"""
        date_format = "%Y%m%d"
        self.assertEqual(is_valid_date("20211320", date_format), False)
        self.assertEqual(is_valid_date("20211220", date_format), True)
        self.assertEqual(is_valid_date("123", date_format), False)
        self.assertEqual(is_valid_date("abc", date_format), False)

    def test_read_data_from_database(self):
        """Test raises when storage is not created"""
        with self.assertRaises(SystemExit):
            Feed.read_from_database(date="20201025", source=None, file_name="storage1.json")

    def test_image_url(self):
        """
        Testing validation of urls with image.
        """
        url1 = "https://s.yimg.com/uu/api/res/1.2/bzN5b4bWT3Gh5mPOCpCNYg--~B/" \
               "aD0xODY2O3c9MjQ4ODthcHBpZD15dGFjaHlvbg--/" \
               "https://media.zenfs.com/en/insider_articles_922/71b55f0b83872c715b7bcc9b62d11669"
        url2 = "https://icdn.lenta.ru/images/2021/10/26/14/20211026144715331/" \
               "pic_ed6e37f8cadef633084257b696c03ba2.jpg"
        url3 = "https://3dnews.ru/assets/external/illustrations/2021/10/17/1051476/sm.Box.400.JPG"
        url4 = "https://content.onliner.by/news/thumbnail/74099a009069e4d93fa01068a480f1aa.jpeg"
        url5 = "https://money.onliner.by"
        self.assertEqual(is_valid_url_image(url1), True)
        self.assertEqual(is_valid_url_image(url2), True)
        self.assertEqual(is_valid_url_image(url3), True)
        self.assertEqual(is_valid_url_image(url4), True)
        self.assertEqual(is_valid_url_image(url5), False)

    def test_feeds_creation(self):
        """Tests if feeds_list created properly"""
        self.assertEqual(create_list_of_feeds({1:1,2:2,3:3}), [{1:1,2:2,3:3}])
        self.assertEqual(create_list_of_feeds([1,2,3]), [1,2,3])

    def test_fb2_creation(self):
        """Test of creating of fb2 file"""
        new_feed = Feed("https://tech.onliner.by/feed")
        with self.assertRaises(SystemExit):
            create_fb2(feeds_source=new_feed.get_dict(),
                       path="123",
                       limit=2)

    def test_html_creation(self):
        """Test of creating of html file"""
        new_feed = Feed("https://tech.onliner.by/feed")
        with self.assertRaises(SystemExit):
            create_html(feeds_source=new_feed.get_dict(),
                        path="123",
                        limit=-1)


if __name__ == "__main__":
    unittest.main()


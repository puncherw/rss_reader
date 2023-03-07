#Python command-line RSS reader.
 Version 3.0.

RSS reader is a command-line utility which receives RSS URL and prints results in human-readable format.

```
usage: rss_reader [-h] [--version] [--limit LIMIT] [--json] [--verbose] [--date DATE] [--to_html TO_HTML] [--to_fb2 TO_FB2] [source]
At least one arguments are required: source or date.

Get news from rss feed

positional arguments:
  source             Rss feed url

optional arguments:
  -h, --help         show this help message and exit
  --version          show program's version number and exit
  --limit LIMIT      Limit of news to display.
  --json             Print result as JSON in stdout.
  --verbose          Outputs verbose status messages.
  --date DATE        Publishing date of news to display from storage file.
  --to_html TO_HTML  Create html file with news from rss feed. 
                     This argument receives the path where new html file will be saved.
  --to_fb2 TO_FB2    Create fb2 file with news from rss feed.
                     This argument receives the path where new fb2 file will be saved.   
```


**JSON structure of one feed:**

```shell
{
   "Feed title": the title of rss feed,
   "items"*: 
[
      {
         "title": the title of the story linked to by the item,
         "link": The URL of the story the item is describing,
         "pubDate": The publication date of the item,
         "guid": contain a string that uniquely identifies the item,
         "description": A synopsis of the story,
         ... 
         * Items can contain different information depends on rss feed schema. 
      },
   ]
}

```

crap script to self host a podcast.

1. `pip3 install -r requirements`
2. to go webserver dir, e.g. `/var/www/podcast`
3. upload all files and MP3 files
4. change `header.xml` according to your needs (author, title,...)
5. run `./mypodcast.py --headerfile header.xml "pathtomypodcastfile.mp3"` verify and pipe to rss.xml or whatever
6. if you have `rss.xml` and want to add more episodes, run `./mypodcast.py --rssfile rss.xml "pathtomypodcastfile.mp3"` and verify it
7. fork it and send PR to make it better

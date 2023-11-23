crap script to self host a podcast.

1. install requirements
2. to go webserver dir, e.g. /var/www/podcast
3. upload all files and MP3 files
4. change header.xml according to your needs (author, title,...)
5. change baseurl in mypodcast.py to yours
6. run ./mypodcast.py "PATH TO MY .MP3" verify and pipe to rss.xml or whatever
7. fork it and send PR to make it better
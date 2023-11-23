#!/usr/bin/python3
from mutagen.mp3 import MP3
import argparse
from datetime import datetime
import os
import requests

# change this to your site
base_url = "https://bongoalex.bongoalex/"



class PodcastItem:
    def __init__(self, title, itunes_title, description, pub_date, link, guid, content_encoded, episode, episode_type, subtitle, summary, explicit, keywords, author, enclosure_url, enclosure_type, enclosure_length):
        self.title = title
        self.itunes_title = itunes_title
        self.description = description
        self.pub_date = pub_date
        self.link = link
        self.guid = guid
        self.content_encoded = content_encoded
        self.episode = episode
        self.episode_type = episode_type
        self.subtitle = subtitle
        self.summary = summary
        self.explicit = explicit
        self.keywords = keywords
        self.author = author
        self.enclosure_url = enclosure_url
        self.enclosure_type = enclosure_type
        self.enclosure_length = enclosure_length
    def toPodcast(self):
        item_xml  = "    <item>\n"
        item_xml += "      <title>"+self.title+"</title>\n"
        item_xml += "      <itunes:title>"+self.itunes_title+"</itunes:title>\n"
        item_xml += "      <description>"+self.description+"</description>\n"
        item_xml += "      <pubDate>"+self.pub_date+"</pubDate>\n"
        item_xml += "      <link>"+self.link+"</link>\n"
        item_xml += "      <guid>"+self.guid+"</guid>\n"
        item_xml += "      <content:encoded>"+self.content_encoded+"</content:encoded>\n"
        item_xml += "      <itunes:episode>"+self.episode+"</itunes:episode>\n"
        item_xml += "      <itunes:episode_type>"+self.episode_type+"</itunes:episode_type>\n"
        item_xml += "      <itunes:subtitle>"+self.subtitle+"</itunes:subtitle>\n"
        item_xml += "      <itunes:summary>"+self.summary+"</itunes:summary>\n"
        item_xml += "      <itunes:explicit>"+self.explicit+"</itunes:explicit>\n"
        item_xml += "      <itunes:keywords>"+self.keywords+"</itunes:keywords>\n"
        item_xml += "      <itunes:author>"+self.author+"</itunes:author>\n"
        item_xml += "        <enclosure url=\""+self.enclosure_url+"\""
        item_xml += " type=\""+self.enclosure_type+"\""
        item_xml += " length=\""+self.enclosure_length+"\"/>\n"
        item_xml += "    </item>"
        return item_xml


def read_file(filename):
    with open(filename, 'r') as file:
        content = file.read()
    return content
def write_file(filename, content):
    with open(filename, 'w') as file:
        file.write(content)
def append_file(filename, content):
    with open(filename, 'a') as file:
        file.write(content)
def get_mp3_length(file_path):
    audio = MP3(file_path)
    length_in_seconds = audio.info.length
    return round(length_in_seconds)


# Create the parser
parser = argparse.ArgumentParser(description='My really really shity podcast producer script')
# Add arguments
parser.add_argument('input_file', help='Path to the input MP3 file')
#parser.add_argument('-o', '--output', default='NONE', help='Path to the output file')
# Parse the arguments
args = parser.parse_args()
# Access the parsed arguments
input_file = args.input_file
#output_file = args.output
# Print the help message if requested
if input_file == '-h' or input_file == '--help':
    parser.print_help()
    exit()




# Get the current date and time
current_datetime = datetime.now()
# Format the date and time as per the desired format
formatted_datetime = current_datetime.strftime("%a, %d %b %Y %H:%M:%S +0000")
# Get length of MP3
podcast_len = get_mp3_length(input_file)


# read header
header_content = read_file('header.xml')
#write_file('feed.xml', header_content)
# get MP3 file data
directory = os.path.dirname(input_file)
#print("Directory:", directory)
# Get the filename with extension
filename = os.path.basename(input_file)
#print("Filename:", filename)

# build vars
mp3_url_location = base_url + requests.utils.quote(directory) + "/" + requests.utils.quote(filename)


item = PodcastItem(
    filename,
    filename,
    "Ein weiterer toller Podcast",
    formatted_datetime,
    base_url,
    base_url,
    "Ein weiterer toller Podcast",
    "1",
    "full",
    filename,
    "Ein weiterer toller Podcast",
    "no",
    "keywords",
    "@bongoalex",
    mp3_url_location,
    "audio/mpeg",
    str(podcast_len)
    )

print(header_content)
print(item.toPodcast())
print("\n\n  </channel>\n</rss>")

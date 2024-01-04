#!/usr/bin/python3
from mutagen.mp3 import MP3
import argparse
from datetime import datetime
import os
import requests
import sys
import xml.etree.ElementTree as ET
import openai

####################################################################################
# vars #############################################################################
####################################################################################
base_url = "https://bongoalex.bongoalex/"
openai_org = "org-bar"
openai_apikey = ("sk-foo")
####################################################################################
# classes ##########################################################################
####################################################################################
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
####################################################################################
# functions ########################################################################
####################################################################################
def askChatGPTv2(question):
    openai.organization = openai_org
    openai.api_key = openai_apikey
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": question,
            },
        ],
    )
    return(completion.choices[0].message.content)
def read_file(filename):
    with open(filename, 'r') as file:
        content = file.read()
    return content
def read_headerfile(filename):
    # like read_file, but stops after </itunes:owner>
    result = ""
    with open(filename, 'r') as file:
        for line in file:
            if '</itunes:owner>' in line:
                result += line
                break
            result += line
    return result
def read_items_from_file(filename):
    # i hope nobody reads this ugly code .. and if you do - go fix it!
    result = ""
    in_items = False
    with open(filename, 'r') as file:
        for line in file:
            if '<item>' in line:
                in_items = True
            if in_items:
                result += line
            if '</item>' in line:
                in_items = False
    return result
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
def get_baseurl_from_headerfile(filename):
    with open(filename, 'r') as file:
        for line in file:
            if '<link>' in line:
                break
    return line.split(">")[1].split("<")[0]
def update_lastbuilddate(headercontent, newdate):
    result = ""
    for line in headercontent.split("\n"):
        if '<lastBuildDate>' in line:
            line = line.replace("{{ lastbuilddate }}", newdate)
        result += line + "\n"
    return result
def print_err(msg):
    # print to stderr, as func in case logging or else needs to be added
    # also stderr is printed when you pipe output ;)
    print(msg, file=sys.stderr)

####################################################################################
# main code ########################################################################
####################################################################################
if __name__ == "__main__":
    # Create the parser and add arguments
    parser = argparse.ArgumentParser(description='My really really shity podcast producer script')
    parser.add_argument('input_file', help='Path to the input MP3 file')
    parser.add_argument('--headerfile', help='RSS Header file', required=False)
    parser.add_argument('--rssfile', help='Read and append to existing RSS file', required=False)
    # Parse the arguments
    args = parser.parse_args()
    # Access the parsed arguments
    input_file = args.input_file
    # Print the help message if requested
    if input_file == '-h' or input_file == '--help':
        parser.print_help()
        exit()
    # Extract baseurl from header file
    if args.headerfile:
        global headerfile
        base_url = get_baseurl_from_headerfile(args.headerfile)
        headerfile = args.headerfile
        print_err("[i] Using headerfile " + headerfile)
    if args.rssfile:
        global rssfile
        base_url = get_baseurl_from_headerfile(args.rssfile)
        rssfile = args.rssfile
        print_err("[i] Using RSS file " + rssfile)
    if args.headerfile is None and args.rssfile is None:
        print_err("[-] You need to supply a headerfile OR rssfile in order to extract the base parameters.")
        sys.exit(1)

    # STEP 1
    # Get some data needed for creating the class like the current date and time
    current_datetime = datetime.now()
    # Format the date and time as per the desired podcast format
    formatted_datetime = current_datetime.strftime("%a, %d %b %Y %H:%M:%S +0000")

    # STEP 2
    # read header and update lastbuilddate
    # a) read it from existing rss.xml file, if supplied
    if args.rssfile:
        header_content = read_headerfile(rssfile)
        header_content = update_lastbuilddate(header_content, formatted_datetime)
        # read other items
        current_rss_content = read_items_from_file(rssfile)
    # b) read it from headerfile
    if args.headerfile:
        header_content = read_headerfile(headerfile)
        header_content = update_lastbuilddate(header_content, formatted_datetime)
    # note: if both are supplied, because some champ didnt think about it, headerfile takes presedence
    #write_file('feed.xml', header_content)

    # create mp3 url location based on base_url, directory and filename for the class
    # get MP3 file data of new episode
    directory = os.path.dirname(input_file)
    #print("Directory:", directory)
    # Get the filename with extension
    filename = os.path.basename(input_file)
    if not filename.endswith(".mp3"):
        print_err("[-] I could not see an .mp3 extension. You know what you are doing?")
        sys.exit(1)
    #print("Filename:", filename)
    mp3_url_location = base_url + requests.utils.quote(directory) + "/" + requests.utils.quote(filename)
    # Get length of MP3 (really needed or optional?) - and is it really seconds or filesize??
    #podcast_len = get_mp3_length(input_file) # length in seconds
    podcast_len = os.path.getsize(input_file) # filesize in bytes

    # ask chatgpt for a nice description
    ai_description = askChatGPTv2("Gib mir eine zusammenfassung zu folgender datei "+filename)
    
    # STEP 3
    # create the item
    item = PodcastItem(
        filename,
        filename,
        ai_description,
        formatted_datetime,
        mp3_url_location,
        mp3_url_location,
        ai_description,
        "1", # episode
        "full", 
        filename,
        ai_description,
        "no",
        "keywords",
        "@bongoalex",
        mp3_url_location,
        "audio/mpeg", # video/mpeg should work as well for videos - see https://flylib.com/books/en/2.140.1.61/1/
        str(podcast_len)
        )

    # STEP 4 option append to existing rss
    if args.rssfile:
        print(header_content)
        print(current_rss_content)
        print(item.toPodcast())
        print("\n\n  </channel>\n</rss>")

    # STEP 4 option create new rss
    # simply print the resulting XML file like a boss - using print statements!
    if args.headerfile:
        print(header_content)
        print(item.toPodcast())
        print("\n\n  </channel>\n</rss>")

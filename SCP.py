# https://medium.com/analytics-vidhya/web-scraping-with-python-using-beautifulsoup-69b8bc07ff43#:~:text=To%20extract%20the%20raw%20HTML,the%20URL%20path%20we%20passed.&text=The%20way%20requests%20delivers%20the,is%20quite%20messy%20for%20analysis.
# Wikidot SCP foundation database reformat
# Aaron Grissom 8/2/2022
import requests
from bs4 import BeautifulSoup
import sys
import re

# recieve input from user
SCP = input("Which SCP are you trying to access?: \nSCP-") # user inputs scp number
print ("-----------------------")
Series = str(int(int(SCP)/1000+1))

# test input from user
if int(SCP) <= 0 or int(SCP) >= 7000: # all SCP values are between 1 and 6999
        print("Error SCP-" + SCP + " does not exsist")
        sys.exit()

if int(SCP) <= 999: # formating check for URL
    if int(SCP) <= 99:
        SCP = "0" + str(int(SCP))
    if int(SCP) <= 9:
        SCP = "00" + str(int(SCP))

# access wikidot
url_path = ('https://scp-wiki.wikidot.com/scp-'+SCP) # url for SCP the user wants
url_series = ('https://scp-wiki.wikidot.com/scp-series-'+Series) # url for Series the user wants, used to retrieve colloquial name of SCP
html_text = requests.get(url_path).text # raw html code in text from wikidot
series_html = requests.get(url_series).text # raw html code in text from wikidot
soup = BeautifulSoup(html_text,features="html.parser") # Formatting raw html
salad = BeautifulSoup(series_html,features="html.parser") # Formatting raw html
body = soup.find_all('p') # create a bs4.element.ResultSet of the webpage main content
name_list = salad.find_all('li') # create a bs4.element.ResultSet of the series webpage list

# initaliza varables
object_class = ""
item_number = ""

# start of magic!
paragraph = [] # empty list to contain list of strings of content from pages
for text in name_list: # add the colloquial name to the file
    if "SCP-"+SCP in str(text.contents):
        paragraph.append(str(text.contents))

        
add = False; # variable to know when to start and stop adding text to paragraph from page
for text in body: # body is a list of <p></p> in the html page
    string = str(text.contents) # convert text to string type
    if not add and "Item #" in string:
        add = True; # start at Item #
    if not add and "Special Containment Procedures" in string:
        add = True; # start at Special Containment Procedures
    if add and "| SCP-" in string:
        add = False; # stop at navigation
    if add:
        paragraph.append(string)

# paragraph is a list of strings with brackets, need to clean those up "[....]" --> "..."
count = 0
for text in paragraph:
    text = text.replace("[","")
    text = text.replace("]","")
    paragraph[count] = text
    count = count + 1
# reformat the colloquial name, should allways be paragraph 0
paragraph[0] = re.sub(r'<.+?>','', paragraph[0])
paragraph[0] = paragraph[0].replace("' - ","The ")
paragraph[0] = paragraph[0].replace("'","")
paragraph[0] = paragraph[0].replace(",","")
paragraph[0] = paragraph[0].replace("SCP-" + SCP,"")
paragraph[0] = paragraph[0].replace(" The","The")

# reformat/find Item #
count = 0
found = False
while not found:
    if paragraph[count] == paragraph[-1]:
        break
    count = count + 1
    if "Item #" in paragraph[count]:
        found = True
if found:
    paragraph[count] = paragraph[count].replace(",","")
    paragraph[count] = paragraph[count].replace("'","")
    paragraph[count] = paragraph[count].replace("Item #:","")
else:
    item_number = str(soup.find_all('span',{'class':'number'})[1])
    item_number = "SCP-" + re.sub(r'<.+?>', '', item_number)

# reformat/find Object Class
count = 0
found = False
while not found:
    count = count + 1
    if "Object Class" in paragraph[count]:
        found = True
    if paragraph[count] == paragraph[-1]:
        break
if found:
    paragraph[count] = paragraph[count].replace(",","")
    paragraph[count] = paragraph[count].replace("'","")
    paragraph[count] = paragraph[count].replace("Item #:","")
else:
    object_class = str(soup.find_all('div',{'class':'class-text'}))
    object_class = re.sub(r'<.+?>', '', object_class)

#remove unnessesaty ' from text
count = 0
for text in paragraph:
    text = text.replace("</strong>, '","")
    if text[-1] == "'":
        text = text[:-1]
    if text[0] == "'":
        text = text[1:]
    paragraph[count] = text
    count = count + 1
    
#remove <...> from text
count = 0
for text in paragraph:
    if "<strong>" in text:
        text = text.replace("<strong>", "&&")
    text = re.sub(r'<.+?>', '', text)
    paragraph[count] = text
    count = count + 1

#remove extra html junk
count = 0
for text in paragraph:
    text = text.replace("&lt;","")
    text = text.replace("&gt;","")
    text = text.replace("',","")
    text = text.replace(", '","")
    text = text.replace('\\n',"")
    text = text.replace('SCP-'+SCP+',',"")
    text = text.replace('SCP-'+SCP+':,','SCP-'+SCP+':')
    text = text.replace(':, "',':')
    text = text.replace('\\xa0','')
    paragraph[count] = text
    count = count + 1

#remove multiple spaces from text
count = 0
for text in paragraph:
    text = re.sub(' +', ' ',text)
    paragraph[count] = text
    count = count + 1    

# Move into seperate variables
coloquilal_name = paragraph[0]
picture = ""
if item_number == "":
    item_number = paragraph[1]
if object_class == "":
    object_class = paragraph[2]
containment_prosedure = ""
description = ""
other = ""

# find the picture
picture = str(soup.find_all('div',{'class':'scp-image-block block-right'}))
strings = re.findall(r'"(.*?)"', picture)
for text in strings:
    if "http" in text:
        picture = str(text)

        
# reformat variables
item_number = item_number.replace("&& ","")
object_class = object_class.replace("&& ","")

# find Special Containment Procedures
read = False
for text in paragraph:
    if "&&Special Containment Procedures:" in text:
        read = True
    if "&&Description:" in text:
        read = False
    if read:
        containment_prosedure = "\n" + containment_prosedure + text

# reformat containment_prosedure
containment_prosedure = containment_prosedure.replace("&&Special Containment Procedures: ","")
while "\n\n" in containment_prosedure:
    containment_prosedure = containment_prosedure.replace("\n\n","\n")

# find Description
read = False
for text in paragraph:
    if read and "&&" in text:
        read = False
    if "&&Description:" in text:
        read = True
    if read:
        description = "\n" + description + text

# reformat description
description = description.replace("&&Description: ","")
while "\n\n" in description:
    description = description.replace("\n\n","\n")

# find remaining content
read = False
for text in paragraph:
    if not read and "&&" in text:
        if "&&Description:" in text:
            read = False
        elif "&&Special Containment Procedures:" in text:
            read = False
        else:
            read = True
    if read:
        other = "\n" + other + text

# reformat other
while "\n\n" in other:
    other = other.replace("\n\n","\n")
other = other.replace("&&","\n")
if other[0] == "\n":
    other = other[1:]

print("coloquilal_name: " + coloquilal_name)
print("picture: " + picture)
print("item_number: " + item_number)
print("object_class: " + object_class)
print("containment_prosedure:" + containment_prosedure)
print("description :" + description)
print("other :" + other)
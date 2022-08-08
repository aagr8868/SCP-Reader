# https://medium.com/analytics-vidhya/web-scraping-with-python-using-beautifulsoup-69b8bc07ff43#:~:text=To%20extract%20the%20raw%20HTML,the%20URL%20path%20we%20passed.&text=The%20way%20requests%20delivers%20the,is%20quite%20messy%20for%20analysis.
# Wikidot SCP foundation database reformat
# Aaron Grissom 8/2/2022
import requests
from bs4 import BeautifulSoup
import sys
import re

SCP = input("Which SCP are you trying to access?: \nSCP-") # user inputs scp number
print ("-----------------------")
Series = str(int(int(SCP)/1000+1))

if int(SCP) <= 0 or int(SCP) >= 7000: # all SCP values are between 1 and 6999
        print("Error SCP-" + SCP + " does not exsist")
        sys.exit()

if int(SCP) <= 999: # formating check for URL
    if int(SCP) <= 99:
        SCP = "0" + str(int(SCP))
    if int(SCP) <= 9:
        SCP = "00" + str(int(SCP))

url_path = ('https://scp-wiki.wikidot.com/scp-'+SCP) # url for SCP the user wants
url_series = ('https://scp-wiki.wikidot.com/scp-series-'+Series) # url for Series the user wants, used to retrieve colloquial name of SCP
html_text = requests.get(url_path).text # raw html code in text from wikidot
series_html = requests.get(url_series).text # raw html code in text from wikidot
soup = BeautifulSoup(html_text,features="html.parser") # Formatting raw html
salad = BeautifulSoup(series_html,features="html.parser") # Formatting raw html
body = soup.find_all('p') # create a bs4.element.ResultSet of the webpage main content
name_list = salad.find_all('li') # create a bs4.element.ResultSet of the series webpage list

paragraph = [] # empty list to contain list of strings of content from pages
for text in name_list: # add the colloquial name to the file
    if "SCP-"+SCP in str(text.contents):
        paragraph.append(str(text.contents))

        
add = False; # variable to know when to start and stop adding text to paragraph from page
for text in body: # body is a list of <p></p> in the html page
    string = str(text.contents) # convert text to string type
    if not add and "Item #" in string:
        add = True; # start at Item #
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
# reformat the colloquial name
paragraph[0] = re.sub(r'<.+?>','', paragraph[0])
paragraph[0] = paragraph[0].replace("' - ","The ")
paragraph[0] = paragraph[0].replace("'","")
paragraph[0] = paragraph[0].replace(",","")
paragraph[0] = paragraph[0].replace("SCP-" + SCP,"Colloquial name:")

#reformat Item #
paragraph[1] = paragraph[1].replace(",","")
paragraph[1] = paragraph[1].replace("'","")

#reformat Object Class
paragraph[2] = paragraph[2].replace(",","")
paragraph[2] = paragraph[2].replace("'","")

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
        text = text.replace("<strong>", "\n")
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
    paragraph[count] = text
    count = count + 1

#remove multiple spaces from text
count = 0
for text in paragraph:
    text = re.sub(' +', ' ',text)
    paragraph[count] = text
    count = count + 1    
    
for text in paragraph:
    print (text)
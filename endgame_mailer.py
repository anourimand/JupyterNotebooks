# This program will take the box-office gross amount earned data for "Avengers Endgame" and send me an email with the amount earned, and how much the movie must earn to pass Avatar
# (I check this everyday and I'd just rather have it emailed to me)

# Part 1 - scraping the "All time Box Office" Table - following the "Web scraping tables in python" tutorial

import requests  # gets the HTML contents of the website
import lxml.html as lh  # parses the relevant fields
import pandas as pd  # for dataframe for tabling data

import smtplib #used to email the data to my email
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText

web_url = 'https://www.boxofficemojo.com/alltime/world/' #website which contains data to scrape

# create a handle page to handle the contents of the website
page = requests.get(web_url)

# store contents of website in a doc
doc = lh.fromstring(page.content)

#parse data that is stored between <tr> and /<tr> --> this is the location where the info of the data is stored
tr_elements = doc.xpath('//tr')

#The table I am looking for starts at the 4th row 

# Part 2 - take the scraped data and make a dataframe 
# First - make a header
# Since the header of the table does not have the same number of columns as the succeeding data, I will define the header myself
header_array = ['Rank', 'Title', 'Studio', 'Worldwide ($M)', 'Domestic', '%', 'Overseas', '%', 'Year']

#Create empty list
col=[]
i=0
#For each row, store each first element (header) and an empty list
for t in header_array:
    col.append((header_array[i],[])) 
    i = i+1

# Now that the array is made, it is time to populate the data in a pandas dataframe with the top 25 movies in the highest grossing
for j in range(3,28):
    #T is our j'th row
    T=tr_elements[j]
      
    #i is the index of our column
    i=0
    
    #Iterate through each element of the row
    for t in T.iterchildren():
        data=t.text_content()
        #Append the data to the empty list of the i'th column
        col[i][1].append(data)
        #Increment i for the next column
        i+=1

Dict={title:column for (title,column) in col} #generate a dictionary to convert the data collected into a pandas dataframe
df=pd.DataFrame(Dict)

# Part 3 - it is time to generate an HTML file to email out 

header = '''
<html>
    <head>
    <style> 
    .df th {
        padding-top: 12px;
        padding-bottom: 12px;
        text-align: left;
        background-color: #ac00e6;
        color: white;
    }
    .df {
        font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
        border-collapse: collapse;
        width: 100%;
    }
    .df td, .df th {
        border: 1px solid #ddd;
        padding: 8px;
    }
    </style>
    </head>
    <body>
'''
footer = '''
    </body>
</html>
'''

# Write a new HTML file with the collected data from the box office rankings
with open('rankings.html', 'w') as f:
    f.write(header)
    f.write(df.to_html(classes='df'))
    f.write(footer)

# Create convert the HTML file that has been generated to a variable. This variable will be used to create the email
with open('rankings.html', 'r') as f:
    ghtml = f.read()

# Part 4 - make the email and send out
# me == my email address
# you == recipient's email address
me = "-- email address to be sending from --"
you = "-- email address which the data will be sent to --"

# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] = "Box Office Ranking"
msg['From'] = me
msg['To'] = you
text = "What's good?"

# Record the MIME types of both parts - text/plain and text/html.
part1 = MIMEText(text, 'plain')
part2 = MIMEText(ghtml, 'html')

# Attach parts into message container.
# According to RFC 2046, the last part of a multipart message, in this case
# the HTML message, is best and preferred.
msg.attach(part1)
msg.attach(part2)

# Send the message via local SMTP server.
mail = smtplib.SMTP('smtp.gmail.com', 587) # I will be using my Gmail account to send the table
mail.ehlo()
mail.starttls()

while True:
        mail.login('-- username of the email which will be sending --', '-- password --')
        mail.sendmail(me, you, msg.as_string())
        mail.quit()


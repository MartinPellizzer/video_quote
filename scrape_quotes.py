import requests
import json
import csv
import time
import pandas

from bs4 import BeautifulSoup

'''
while True:
    response = requests.get(f'https://zenquotes.io/api/quotes')
    json_data = response.json()

    with open('export.csv', 'a', newline='') as f:
        pass

    quotes = list()
    with open('export.csv', 'r') as f:
        reader = csv.reader(f, delimiter="|")
        for row in reader:
            quotes.append(row[0])

    with open('export.csv', 'a', newline='') as f:
        writer = csv.writer(f, delimiter="|")
        for dic in json_data:
            
            found = False
            for quote in quotes:
                if dic['q'] == quote:
                    print('found')
                    found = True
                    break

            if not found:
                writer.writerow([dic['q'], dic['a'], dic['c']])
    
    time.sleep(60)

quit()

for dic in json_data:
    print(dic['q'])
    for key in dic:
        print(key, ':', dic[key])
'''

params = {
	'q': 'fyodor dostoyevsky'
}

# response = requests.get('https://goodreads.com/quotes/tag/motivational')
# response = requests.get('https://goodreads.com/quotes/search?q=Fyodor+Dostoyevsky')
response = requests.get('https://goodreads.com/quotes/search', params=params)
soup = BeautifulSoup(response.content, 'html.parser')

quotes_text = [q.contents[0].strip() for q in soup.find_all(class_='quoteText')]
quotes_author = [q.getText().strip().replace(',', '') for q in soup.find_all(name='span', class_='authorOrTitle')]

quotes = []
for i in range(len(quotes_text)):
	print(quotes_text[i], quotes_author[i])
	quotes.append([quotes_text[i], quotes_author[i]])

df = pandas.DataFrame(quotes, columns=['quote', 'author'])
df.to_csv('quotes.csv', sep='|', encoding='utf-8', index=False)
print(df)
	
#print(quotes)

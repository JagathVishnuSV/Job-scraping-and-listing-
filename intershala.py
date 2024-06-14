import csv
from bs4 import BeautifulSoup
import requests
import os
import time

def find_internshala_jobs():
    url = 'https://internshala.com/jobs/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    jobs = soup.find_all('div', class_='individual_internship')

    with open('internshala_jobs.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Job Name', 'More Info']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for job in jobs:
            try:
                name = job.find('h3', class_='job-internship-name').text.strip()
                more_info = 'https://internshala.com' + job['data-href']

                writer.writerow({'Job Name': name, 'More Info': more_info})
            except AttributeError:
                continue

if __name__ == '__main__':
    find_internshala_jobs()
    print("Filed saved as intershala_jobs.csv")

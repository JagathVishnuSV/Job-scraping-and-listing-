import csv
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from difflib import get_close_matches
import time
from urllib.robotparser import RobotFileParser

def fetch_webpage(url, headers):
    """Fetches the content of the webpage."""
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Ensure the request was successful
    return response.content

def parse_webpage(content):
    """Parses the webpage content using BeautifulSoup."""
    return BeautifulSoup(content, "html.parser")

def extract_timesjobs_jobs(soup):
    """Extracts job postings from TimesJobs."""
    jobs = soup.find_all('li', class_='clearfix job-bx wht-shd-bx')
    job_data = []
    for job in jobs:
        try:
            company_element = job.find('h3', class_='joblist-comp-name')
            more_info_element = job.header.h2.a
            skills_element = job.find('span', class_='srp-skills')

            company = company_element.text.strip() if company_element else 'N/A'
            more_info = more_info_element['href'] if more_info_element else 'N/A'
            skills = skills_element.text.replace(' ', '').strip() if skills_element else 'N/A'

            job_data.append({'Company': company, 'Skills': skills, 'More Info': more_info})
        except AttributeError as e:
            print(f"Error processing job: {e}")
            continue
    return job_data

def scrape_timesjobs(num_pages, headers):
    """Scrapes TimesJobs job postings from multiple pages."""
    all_job_details = []
    for page in range(1, num_pages + 1):
        URL = f"https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords=internship+computer+science&txtLocation=&luceneResultSize=25&postWeek=60&pDate=Y&sequence={page}"
        if not check_robots_txt(URL):
            print(f"Scraping not allowed for URL: {URL}")
            continue
        webpage_content = fetch_webpage(URL, headers)
        soup = parse_webpage(webpage_content)
        timesjobs_jobs = extract_timesjobs_jobs(soup)
        all_job_details.extend(timesjobs_jobs)
        time.sleep(1)  # Rate limiting
    return all_job_details

def find_timesjobs_jobs_by_skill(skill, num_pages, headers):
    """Finds TimesJobs job postings based on specified skills from multiple pages."""
    all_job_details = []
    for page in range(1, num_pages + 1):
        URL = f"https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords={skill}&txtLocation=&luceneResultSize=25&postWeek=60&pDate=Y&sequence={page}"
        print(f"Fetching page {page}: {URL}")
        if not check_robots_txt(URL):
            print(f"Scraping not allowed for URL: {URL}")
            continue
        webpage_content = fetch_webpage(URL, headers)
        soup = parse_webpage(webpage_content)
        jobs = soup.find_all('li', class_='clearfix job-bx wht-shd-bx')

        for job in jobs:
            try:
                job_published_date = job.find('span', class_='sim-posted').span.text
                if 'few' in job_published_date:
                    company = job.find('h3', class_='joblist-comp-name').text.strip()
                    skills = job.find('span', class_='srp-skills').text.replace(' ', '').strip()
                    more_info = job.header.h2.a['href']
                    print(f"Checking job: {company} with skills: {skills}")
                    if skill.lower() in skills.lower():
                        all_job_details.append({'Company': company, 'Skills': skills, 'More Info': more_info})
            except AttributeError as e:
                print(f"Error processing job: {e}")
                continue
        time.sleep(1)  # Rate limiting

    posts_folder = 'posts'
    if not os.path.exists(posts_folder):
        os.makedirs(posts_folder)

    if all_job_details:
        df = pd.DataFrame(all_job_details)
        df.to_csv(os.path.join(posts_folder, 'timesjobs_jobs.csv'), index=False)
        print('File saved: timesjobs_jobs.csv')
    else:
        print('No jobs found with the specified criteria.')

def find_internshala_jobs(headers):
    url = 'https://internshala.com/jobs/'
    if not check_robots_txt(url):
        print("Scraping not allowed for Internshala")
        return
    response = requests.get(url, headers=headers)
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
            except AttributeError as e:
                print(f"Error processing job: {e}")
                continue
    print("File saved as internshala_jobs.csv")

def suggest_similar_skills(skill, all_skills):
    suggestions = get_close_matches(skill, all_skills, n=5, cutoff=0.7)
    if suggestions:
        print(f"Did you mean: {', '.join(suggestions)}?")

def check_robots_txt(url):
    rp = RobotFileParser()
    rp.set_url('https://www.timesjobs.com/robots.txt')
    rp.read()
    return rp.can_fetch('*', url)

def main():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    all_skills = ["python", "java", "c++", "data science", "machine learning", "artificial intelligence", "deep learning", "sql", "hadoop", "spark", "html", "css", "javascript"]

    while True:
        print("\nMenu:")
        print("1. Scrape and save Internshala jobs")
        print("2. Scrape and save TimesJobs jobs")
        print("3. Find and save TimesJobs jobs by skills")
        print("4. Quit")
        choice = input("Enter your choice: ")

        if choice == '1':
            find_internshala_jobs(headers)

        elif choice == '2':
            num_pages = int(input("Enter the number of pages to scrape from TimesJobs: "))
            job_details = scrape_timesjobs(num_pages, headers)
            df = pd.DataFrame(job_details, columns=['Company', 'Skills', 'More Info'])
            df.to_excel("timesjobs_jobs.xlsx", index=False)
            print("timesjobs_jobs.xlsx saved successfully!")

        elif choice == '3':
            skill = input("Enter a skill you want to search for: ")
            suggest_similar_skills(skill, all_skills)
            num_pages = int(input("Enter the number of pages to scrape from TimesJobs: "))
            find_timesjobs_jobs_by_skill(skill, num_pages, headers)

        elif choice == '4':
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

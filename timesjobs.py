import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_webpage(url):
    """Fetches the content of the webpage."""
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful
    return response.content

def parse_webpage(content):
    """Parses the webpage content using BeautifulSoup."""
    return BeautifulSoup(content, "html.parser")

def extract_timesjobs_jobs(soup):
    """Extracts job postings from TimesJobs."""
    jobs = soup.find_all('li', class_='clearfix job-bx wht-shd-bx')
    return jobs

def extract_job_details_timesjobs(job_element):
    """Extracts job details from a TimesJobs job element."""
    try:
        company_element = job_element.find('h3', class_='joblist-comp-name')
        skills_element = job_element.find('span', class_='srp-skills')
        more_info_element = job_element.header.h2.a

        company = company_element.text.strip() if company_element else 'N/A'
        skills = skills_element.text.strip() if skills_element else 'N/A'
        more_info = more_info_element['href'] if more_info_element else 'N/A'
        
        return company, skills, more_info
    except AttributeError as e:
        print(f"Error extracting details from a TimesJobs job element: {e}")
        return 'N/A', 'N/A', 'N/A'

def scrape_timesjobs(num_pages):
    """Scrapes TimesJobs job postings from multiple pages."""
    all_job_details = []
    for page in range(1, num_pages + 1):
        URL = f"https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords=internship+computer+science&txtLocation=&luceneResultSize=25&postWeek=60&pDate=Y&sequence={page}"
        webpage_content = fetch_webpage(URL)
        soup = parse_webpage(webpage_content)
        timesjobs_jobs = extract_timesjobs_jobs(soup)
        job_details = [extract_job_details_timesjobs(job) for job in timesjobs_jobs]
        all_job_details.extend(job_details)
    return all_job_details

def display_job_details(job_details):
    """Displays job details in a formatted manner."""
    for detail in job_details:
        print(f"{detail}\n")

def find_timesjobs_jobs(unfamiliar_skill):
    html_text = requests.get('https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords=internship+computer+science&txtLocation=').text
    soup = BeautifulSoup(html_text, 'lxml')
    jobs = soup.find_all('li', class_='clearfix job-bx wht-shd-bx')

    posts_folder = 'posts'
    if not os.path.exists(posts_folder):
        os.makedirs(posts_folder)

    job_data = []

    for index, job in enumerate(jobs):
        job_published_date = job.find('span', class_='sim-posted').span.text
        if 'few' in job_published_date:
            company = job.find('h3', class_='joblist-comp-name').text.strip()
            skills = job.find('span', class_='srp-skills').text.replace(' ', '').strip()
            more_info = job.header.h2.a['href']
            if unfamiliar_skill.lower() not in skills.lower(): 
                job_data.append({'Company': company, 'Skills': skills, 'More Info': more_info})

    df = pd.DataFrame(job_data)
    df.to_csv(os.path.join(posts_folder, 'timesjobs_jobs.csv'), index=False)
    print('File saved: timesjobs_jobs.csv')

def main():
    while True:
        print("\nMenu:")
        print("1. List TimesJobs jobs")
        print("2. Scrape and save TimesJobs jobs")
        print("3. Find and save TimesJobs jobs by skills")
        print("4. Quit")
        choice = input("Enter your choice: ")

        if choice == '1':
            num_pages = int(input("Enter the number of pages to scrape: "))
            job_details = scrape_timesjobs(num_pages)
            display_job_details(job_details)

        elif choice == '2':
            num_pages = int(input("Enter the number of pages to scrape: "))
            job_details = scrape_timesjobs(num_pages)
            df = pd.DataFrame(job_details, columns=['Company', 'Skills', 'More Info'])
            df.to_excel("timesjobs_jobs.xlsx", index=False)
            print("TimesJobs jobs saved successfully!")

        elif choice == '3':
            unfamiliar_skill = input("Enter a skill you are unfamiliar with: ")
            find_timesjobs_jobs(unfamiliar_skill)

        elif choice == '4':
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

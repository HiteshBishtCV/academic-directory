#!/usr/bin/env python3
"""
Enhanced Academic Directory - Medical Physics PhD Opportunity Tracker
Features: LinkedIn integration, website testing, comprehensive data collection
"""

import requests
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse
import sqlite3
import schedule
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ProfessorProfile:
    """Professor profile data structure"""
    name: str
    university: str
    department: str
    email: str
    research_areas: List[str]
    linkedin_url: Optional[str] = None
    personal_website: Optional[str] = None
    recent_publications: List[str] = None
    hiring_status: str = "unknown"
    last_updated: str = ""
    
@dataclass
class JobOpportunity:
    """Job opportunity data structure"""
    title: str
    institution: str
    location: str
    application_deadline: Optional[str]
    posted_date: str
    description: str
    requirements: List[str]
    contact_info: str
    url: str
    source: str  # 'university_website', 'linkedin', 'other'
    
class LinkedInScraper:
    """LinkedIn job and profile scraper"""
    
    def __init__(self, headless: bool = True):
        self.driver = None
        self.headless = headless
        self.setup_driver()
        
    def setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            
    def search_phd_positions(self, keywords: List[str], location: str = "") -> List[JobOpportunity]:
        """Search for PhD positions on LinkedIn"""
        opportunities = []
        
        if not self.driver:
            return opportunities
            
        try:
            for keyword in keywords:
                search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}%20PhD&location={location}&f_TPR=r86400"
                self.driver.get(search_url)
                time.sleep(3)
                
                # Scroll to load more jobs
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".job-search-card")
                
                for card in job_cards[:10]:  # Limit to first 10 results
                    try:
                        title = card.find_element(By.CSS_SELECTOR, ".base-search-card__title").text
                        company = card.find_element(By.CSS_SELECTOR, ".base-search-card__subtitle").text
                        location_elem = card.find_element(By.CSS_SELECTOR, ".job-search-card__location")
                        job_location = location_elem.text if location_elem else ""
                        
                        link = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                        
                        # Get job details
                        job_details = self.get_job_details(link)
                        
                        opportunity = JobOpportunity(
                            title=title,
                            institution=company,
                            location=job_location,
                            application_deadline=None,
                            posted_date=datetime.now().strftime("%Y-%m-%d"),
                            description=job_details.get("description", ""),
                            requirements=job_details.get("requirements", []),
                            contact_info="",
                            url=link,
                            source="linkedin"
                        )
                        
                        opportunities.append(opportunity)
                        
                    except Exception as e:
                        logger.warning(f"Error processing job card: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"LinkedIn search failed: {e}")
            
        return opportunities
    
    def get_job_details(self, job_url: str) -> Dict:
        """Get detailed job information"""
        details = {"description": "", "requirements": []}
        
        try:
            self.driver.get(job_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".show-more-less-html__markup"))
            )
            
            description_elem = self.driver.find_element(By.CSS_SELECTOR, ".show-more-less-html__markup")
            details["description"] = description_elem.text
            
            # Extract requirements from description
            requirements = []
            desc_lower = details["description"].lower()
            if "phd" in desc_lower or "doctorate" in desc_lower:
                requirements.append("PhD or equivalent degree")
            if "experience" in desc_lower:
                requirements.append("Relevant research experience")
                
            details["requirements"] = requirements
            
        except Exception as e:
            logger.warning(f"Could not get job details for {job_url}: {e}")
            
        return details
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

class WebsiteTester:
    """Test university websites for accessibility and job postings"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def test_website_accessibility(self, url: str) -> Dict:
        """Test if a website is accessible and responsive"""
        result = {
            "url": url,
            "accessible": False,
            "response_time": None,
            "status_code": None,
            "has_job_section": False,
            "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            start_time = time.time()
            response = self.session.get(url, timeout=10)
            end_time = time.time()
            
            result["response_time"] = round(end_time - start_time, 2)
            result["status_code"] = response.status_code
            result["accessible"] = response.status_code == 200
            
            if result["accessible"]:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Check for job/career sections
                job_keywords = ['job', 'career', 'position', 'opening', 'vacancy', 'phd', 'postdoc']
                page_text = soup.get_text().lower()
                
                result["has_job_section"] = any(keyword in page_text for keyword in job_keywords)
                
        except Exception as e:
            logger.error(f"Error testing website {url}: {e}")
            
        return result
    
    def find_job_pages(self, base_url: str) -> List[str]:
        """Find job/career pages on a university website"""
        job_pages = []
        
        try:
            response = self.session.get(base_url, timeout=10)
            if response.status_code != 200:
                return job_pages
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for job-related links
            job_patterns = [
                r'job', r'career', r'position', r'opening', r'vacancy', 
                r'phd', r'postdoc', r'graduate', r'student'
            ]
            
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                link_text = link.get_text().lower()
                
                if any(re.search(pattern, link_text) for pattern in job_patterns):
                    full_url = urljoin(base_url, href)
                    if full_url not in job_pages:
                        job_pages.append(full_url)
                        
        except Exception as e:
            logger.error(f"Error finding job pages for {base_url}: {e}")
            
        return job_pages[:5]  # Limit to 5 job pages per site

class UniversityJobScraper:
    """Scrape job postings from university websites"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_psi_jobs(self) -> List[JobOpportunity]:
        """Scrape jobs from PSI (Paul Scherrer Institute)"""
        opportunities = []
        base_url = "https://www.psi.ch/en/hr/job-opportunities"
        
        try:
            response = self.session.get(base_url)
            if response.status_code != 200:
                return opportunities
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job listings
            job_links = soup.find_all('a', href=re.compile(r'/job-opportunities/\d+'))
            
            for link in job_links[:10]:  # Limit to 10 jobs
                job_url = urljoin(base_url, link.get('href'))
                job_title = link.get_text().strip()
                
                if 'phd' in job_title.lower() or 'student' in job_title.lower():
                    opportunity = JobOpportunity(
                        title=job_title,
                        institution="Paul Scherrer Institute",
                        location="Switzerland",
                        application_deadline=None,
                        posted_date=datetime.now().strftime("%Y-%m-%d"),
                        description="",
                        requirements=[],
                        contact_info="",
                        url=job_url,
                        source="university_website"
                    )
                    opportunities.append(opportunity)
                    
        except Exception as e:
            logger.error(f"Error scraping PSI jobs: {e}")
            
        return opportunities
    
    def scrape_generic_university(self, university_name: str, job_page_url: str) -> List[JobOpportunity]:
        """Generic university job scraper"""
        opportunities = []
        
        try:
            response = self.session.get(job_page_url)
            if response.status_code != 200:
                return opportunities
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for PhD-related postings
            phd_keywords = ['phd', 'doctorate', 'doctoral', 'graduate student', 'research assistant']
            
            for element in soup.find_all(['a', 'div', 'span']):
                text = element.get_text().lower()
                
                if any(keyword in text for keyword in phd_keywords):
                    if element.name == 'a' and element.get('href'):
                        url = urljoin(job_page_url, element.get('href'))
                        
                        opportunity = JobOpportunity(
                            title=element.get_text().strip(),
                            institution=university_name,
                            location="",
                            application_deadline=None,
                            posted_date=datetime.now().strftime("%Y-%m-%d"),
                            description="",
                            requirements=[],
                            contact_info="",
                            url=url,
                            source="university_website"
                        )
                        opportunities.append(opportunity)
                        
        except Exception as e:
            logger.error(f"Error scraping {university_name}: {e}")
            
        return opportunities

class DatabaseManager:
    """Manage SQLite database for storing opportunities and profiles"""
    
    def __init__(self, db_path: str = "academic_directory.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Professors table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS professors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    university TEXT NOT NULL,
                    department TEXT,
                    email TEXT,
                    research_areas TEXT,
                    linkedin_url TEXT,
                    personal_website TEXT,
                    recent_publications TEXT,
                    hiring_status TEXT,
                    last_updated TEXT,
                    UNIQUE(name, university)
                )
            ''')
            
            # Job opportunities table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    institution TEXT NOT NULL,
                    location TEXT,
                    application_deadline TEXT,
                    posted_date TEXT,
                    description TEXT,
                    requirements TEXT,
                    contact_info TEXT,
                    url TEXT UNIQUE,
                    source TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Website monitoring table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS website_monitoring (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE,
                    accessible BOOLEAN,
                    response_time REAL,
                    status_code INTEGER,
                    has_job_section BOOLEAN,
                    last_checked TEXT
                )
            ''')
            
            conn.commit()
    
    def save_opportunities(self, opportunities: List[JobOpportunity]):
        """Save job opportunities to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for opp in opportunities:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO job_opportunities 
                        (title, institution, location, application_deadline, posted_date, 
                         description, requirements, contact_info, url, source)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        opp.title, opp.institution, opp.location, opp.application_deadline,
                        opp.posted_date, opp.description, json.dumps(opp.requirements),
                        opp.contact_info, opp.url, opp.source
                    ))
                except sqlite3.IntegrityError:
                    logger.info(f"Opportunity already exists: {opp.title}")
                    
            conn.commit()
    
    def save_website_test(self, test_result: Dict):
        """Save website test result"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO website_monitoring 
                (url, accessible, response_time, status_code, has_job_section, last_checked)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                test_result["url"], test_result["accessible"], test_result["response_time"],
                test_result["status_code"], test_result["has_job_section"], test_result["last_checked"]
            ))
            
            conn.commit()

class EnhancedAcademicTracker:
    """Main tracker class with enhanced features"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.linkedin_scraper = LinkedInScraper()
        self.website_tester = WebsiteTester()
        self.university_scraper = UniversityJobScraper()
        
        # University websites to monitor
        self.universities = {
            "Paul Scherrer Institute": "https://www.psi.ch/en/hr/job-opportunities",
            "ETH Zurich": "https://jobs.ethz.ch/",
            "CERN": "https://careers.cern/",
            "University of Pennsylvania": "https://www.upenn.edu/careers/",
            "Stanford University": "https://jobs.stanford.edu/",
            "MIT": "https://careers.mit.edu/",
            "Harvard University": "https://careers.harvard.edu/",
            "University of California, Berkeley": "https://jobs.berkeley.edu/",
            "University of Michigan": "https://careers.umich.edu/",
            "Johns Hopkins University": "https://jobs.jhu.edu/"
        }
    
    def run_full_scan(self):
        """Run complete scan of all sources"""
        logger.info("Starting full scan...")
        
        # Test all university websites
        self.test_all_websites()
        
        # Scrape LinkedIn
        self.scrape_linkedin_jobs()
        
        # Scrape university websites
        self.scrape_university_jobs()
        
        logger.info("Full scan completed!")
    
    def test_all_websites(self):
        """Test accessibility of all university websites"""
        logger.info("Testing website accessibility...")
        
        for university, url in self.universities.items():
            logger.info(f"Testing {university}...")
            result = self.website_tester.test_website_accessibility(url)
            self.db.save_website_test(result)
            time.sleep(1)  # Be respectful
    
    def scrape_linkedin_jobs(self):
        """Scrape LinkedIn for PhD opportunities"""
        logger.info("Scraping LinkedIn jobs...")
        
        keywords = [
            "Medical Physics PhD", "Radiation Physics PhD", "Medical Imaging PhD",
            "Radiotherapy PhD", "Nuclear Medicine PhD", "Health Physics PhD"
        ]
        
        opportunities = self.linkedin_scraper.search_phd_positions(keywords)
        self.db.save_opportunities(opportunities)
        
        logger.info(f"Found {len(opportunities)} LinkedIn opportunities")
    
    def scrape_university_jobs(self):
        """Scrape university websites for jobs"""
        logger.info("Scraping university websites...")
        
        all_opportunities = []
        
        # Special handling for PSI
        psi_jobs = self.university_scraper.scrape_psi_jobs()
        all_opportunities.extend(psi_jobs)
        
        # Generic scraping for other universities
        for university, url in self.universities.items():
            if university != "Paul Scherrer Institute":
                job_pages = self.website_tester.find_job_pages(url)
                for job_page in job_pages:
                    opportunities = self.university_scraper.scrape_generic_university(university, job_page)
                    all_opportunities.extend(opportunities)
                    time.sleep(2)  # Be respectful
        
        self.db.save_opportunities(all_opportunities)
        logger.info(f"Found {len(all_opportunities)} university opportunities")
    
    def generate_report(self) -> str:
        """Generate summary report"""
        with sqlite3.connect(self.db.db_path) as conn:
            # Get opportunity counts
            opp_df = pd.read_sql_query('''
                SELECT source, COUNT(*) as count 
                FROM job_opportunities 
                GROUP BY source
            ''', conn)
            
            # Get website status
            website_df = pd.read_sql_query('''
                SELECT url, accessible, response_time, has_job_section
                FROM website_monitoring
                ORDER BY response_time
            ''', conn)
            
            # Get recent opportunities
            recent_df = pd.read_sql_query('''
                SELECT title, institution, posted_date, url
                FROM job_opportunities
                WHERE posted_date >= date('now', '-7 days')
                ORDER BY posted_date DESC
                LIMIT 10
            ''', conn)
        
        report = f"""
# Academic Directory Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Opportunity Summary
"""
        
        for _, row in opp_df.iterrows():
            report += f"- {row['source']}: {row['count']} opportunities\n"
        
        report += "\n## Website Status\n"
        for _, row in website_df.iterrows():
            status = "✅" if row['accessible'] else "❌"
            jobs = "📋" if row['has_job_section'] else "❓"
            report += f"- {status} {jobs} {row['url']} ({row['response_time']}s)\n"
        
        report += "\n## Recent Opportunities\n"
        for _, row in recent_df.iterrows():
            report += f"- **{row['title']}** at {row['institution']} ({row['posted_date']})\n"
            report += f"  {row['url']}\n\n"
        
        return report
    
    def cleanup(self):
        """Clean up resources"""
        self.linkedin_scraper.close()

def main():
    """Main function to run the enhanced tracker"""
    tracker = EnhancedAcademicTracker()
    
    try:
        # Run initial scan
        tracker.run_full_scan()
        
        # Generate and save report
        report = tracker.generate_report()
        
        with open("academic_report.md", "w") as f:
            f.write(report)
        
        print("Report generated: academic_report.md")
        print("\nReport preview:")
        print("=" * 50)
        print(report[:1000] + "..." if len(report) > 1000 else report)
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error running tracker: {e}")
    finally:
        tracker.cleanup()

if __name__ == "__main__":
    main()

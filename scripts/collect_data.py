#!/usr/bin/env python3
"""
Academic Directory Data Collector
Simple version for beginners
"""

import sqlite3
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import time
import os

class AcademicCollector:
    def __init__(self):
        self.db_name = "academic_directory.db"
        self.setup_database()
    
    def setup_database(self):
        """Create database tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Create professors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS professors (
                id INTEGER PRIMARY KEY,
                name TEXT,
                university TEXT,
                email TEXT,
                title TEXT,
                h_index INTEGER DEFAULT 0,
                created_date TEXT
            )
        """)
        
        # Create postings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS postings (
                id INTEGER PRIMARY KEY,
                professor_name TEXT,
                position_type TEXT,
                posted_date TEXT,
                year INTEGER,
                month INTEGER
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Database setup complete")
    
    def add_sample_data(self):
        """Add sample data for testing"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Sample professors
        professors = [
            ("Dr. John Smith", "Stanford University", "jsmith@stanford.edu", "Professor", 45),
            ("Dr. Jane Doe", "MD Anderson", "jdoe@mdanderson.org", "Associate Professor", 38),
            ("Dr. Bob Johnson", "Johns Hopkins", "bjohnson@jhu.edu", "Professor", 42),
            ("Dr. Alice Brown", "UCSF", "abrown@ucsf.edu", "Assistant Professor", 35),
            ("Dr. Charlie Wilson", "Mayo Clinic", "cwilson@mayo.edu", "Professor", 41),
            ("Dr. Sarah Chen", "MIT", "schen@mit.edu", "Professor", 39),
            ("Dr. Michael Rodriguez", "UCLA", "mrodriguez@ucla.edu", "Associate Professor", 33)
        ]
        
        # Sample postings
        postings = [
            ("Dr. John Smith", "PhD", "2023-09-15", 2023, 9),
            ("Dr. Jane Doe", "Postdoc", "2023-10-01", 2023, 10),
            ("Dr. Bob Johnson", "PhD", "2024-01-15", 2024, 1),
            ("Dr. Alice Brown", "PhD", "2024-02-01", 2024, 2),
            ("Dr. Charlie Wilson", "Postdoc", "2024-03-15", 2024, 3),
            ("Dr. Sarah Chen", "PhD", "2023-08-20", 2023, 8),
            ("Dr. Michael Rodriguez", "Research Assistant", "2024-04-10", 2024, 4)
        ]
        
        # Insert professors
        for prof in professors:
            cursor.execute("""
                INSERT OR REPLACE INTO professors 
                (name, university, email, title, h_index, created_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, prof + (datetime.now().isoformat(),))
        
        # Insert postings
        for posting in postings:
            cursor.execute("""
                INSERT OR REPLACE INTO postings 
                (professor_name, position_type, posted_date, year, month)
                VALUES (?, ?, ?, ?, ?)
            """, posting)
        
        conn.commit()
        conn.close()
        print(f"✅ Added {len(professors)} professors and {len(postings)} postings")
    
    def run_collection(self):
        """Main collection function"""
        print("🚀 Starting data collection...")
        self.add_sample_data()
        print("✅ Data collection complete!")

if __name__ == "__main__":
    collector = AcademicCollector()
    collector.run_collection()

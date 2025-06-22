#!/usr/bin/env python3
"""
Setup script for Enhanced Academic Directory
"""

import os
import subprocess
import sys
import json
from pathlib import Path

def create_directory_structure():
    """Create necessary directories"""
    directories = [
        "data",
        "logs", 
        "docs",
        "docs/api",
        "scripts",
        "web",
        "tests"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_config_files():
    """Create configuration files"""
    
    # Create config.yaml
    config_content = """
database:
  path: "data/academic_directory.db"
  backup_interval: 24

scraping:
  delay_between_requests: 2
  max_retries: 3
  timeout: 10
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

linkedin:
  enabled: true
  headless: true
  max_results_per_search: 10

universities:
  "Paul Scherrer Institute":
    url: "https://www.psi.ch/en/hr/job-opportunities"
    country: "Switzerland"
  "ETH Zurich":
    url: "https://jobs.ethz.ch/"
    country: "Switzerland"
  "MIT":
    url: "https://careers.mit.edu/"
    country: "USA"
  "Stanford University":
    url: "https://jobs.stanford.edu/"
    country: "USA"

monitoring:
  check_interval: 6
  website_timeout: 10
"""
    
    with open("config.yaml", "w") as f:
        f.write(config_content)
    print("✅ Created config.yaml")
    
    # Create .env file
    env_content = """
# LinkedIn credentials (optional, for enhanced scraping)
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password

# Email notifications (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
NOTIFICATION_EMAIL=recipient@example.com

# GitHub Pages URL
GITHUB_PAGES_URL=https://HiteshBishtCV.github.io/academic-directory/
"""
    
    with open(".env.example", "w") as f:
        f.write(env_content)
    print("✅ Created .env.example")

def create_requirements_file():
    """Create requirements.txt"""
    requirements = """
requests>=2.31.0
beautifulsoup4>=4.12.0
selenium>=4.15.0
pandas>=2.0.0
schedule>=1.2.0
lxml>=4.9.0
webdriver-manager>=4.0.0
pyyaml>=6.0
python-dotenv>=1.0.0
feedparser>=6.0.10
jinja2>=3.1.0
plotly>=5.17.0
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    print("✅ Created requirements.txt")

def create_github_workflow():
    """Create GitHub Actions workflow"""
    workflow_dir = Path(".github/workflows")
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_content = """
name: Update Academic Directory

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  update-data:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install Chrome
      uses: browser-actions/setup-chrome@latest
      
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Run data collection
      run: |
        python enhanced_academic_tracker.py
        
    - name: Generate web report
      run: |
        python web_report_generator.py
        
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./docs
"""
    
    with open(workflow_dir / "update-data.yml", "w") as f:
        f.write(workflow_content)
    print("✅ Created GitHub Actions workflow")

def create_readme():
    """Create comprehensive README"""
    readme_content = """
# 🎓 Enhanced Academic Directory

An intelligent tracker for Medical Physics PhD opportunities with LinkedIn integration, website monitoring, and real-time updates.

## ✨ Features

- **🔍 LinkedIn Integration**: Automatically scrape PhD positions from LinkedIn
- **🌐 Website Monitoring**: Test university websites for accessibility and job postings
- **📊 Interactive Dashboard**: Real-time web interface with charts and filtering
- **🤖 Automated Updates**: GitHub Actions update data every 6 hours
- **📡 API Endpoints**: JSON APIs for external integrations
- **📰 RSS Feed**: Subscribe to new opportunities
- **🎯 Smart Filtering**: Filter by institution, source, and keywords
- **📱 Mobile Responsive**: Works on all devices

## 🏛️ Supported Institutions

- Paul Scherrer Institute (Switzerland)
- ETH Zurich (Switzerland)
- CERN (Switzerland)
- MIT (USA)
- Stanford University (USA)
- Harvard University (USA)
- University of Pennsylvania (USA)
- Johns Hopkins University (USA)
- University of Michigan (USA)
- And many more...

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Chrome browser (for web scraping)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/HiteshBishtCV/academic-directory.git
   cd academic-directory
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure settings** (optional)
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Run initial data collection**
   ```bash
   python enhanced_academic_tracker.py
   ```

6. **Generate web dashboard**
   ```bash
   python web_report_generator.py
   ```

7. **View the dashboard**
   ```bash
   # Open docs/index.html in your browser
   # Or serve locally:
   python -m http.server 8000 --directory docs
   ```

## 📖 Usage

### Manual Data Collection
```bash
# Run full scan (LinkedIn + Universities + Website testing)
python enhanced_academic_tracker.py

# Generate reports
python web_report_generator.py
```

### Automated Updates
The system automatically updates every 6 hours via GitHub Actions when deployed.

### API Usage
Access structured data via API endpoints:

- **All Opportunities**: `/api/opportunities.json`
- **Summary Stats**: `/api/summary.json`
- **Website Status**: `/api/monitoring.json`

### RSS Feed
Subscribe to new opportunities: `/feed.xml`

## 🔧 Configuration

Edit `config.yaml` to customize:

```yaml
scraping:
  delay_between_requests: 2  # Be respectful to websites
  max_retries: 3
  timeout: 10

linkedin:
  enabled: true
  headless: true
  max_results_per_search: 10

universities:
  "Your University":
    url: "https://jobs.university.edu/"
    country: "Country"
```

## 📊 Dashboard Features

### Real-time Statistics
- Total opportunities tracked
- New positions this month
- Active data sources
- Website monitoring status

### Interactive Charts
- Opportunities by source (LinkedIn vs University websites)
- Top hiring institutions
- Trends over time

### Advanced Filtering
- Search by keywords
- Filter by institution
- Filter by source
- Date range selection

### Mobile-First Design
- Responsive layout
- Touch-friendly interface
- Fast loading times

## 🔬 Data Sources

### LinkedIn Integration
- Automated job search using Selenium
- Keyword-based filtering for PhD positions
- Respect rate limits and ToS

### University Websites
- Direct scraping of career pages
- Custom parsers for major institutions
- Fallback generic scrapers

### Website Monitoring
- Accessibility testing
- Response time monitoring
- Job section detection
- Automated health checks

## 🚀 Deployment

### GitHub Pages (Recommended)
1. Enable GitHub Pages in repository settings
2. Set source to "GitHub Actions"
3. Push changes to trigger automatic deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f academic-tracker
```

### Manual Deployment
```bash
# Set up cron job for regular updates
crontab -e
# Add: 0 */6 * * * cd /path/to/academic-directory && python enhanced_academic_tracker.py && python web_report_generator.py
```

## 🧪 Testing

```bash
# Run basic tests
python -m pytest tests/

# Test specific components
python tests/test_linkedin_scraper.py
python tests/test_website_monitoring.py
```

## 📈 Monitoring & Analytics

### Dashboard Metrics
- Opportunity discovery rate
- Website uptime statistics
- Data source performance
- User engagement (if hosted publicly)

### Alerts & Notifications
- Email notifications for new opportunities
- Website downtime alerts
- Error reporting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Adding New Universities
1. Add to `config.yaml` under `universities`
2. Create custom scraper if needed in `enhanced_academic_tracker.py`
3. Test with `python tests/test_new_university.py`

### Improving Scrapers
- Respect robots.txt
- Add appropriate delays
- Handle errors gracefully
- Update user agents regularly

## 🐛 Troubleshooting

### Common Issues

**ChromeDriver Issues**
```bash
# Update ChromeDriver
pip install --upgrade webdriver-manager
```

**Permission Errors**
```bash
# Fix file permissions
chmod +x enhanced_academic_tracker.py
chmod +x web_report_generator.py
```

**Database Locked**
```bash
# Reset database
rm data/academic_directory.db
python enhanced_academic_tracker.py
```

**LinkedIn Scraping Blocked**
- Use VPN or proxy
- Increase delays between requests
- Update user agent strings
- Consider using LinkedIn API (requires approval)

### Performance Optimization

**Large Datasets**
- Enable database indexing
- Implement pagination
- Use background processing

**Memory Usage**
- Process data in chunks
- Clear browser cache regularly
- Optimize database queries

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Claude AI assistance
- Inspired by the academic job market challenges
- Thanks to the open-source community

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/HiteshBishtCV/academic-directory/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/HiteshBishtCV/academic-directory/discussions)
- 📧 **Contact**: [Your Email]

## 🔮 Roadmap

- [ ] Machine learning for opportunity scoring
- [ ] Integration with academic social networks
- [ ] Mobile app development
- [ ] Advanced analytics and insights
- [ ] Multi-language support
- [ ] Integration with calendar applications
- [ ] Automated application tracking

---

⭐ **Star this repository if it helps you find your dream PhD position!**

📊 **Live Dashboard**: [https://HiteshBishtCV.github.io/academic-directory/](https://HiteshBishtCV.github.io/academic-directory/)
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    print("✅ Created comprehensive README.md")

def create_test_files():
    """Create basic test files"""
    test_dir = Path("tests")
    
    # Basic test file
    test_content = """
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from enhanced_academic_tracker import WebsiteTester, DatabaseManager

class TestWebsiteTester(unittest.TestCase):
    def setUp(self):
        self.tester = WebsiteTester()
    
    def test_website_accessibility(self):
        result = self.tester.test_website_accessibility("https://httpbin.org/status/200")
        self.assertTrue(result['accessible'])
        self.assertEqual(result['status_code'], 200)
    
    def test_website_inaccessible(self):
        result = self.tester.test_website_accessibility("https://httpbin.org/status/404")
        self.assertFalse(result['accessible'])
        self.assertEqual(result['status_code'], 404)

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseManager(":memory:")  # Use in-memory database
    
    def test_database_initialization(self):
        # Test that tables are created
        with self.db.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['professors', 'job_opportunities', 'website_monitoring']
            for table in expected_tables:
                self.assertIn(table, tables)

if __name__ == '__main__':
    unittest.main()
"""
    
    with open(test_dir / "test_basic.py", "w") as f:
        f.write(test_content)
    print("✅ Created basic test files")

def install_dependencies():
    """Install Python dependencies"""
    try:
        print("📦 Installing Python dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    return True

def setup_chromedriver():
    """Setup ChromeDriver for Selenium"""
    try:
        print("🌐 Setting up ChromeDriver...")
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium import webdriver
        
        # This will download ChromeDriver if needed
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver ready at: {driver_path}")
        
        # Test basic functionality
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        driver.get("https://httpbin.org/status/200")
        print("✅ ChromeDriver test successful")
        driver.quit()
        
    except Exception as e:
        print(f"❌ ChromeDriver setup failed: {e}")
        print("💡 Try: pip install webdriver-manager")
        return False
    return True

def run_initial_test():
    """Run initial test to verify setup"""
    try:
        print("🧪 Running initial tests...")
        
        # Test database creation
        from enhanced_academic_tracker import DatabaseManager
        db = DatabaseManager("data/test.db")
        print("✅ Database test passed")
        
        # Test website monitoring
        from enhanced_academic_tracker import WebsiteTester
        tester = WebsiteTester()
        result = tester.test_website_accessibility("https://httpbin.org/status/200")
        if result['accessible']:
            print("✅ Website testing passed")
        else:
            print("❌ Website testing failed")
            
        # Clean up test database
        os.remove("data/test.db")
        
    except Exception as e:
        print(f"❌ Initial test failed: {e}")
        return False
    return True

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("\n1. 🔧 Configure (Optional):")
    print("   - Copy .env.example to .env")
    print("   - Edit config.yaml for your needs")
    print("\n2. 🚀 Run Data Collection:")
    print("   python enhanced_academic_tracker.py")
    print("\n3. 📊 Generate Dashboard:")
    print("   python web_report_generator.py")
    print("\n4. 🌐 View Results:")
    print("   Open docs/index.html in your browser")
    print("   Or run: python -m http.server 8000 --directory docs")
    print("\n5. 🤖 Enable Auto-Updates:")
    print("   - Push to GitHub")
    print("   - Enable GitHub Pages")
    print("   - Updates will run every 6 hours")
    print("\n📚 Documentation:")
    print("   - README.md: Complete guide")
    print("   - config.yaml: Configuration options")
    print("   - tests/: Run tests with 'python -m pytest'")
    print("\n🆘 Need Help?")
    print("   - Check README.md for troubleshooting")
    print("   - Open GitHub issue for bugs")
    print("   - View live example: https://HiteshBishtCV.github.io/academic-directory/")
    print("\n" + "="*60)

def main():
    """Main setup function"""
    print("🎓 Enhanced Academic Directory Setup")
    print("="*40)
    
    try:
        # Create directory structure
        print("\n📁 Creating directories...")
        create_directory_structure()
        
        # Create configuration files
        print("\n⚙️ Creating configuration files...")
        create_config_files()
        create_requirements_file()
        create_github_workflow()
        create_readme()
        create_test_files()
        
        # Install dependencies
        print("\n📦 Installing dependencies...")
        if not install_dependencies():
            print("⚠️ Manual installation required: pip install -r requirements.txt")
        
        # Setup ChromeDriver
        print("\n🌐 Setting up web scraping...")
        if not setup_chromedriver():
            print("⚠️ ChromeDriver setup failed - LinkedIn scraping may not work")
        
        # Run initial tests
        print("\n🧪 Running initial tests...")
        if not run_initial_test():
            print("⚠️ Some tests failed - check configuration")
        
        # Print next steps
        print_next_steps()
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("📧 Please check the error and try again")
        return False
    
    return True

if __name__ == "__main__":
    main()

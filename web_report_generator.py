#!/usr/bin/env python3
"""
Enhanced Web Report Generator for Academic Directory
Creates interactive HTML dashboard with charts and filtering
"""

import sqlite3
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import os

class WebReportGenerator:
    """Generate interactive web dashboard"""
    
    def __init__(self, db_path: str = "academic_directory.db"):
        self.db_path = db_path
        self.output_dir = "docs"  # GitHub Pages directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    def get_data_summary(self) -> Dict:
        """Get summary statistics from database"""
        with sqlite3.connect(self.db_path) as conn:
            # Total opportunities
            total_jobs = pd.read_sql_query(
                "SELECT COUNT(*) as count FROM job_opportunities", conn
            ).iloc[0]['count']
            
            # Jobs by source
            jobs_by_source = pd.read_sql_query("""
                SELECT source, COUNT(*) as count 
                FROM job_opportunities 
                GROUP BY source
            """, conn)
            
            # Jobs by institution
            jobs_by_institution = pd.read_sql_query("""
                SELECT institution, COUNT(*) as count 
                FROM job_opportunities 
                GROUP BY institution 
                ORDER BY count DESC
                LIMIT 10
            """, conn)
            
            # Recent jobs (last 30 days)
            recent_jobs = pd.read_sql_query("""
                SELECT COUNT(*) as count 
                FROM job_opportunities 
                WHERE posted_date >= date('now', '-30 days')
            """, conn).iloc[0]['count']
            
            # Website status
            website_status = pd.read_sql_query("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN accessible = 1 THEN 1 ELSE 0 END) as accessible,
                    AVG(response_time) as avg_response_time
                FROM website_monitoring
            """, conn)
            
            return {
                'total_jobs': total_jobs,
                'recent_jobs': recent_jobs,
                'jobs_by_source': jobs_by_source.to_dict('records'),
                'jobs_by_institution': jobs_by_institution.to_dict('records'),
                'website_stats': website_status.to_dict('records')[0] if not website_status.empty else {}
            }
    
    def get_recent_opportunities(self, limit: int = 20) -> List[Dict]:
        """Get recent job opportunities"""
        with sqlite3.connect(self.db_path) as conn:
            recent_df = pd.read_sql_query("""
                SELECT title, institution, location, posted_date, url, source
                FROM job_opportunities
                ORDER BY posted_date DESC
                LIMIT ?
            """, conn, params=(limit,))
            
            return recent_df.to_dict('records')
    
    def get_website_monitoring_data(self) -> List[Dict]:
        """Get website monitoring results"""
        with sqlite3.connect(self.db_path) as conn:
            monitoring_df = pd.read_sql_query("""
                SELECT url, accessible, response_time, has_job_section, last_checked
                FROM website_monitoring
                ORDER BY response_time
            """, conn)
            
            return monitoring_df.to_dict('records')
    
    def generate_html_dashboard(self):
        """Generate the main HTML dashboard"""
        data_summary = self.get_data_summary()
        recent_opportunities = self.get_recent_opportunities()
        website_data = self.get_website_monitoring_data()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Academic Directory - Medical Physics PhD Opportunities</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/date-fns@2.29.0/index.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
            padding: 40px 0;
        }}
        
        .header h1 {{
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-number {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .stat-label {{
            font-size: 1rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}
        
        .chart-container {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .chart-title {{
            font-size: 1.5rem;
            margin-bottom: 20px;
            color: #333;
            text-align: center;
        }}
        
        .opportunities-section {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            margin-bottom: 30px;
        }}
        
        .section-title {{
            font-size: 2rem;
            margin-bottom: 25px;
            color: #333;
            text-align: center;
        }}
        
        .filters {{
            display: flex;
            gap: 15px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }}
        
        .filter-input {{
            padding: 10px 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1rem;
            min-width: 200px;
            transition: border-color 0.3s ease;
        }}
        
        .filter-input:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        .opportunities-grid {{
            display: grid;
            gap: 20px;
        }}
        
        .opportunity-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #667eea;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        .opportunity-card:hover {{
            transform: translateX(5px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .opp-title {{
            font-size: 1.3rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .opp-institution {{
            font-size: 1.1rem;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .opp-meta {{
            display: flex;
            gap: 15px;
            margin: 10px 0;
            font-size: 0.9rem;
            color: #666;
        }}
        
        .opp-tag {{
            background: #667eea;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
        }}
        
        .opp-link {{
            display: inline-block;
            margin-top: 10px;
            color: #667eea;
            text-decoration: none;
            font-weight: bold;
        }}
        
        .opp-link:hover {{
            text-decoration: underline;
        }}
        
        .monitoring-section {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .monitoring-grid {{
            display: grid;
            gap: 15px;
        }}
        
        .monitoring-item {{
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        .status-indicator {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}
        
        .status-good {{ background: #28a745; }}
        .status-warning {{ background: #ffc107; }}
        .status-error {{ background: #dc3545; }}
        
        .monitoring-url {{
            flex: 1;
            font-weight: bold;
        }}
        
        .monitoring-stats {{
            display: flex;
            gap: 15px;
            font-size: 0.9rem;
            color: #666;
        }}
        
        .footer {{
            text-align: center;
            color: rgba(255,255,255,0.8);
            margin-top: 40px;
            padding: 20px;
        }}
        
        @media (max-width: 768px) {{
            .dashboard-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .filters {{
                flex-direction: column;
            }}
            
            .filter-input {{
                min-width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 Academic Directory</h1>
            <p>Medical Physics PhD Opportunities Tracker</p>
            <p><small>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</small></p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{data_summary['total_jobs']}</div>
                <div class="stat-label">Total Opportunities</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{data_summary['recent_jobs']}</div>
                <div class="stat-label">New This Month</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(data_summary['jobs_by_source'])}</div>
                <div class="stat-label">Data Sources</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{data_summary.get('website_stats', {}).get('accessible', 0)}</div>
                <div class="stat-label">Active Websites</div>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <div class="chart-container">
                <div class="chart-title">Opportunities by Source</div>
                <canvas id="sourceChart" width="400" height="300"></canvas>
            </div>
            <div class="chart-container">
                <div class="chart-title">Top Institutions</div>
                <canvas id="institutionChart" width="400" height="300"></canvas>
            </div>
        </div>
        
        <div class="opportunities-section">
            <h2 class="section-title">📋 Recent Opportunities</h2>
            <div class="filters">
                <input type="text" id="searchFilter" placeholder="Search opportunities..." class="filter-input">
                <select id="sourceFilter" class="filter-input">
                    <option value="">All Sources</option>
                    <option value="linkedin">LinkedIn</option>
                    <option value="university_website">University Website</option>
                </select>
                <select id="institutionFilter" class="filter-input">
                    <option value="">All Institutions</option>
                </select>
            </div>
            <div class="opportunities-grid" id="opportunitiesGrid">
                <!-- Opportunities will be populated by JavaScript -->
            </div>
        </div>
        
        <div class="monitoring-section">
            <h2 class="section-title">🌐 Website Monitoring</h2>
            <div class="monitoring-grid" id="monitoringGrid">
                <!-- Monitoring data will be populated by JavaScript -->
            </div>
        </div>
        
        <div class="footer">
            <p>🤖 Powered by AI • Updated every 6 hours • 
            <a href="https://github.com/HiteshBishtCV/academic-directory" style="color: rgba(255,255,255,0.8);">View on GitHub</a></p>
        </div>
    </div>

    <script>
        // Data from Python
        const opportunitiesData = {json.dumps(recent_opportunities)};
        const monitoringData = {json.dumps(website_data)};
        const sourceData = {json.dumps(data_summary['jobs_by_source'])};
        const institutionData = {json.dumps(data_summary['jobs_by_institution'])};
        
        // Chart.js configurations
        const chartOptions = {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{
                    position: 'bottom'
                }}
            }}
        }};
        
        // Source Chart
        const sourceCtx = document.getElementById('sourceChart').getContext('2d');
        new Chart(sourceCtx, {{
            type: 'doughnut',
            data: {{
                labels: sourceData.map(item => item.source.replace('_', ' ').toUpperCase()),
                datasets: [{{
                    data: sourceData.map(item => item.count),
                    backgroundColor: [
                        '#667eea',
                        '#764ba2', 
                        '#f093fb',
                        '#f5576c',
                        '#4facfe'
                    ]
                }}]
            }},
            options: chartOptions
        }});
        
        // Institution Chart
        const institutionCtx = document.getElementById('institutionChart').getContext('2d');
        new Chart(institutionCtx, {{
            type: 'bar',
            data: {{
                labels: institutionData.map(item => item.institution.length > 20 ? 
                    item.institution.substring(0, 20) + '...' : item.institution),
                datasets: [{{
                    label: 'Opportunities',
                    data: institutionData.map(item => item.count),
                    backgroundColor: '#667eea',
                    borderColor: '#5a67d8',
                    borderWidth: 1
                }}]
            }},
            options: {{
                ...chartOptions,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        // Populate opportunities
        function renderOpportunities(opportunities) {{
            const grid = document.getElementById('opportunitiesGrid');
            grid.innerHTML = '';
            
            opportunities.forEach(opp => {{
                const card = document.createElement('div');
                card.className = 'opportunity-card';
                
                const location = opp.location ? `📍 ${{opp.location}}` : '';
                const postedDate = new Date(opp.posted_date).toLocaleDateString();
                
                card.innerHTML = `
                    <div class="opp-title">${{opp.title}}</div>
                    <div class="opp-institution">${{opp.institution}}</div>
                    <div class="opp-meta">
                        <span>📅 ${{postedDate}}</span>
                        <span>${{location}}</span>
                    </div>
                    <span class="opp-tag">${{opp.source.replace('_', ' ').toUpperCase()}}</span>
                    <a href="${{opp.url}}" target="_blank" class="opp-link">View Opportunity →</a>
                `;
                
                grid.appendChild(card);
            }});
        }}
        
        // Populate monitoring data
        function renderMonitoring(data) {{
            const grid = document.getElementById('monitoringGrid');
            grid.innerHTML = '';
            
            data.forEach(item => {{
                const div = document.createElement('div');
                div.className = 'monitoring-item';
                
                const statusClass = item.accessible ? 'status-good' : 'status-error';
                const responseTime = item.response_time ? `${{item.response_time}}s` : 'N/A';
                const hasJobs = item.has_job_section ? '📋' : '❓';
                
                div.innerHTML = `
                    <div class="status-indicator ${{statusClass}}"></div>
                    <div class="monitoring-url">${{new URL(item.url).hostname}}</div>
                    <div class="monitoring-stats">
                        <span>${{responseTime}}</span>
                        <span>${{hasJobs}}</span>
                        <span>${{new Date(item.last_checked).toLocaleDateString()}}</span>
                    </div>
                `;
                
                grid.appendChild(div);
            }});
        }}
        
        // Setup filters
        function setupFilters() {{
            const searchFilter = document.getElementById('searchFilter');
            const sourceFilter = document.getElementById('sourceFilter');
            const institutionFilter = document.getElementById('institutionFilter');
            
            // Populate institution filter
            const institutions = [...new Set(opportunitiesData.map(opp => opp.institution))];
            institutions.forEach(inst => {{
                const option = document.createElement('option');
                option.value = inst;
                option.textContent = inst;
                institutionFilter.appendChild(option);
            }});
            
            // Filter function
            function filterOpportunities() {{
                const searchTerm = searchFilter.value.toLowerCase();
                const selectedSource = sourceFilter.value;
                const selectedInstitution = institutionFilter.value;
                
                const filtered = opportunitiesData.filter(opp => {{
                    const matchesSearch = opp.title.toLowerCase().includes(searchTerm) ||
                                        opp.institution.toLowerCase().includes(searchTerm);
                    const matchesSource = !selectedSource || opp.source === selectedSource;
                    const matchesInstitution = !selectedInstitution || opp.institution === selectedInstitution;
                    
                    return matchesSearch && matchesSource && matchesInstitution;
                }});
                
                renderOpportunities(filtered);
            }}
            
            searchFilter.addEventListener('input', filterOpportunities);
            sourceFilter.addEventListener('change', filterOpportunities);
            institutionFilter.addEventListener('change', filterOpportunities);
        }}
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {{
            renderOpportunities(opportunitiesData);
            renderMonitoring(monitoringData);
            setupFilters();
        }});
    </script>
</body>
</html>
"""
        
        # Write the HTML file
        output_path = os.path.join(self.output_dir, "index.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"Dashboard generated: {output_path}")
    
    def generate_api_endpoints(self):
        """Generate JSON API endpoints for external consumption"""
        
        # Generate opportunities API
        opportunities = self.get_recent_opportunities(100)
        api_dir = os.path.join(self.output_dir, "api")
        os.makedirs(api_dir, exist_ok=True)
        
        with open(os.path.join(api_dir, "opportunities.json"), "w") as f:
            json.dump({
                "last_updated": datetime.now().isoformat(),
                "total": len(opportunities),
                "opportunities": opportunities
            }, f, indent=2)
        
        # Generate summary API
        summary = self.get_data_summary()
        with open(os.path.join(api_dir, "summary.json"), "w") as f:
            json.dump({
                "last_updated": datetime.now().isoformat(),
                "summary": summary
            }, f, indent=2)
        
        # Generate monitoring API
        monitoring = self.get_website_monitoring_data()
        with open(os.path.join(api_dir, "monitoring.json"), "w") as f:
            json.dump({
                "last_updated": datetime.now().isoformat(),
                "websites": monitoring
            }, f, indent=2)
        
        print("API endpoints generated in docs/api/")
    
    def generate_rss_feed(self):
        """Generate RSS feed for new opportunities"""
        opportunities = self.get_recent_opportunities(20)
        
        rss_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">
    <channel>
        <title>Academic Directory - Medical Physics PhD Opportunities</title>
        <link>https://HiteshBishtCV.github.io/academic-directory/</link>
        <description>Latest Medical Physics PhD opportunities from top institutions</description>
        <lastBuildDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')}</lastBuildDate>
        <language>en-US</language>
"""
        
        for opp in opportunities:
            pub_date = datetime.strptime(opp['posted_date'], '%Y-%m-%d').strftime('%a, %d %b %Y %H:%M:%S +0000')
            
            rss_content += f"""
        <item>
            <title>{opp['title']}</title>
            <link>{opp['url']}</link>
            <description>PhD opportunity at {opp['institution']}</description>
            <pubDate>{pub_date}</pubDate>
            <dc:creator>{opp['institution']}</dc:creator>
            <category>{opp['source']}</category>
        </item>"""
        
        rss_content += """
    </channel>
</rss>"""
        
        with open(os.path.join(self.output_dir, "feed.xml"), "w", encoding="utf-8") as f:
            f.write(rss_content)
        
        print("RSS feed generated: docs/feed.xml")

def main():
    """Generate all web reports"""
    generator = WebReportGenerator()
    
    try:
        print("Generating web dashboard...")
        generator.generate_html_dashboard()
        
        print("Generating API endpoints...")
        generator.generate_api_endpoints()
        
        print("Generating RSS feed...")
        generator.generate_rss_feed()
        
        print("✅ All reports generated successfully!")
        print("📁 Files created in 'docs/' directory")
        print("🌐 View dashboard at: docs/index.html")
        
    except Exception as e:
        print(f"❌ Error generating reports: {e}")

if __name__ == "__main__":
    main()

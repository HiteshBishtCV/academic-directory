#!/usr/bin/env python3
"""
Web Report Generator
Creates HTML dashboard from collected data
"""

import sqlite3
import json
import os
from datetime import datetime
import calendar

def generate_web_reports():
    """Generate HTML dashboard and JSON API"""
    print("📊 Generating web reports...")
    
    # Create output directories
    os.makedirs("web_output", exist_ok=True)
    os.makedirs("web_output/data", exist_ok=True)
    
    # Connect to database and get data
    try:
        conn = sqlite3.connect("academic_directory.db")
        cursor = conn.cursor()
        
        # Get professors
        cursor.execute("SELECT name, university, email, title, h_index FROM professors ORDER BY h_index DESC")
        professors = cursor.fetchall()
        
        # Get postings
        cursor.execute("SELECT professor_name, position_type, year, month FROM postings ORDER BY year DESC, month DESC")
        postings = cursor.fetchall()
        
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")
        # Use sample data if database doesn't exist
        professors = [("Dr. Sample Professor", "Demo University", "sample@demo.edu", "Professor", 25)]
        postings = [("Dr. Sample Professor", "PhD", 2024, 1)]
    
    # Generate main HTML dashboard
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Academic Directory - Medical Physics</title>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #2c3e50;
        }}
        
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 60px 20px; 
            text-align: center; 
            border-radius: 20px; 
            margin-bottom: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .header h1 {{ 
            font-size: 3.5em; 
            margin: 0; 
            font-weight: 300;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .subtitle {{ 
            font-size: 1.4em; 
            margin: 20px 0; 
            opacity: 0.9; 
        }}
        
        .update-time {{ 
            background: rgba(255,255,255,0.15); 
            padding: 12px 25px; 
            border-radius: 30px; 
            display: inline-block;
            backdrop-filter: blur(10px);
        }}
        
        .stats {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 25px; 
            margin-bottom: 40px; 
        }}
        
        .stat-card {{ 
            background: white; 
            padding: 30px; 
            border-radius: 15px; 
            text-align: center;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
            border-top: 4px solid #667eea;
        }}
        
        .stat-card:hover {{ 
            transform: translateY(-8px); 
        }}
        
        .stat-number {{ 
            font-size: 3em; 
            font-weight: bold; 
            color: #667eea; 
            margin-bottom: 10px;
        }}
        
        .stat-label {{ 
            color: #7f8c8d; 
            font-size: 1.1em; 
            font-weight: 500;
        }}
        
        .section {{ 
            background: white; 
            padding: 40px; 
            border-radius: 20px; 
            margin-bottom: 30px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }}
        
        .section h2 {{ 
            color: #2c3e50; 
            margin-bottom: 25px; 
            padding-bottom: 15px; 
            border-bottom: 3px solid #667eea;
            font-size: 2.2em;
            font-weight: 300;
        }}
        
        .professor-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); 
            gap: 25px; 
        }}
        
        .professor-card {{ 
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            padding: 25px; 
            border-radius: 15px; 
            border-left: 5px solid #667eea;
            transition: all 0.3s ease;
        }}
        
        .professor-card:hover {{ 
            transform: translateY(-5px); 
            box-shadow: 0 12px 30px rgba(0,0,0,0.15);
            background: white;
        }}
        
        .professor-name {{ 
            font-size: 1.4em; 
            font-weight: 600; 
            color: #2c3e50; 
            margin-bottom: 8px; 
        }}
        
        .professor-university {{ 
            color: #667eea; 
            font-weight: 500; 
            font-size: 1.1em;
            margin-bottom: 5px; 
        }}
        
        .professor-title {{ 
            color: #27ae60; 
            font-weight: 500; 
            margin-bottom: 8px;
        }}
        
        .professor-email {{ 
            color: #7f8c8d; 
            font-size: 0.9em; 
            font-family: monospace;
            background: #f1f3f4;
            padding: 5px 10px;
            border-radius: 5px;
            margin-top: 10px;
        }}
        
        .h-index-badge {{
            float: right;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
        }}
        
        .footer {{ 
            text-align: center; 
            margin-top: 60px; 
            padding: 40px; 
            color: #7f8c8d;
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 2.5em; }}
            .stats {{ grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }}
            .professor-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎓 Academic Directory</h1>
        <p class="subtitle">Medical Physics PhD Opportunities & Hiring Pattern Analysis</p>
        <div class="update-time">Last Updated: {datetime.now().strftime("%B %d, %Y at %H:%M UTC")}</div>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{len(professors)}</div>
            <div class="stat-label">Total Professors</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(set(p[1] for p in professors))}</div>
            <div class="stat-label">Universities</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(postings)}</div>
            <div class="stat-label">Historical Postings</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">6h</div>
            <div class="stat-label">Update Frequency</div>
        </div>
    </div>
    
    <div class="section">
        <h2>👨‍🔬 Professor Directory</h2>
        <div class="professor-grid">"""
    
    # Add each professor to the HTML
    for name, university, email, title, h_index in professors:
        html_content += f"""
        <div class="professor-card">
            <div class="h-index-badge">H-index: {h_index}</div>
            <div class="professor-name">{name}</div>
            <div class="professor-university">{university}</div>
            <div class="professor-title">{title}</div>
            <div class="professor-email">{email}</div>
        </div>"""
    
    html_content += """
        </div>
    </div>
    
    <div class="footer">
        <p>🔄 <strong>Automatically updated every 6 hours</strong> via GitHub Actions</p>
        <p>📊 Data collected from major medical physics programs</p>
        <p>🎯 Helping students find PhD opportunities in Medical Physics</p>
    </div>
</body>
</html>"""
    
    # Save the HTML file
    with open("web_output/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # Generate JSON API
    api_data = {
        "total_professors": len(professors),
        "total_universities": len(set(p[1] for p in professors)),
        "total_postings": len(postings),
        "last_updated": datetime.now().isoformat(),
        "professors": [
            {
                "name": p[0],
                "university": p[1], 
                "email": p[2],
                "title": p[3],
                "h_index": p[4]
            } for p in professors
        ]
    }
    
    # Save JSON API
    with open("web_output/data/summary.json", "w") as f:
        json.dump(api_data, f, indent=2)
    
    print(f"✅ Generated web reports:")
    print(f"   📄 HTML Dashboard: web_output/index.html")
    print(f"   📊 JSON API: web_output/data/summary.json")
    print(f"   👨‍🔬 Professors: {len(professors)}")

if __name__ == "__main__":
    generate_web_reports()

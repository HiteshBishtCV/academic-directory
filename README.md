# 🎓 Academic Directory & Hiring Pattern Analyzer

Automated Medical Physics PhD opportunity tracker.

## 🌐 Live Dashboard

**View your dashboard at:** `https://YOUR_USERNAME.github.io/academic-directory/`

## 🚀 What This System Does

- **Professor Directory**: Profiles from major medical physics programs
- **Hiring Patterns**: Historical PhD posting analysis
- **Application Timing**: Optimal timing recommendations
- **Interactive Dashboard**: Real-time web interface updated every 6 hours

## 📊 Current Statistics

- **Professors Tracked**: Automatically updated
- **Universities Covered**: Major medical physics programs
- **Update Frequency**: Every 6 hours via GitHub Actions

## 🔧 Local Development

Setup and run:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python scripts/collect_data.py
python web_report_generator.py
```

## 📄 License

MIT License - Free for academic and personal use

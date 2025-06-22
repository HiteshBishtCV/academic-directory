#!/usr/bin/env python3
"""
Advanced features and utilities for Academic Directory
Email notifications, error handling, performance monitoring
"""

import smtplib
import os
import json
import time
import logging
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Dict, List, Optional
import requests
from dataclasses import dataclass
import sqlite3
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class NotificationConfig:
    """Email notification configuration"""
    smtp_server: str
    smtp_port: int
    email_user: str
    email_password: str
    recipient_email: str
    enabled: bool = True

class EmailNotifier:
    """Handle email notifications for new opportunities"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def send_opportunity_alert(self, opportunities: List[Dict]) -> bool:
        """Send email alert for new opportunities"""
        if not self.config.enabled or not opportunities:
            return True
            
        try:
            msg = MimeMultipart('alternative')
            msg['Subject'] = f"🎓 {len(opportunities)} New PhD Opportunities Found!"
            msg['From'] = self.config.email_user
            msg['To'] = self.config.recipient_email
            
            # Create HTML email content
            html_content = self._create_opportunity_email_html(opportunities)
            msg.attach(MimeText(html_content, 'html'))
            
            # Send email
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.email_user, self.config.email_password)
                server.send_message(msg)
            
            self.logger.info(f"Email notification sent for {len(opportunities)} opportunities")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {e}")
            return False
    
    def _create_opportunity_email_html(self, opportunities: List[Dict]) -> str:
        """Create HTML email content for opportunities"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .opportunity {{ background: #f8f9fa; padding: 15px; margin: 10px 0; 
                              border-left: 4px solid #667eea; border-radius: 5px; }}
                .title {{ font-size: 18px; font-weight: bold; color: #333; margin-bottom: 8px; }}
                .institution {{ color: #667eea; font-size: 16px; margin-bottom: 5px; }}
                .meta {{ color: #666; font-size: 14px; margin-bottom: 8px; }}
                .link {{ display: inline-block; background: #667eea; color: white; 
                        padding: 8px 16px; text-decoration: none; border-radius: 4px; }}
                .footer {{ margin-top: 30px; padding: 15px; background: #f1f1f1; 
                          border-radius: 5px; color: #666; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎓 New PhD Opportunities Found!</h1>
                <p>Academic Directory has discovered {len(opportunities)} new positions</p>
                <p><small>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</small></p>
            </div>
        """
        
        for opp in opportunities[:10]:  # Limit to 10 in email
            html += f"""
            <div class="opportunity">
                <div class="title">{opp.get('title', 'Untitled Position')}</div>
                <div class="institution">📍 {opp.get('institution', 'Unknown Institution')}</div>
                <div class="meta">
                    📅 Posted: {opp.get('posted_date', 'Unknown')} | 
                    🏷️ Source: {opp.get('source', 'Unknown').replace('_', ' ').title()}
                    {f" | 🌍 {opp.get('location', '')}" if opp.get('location') else ""}
                </div>
                <a href="{opp.get('url', '#')}" class="link">View Opportunity →</a>
            </div>
            """
        
        if len(opportunities) > 10:
            html += f"<p><em>... and {len(opportunities) - 10} more opportunities available on the dashboard.</em></p>"
        
        html += f"""
            <div class="footer">
                <p>📊 <a href="https://HiteshBishtCV.github.io/academic-directory/">View Full Dashboard</a></p>
                <p>🔄 Updates run automatically every 6 hours</p>
                <p>To unsubscribe, update your notification preferences in the configuration.</p>
            </div>
        </body>
        </html>
        """
        
        return html

class PerformanceMonitor:
    """Monitor system performance and usage"""
    
    def __init__(self, db_path: str = "data/academic_directory.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_monitoring_tables()
    
    def _init_monitoring_tables(self):
        """Initialize performance monitoring tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    duration_seconds REAL,
                    success BOOLEAN,
                    error_message TEXT,
                    metadata TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_opportunities INTEGER,
                    new_opportunities_today INTEGER,
                    websites_monitored INTEGER,
                    websites_accessible INTEGER,
                    avg_response_time REAL
                )
            ''')
            
            conn.commit()
    
    def log_operation(self, operation: str, duration: float, success: bool, 
                     error: Optional[str] = None, metadata: Optional[Dict] = None):
        """Log an operation's performance"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_logs 
                (timestamp, operation, duration_seconds, success, error_message, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                operation,
                duration,
                success,
                error,
                json.dumps(metadata) if metadata else None
            ))
            
            conn.commit()
    
    def record_system_stats(self):
        """Record current system statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get current stats
            stats = cursor.execute('''
                SELECT 
                    COUNT(*) as total_opportunities,
                    COUNT(CASE WHEN posted_date >= date('now') THEN 1 END) as new_today
                FROM job_opportunities
            ''').fetchone()
            
            website_stats = cursor.execute('''
                SELECT 
                    COUNT(*) as total_websites,
                    COUNT(CASE WHEN accessible = 1 THEN 1 END) as accessible,
                    AVG(response_time) as avg_time
                FROM website_monitoring
            ''').fetchone()
            
            cursor.execute('''
                INSERT INTO system_stats 
                (timestamp, total_opportunities, new_opportunities_today, 
                 websites_monitored, websites_accessible, avg_response_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                stats[0], stats[1],
                website_stats[0], website_stats[1], website_stats[2]
            ))
            
            conn.commit()
    
    def get_performance_report(self, days: int = 7) -> Dict:
        """Generate performance report for last N days"""
        with sqlite3.connect(self.db_path) as conn:
            since_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Operation success rates
            operations = conn.execute('''
                SELECT operation, 
                       COUNT(*) as total,
                       SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                       AVG(duration_seconds) as avg_duration
                FROM performance_logs 
                WHERE timestamp >= ?
                GROUP BY operation
            ''', (since_date,)).fetchall()
            
            # Recent errors
            errors = conn.execute('''
                SELECT timestamp, operation, error_message
                FROM performance_logs 
                WHERE success = 0 AND timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT 10
            ''', (since_date,)).fetchall()
            
            return {
                'operations': [
                    {
                        'name': op[0],
                        'total_runs': op[1],
                        'success_rate': op[2] / op[1] if op[1] > 0 else 0,
                        'avg_duration': op[3]
                    }
                    for op in operations
                ],
                'recent_errors': [
                    {
                        'timestamp': err[0],
                        'operation': err[1],
                        'error': err[2]
                    }
                    for err in errors
                ]
            }

class ConfigManager:
    """Manage configuration and settings"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default configuration"""
        default_config = {
            'database': {
                'path': 'data/academic_directory.db',
                'backup_interval': 24
            },
            'scraping': {
                'delay_between_requests': 2,
                'max_retries': 3,
                'timeout': 10
            },
            'notifications': {
                'email_enabled': False,
                'webhook_enabled': False
            },
            'monitoring': {
                'check_interval': 6,
                'performance_logging': True
            }
        }
        
        with open(self.config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        return default_config
    
    def get_notification_config(self) -> Optional[NotificationConfig]:
        """Get email notification configuration"""
        if not self.config.get('notifications', {}).get('email_enabled', False):
            return None
        
        return NotificationConfig(
            smtp_server=os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            smtp_port=int(os.getenv('SMTP_PORT', '587')),
            email_user=os.getenv('EMAIL_USER', ''),
            email_password=os.getenv('EMAIL_PASSWORD', ''),
            recipient_email=os.getenv('NOTIFICATION_EMAIL', ''),
            enabled=True
        )

class WebhookNotifier:
    """Send notifications to webhooks (Slack, Discord, etc.)"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.logger = logging.getLogger(__name__)
    
    def send_slack_notification(self, opportunities: List[Dict]) -> bool:
        """Send notification to Slack webhook"""
        if not opportunities:
            return True
        
        try:
            message = {
                "text": f"🎓 Found {len(opportunities)} new PhD opportunities!",
                "attachments": [
                    {
                        "color": "#667eea",
                        "fields": [
                            {
                                "title": opp.get('title', 'Untitled'),
                                "value": f"📍 {opp.get('institution', 'Unknown')} | "
                                        f"🏷️ {opp.get('source', 'Unknown').replace('_', ' ').title()}",
                                "short": False
                            }
                            for opp in opportunities[:5]  # Limit to 5
                        ],
                        "footer": "Academic Directory",
                        "ts": int(time.time())
                    }
                ]
            }
            
            response = requests.post(self.webhook_url, json=message, timeout=10)
            response.raise_for_status()
            
            self.logger.info(f"Slack notification sent for {len(opportunities)} opportunities")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send Slack notification: {e}")
            return False

class HealthChecker:
    """System health monitoring and alerts"""
    
    def __init__(self, db_path: str = "data/academic_directory.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
    
    def check_system_health(self) -> Dict:
        """Perform comprehensive system health check"""
        health_status = {
            'overall': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        # Database health
        db_health = self._check_database_health()
        health_status['checks']['database'] = db_health
        
        # Data freshness
        data_health = self._check_data_freshness()
        health_status['checks']['data_freshness'] = data_health
        
        # Website monitoring
        website_health = self._check_website_health()
        health_status['checks']['websites'] = website_health
        
        # Determine overall health
        failed_checks = [check for check in health_status['checks'].values() 
                        if check['status'] != 'healthy']
        
        if failed_checks:
            health_status['overall'] = 'degraded' if len(failed_checks) == 1 else 'unhealthy'
        
        return health_status
    
    def _check_database_health(self) -> Dict:
        """Check database connectivity and integrity"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check table existence
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                required_tables = ['job_opportunities', 'website_monitoring', 'professors']
                missing_tables = [table for table in required_tables if table not in tables]
                
                if missing_tables:
                    return {
                        'status': 'unhealthy',
                        'message': f"Missing tables: {missing_tables}"
                    }
                
                # Check data integrity
                cursor.execute("SELECT COUNT(*) FROM job_opportunities")
                opp_count = cursor.fetchone()[0]
                
                return {
                    'status': 'healthy',
                    'message': f"Database operational with {opp_count} opportunities"
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f"Database error: {str(e)}"
            }
    
    def _check_data_freshness(self) -> Dict:
        """Check if data is fresh (updated recently)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check last update time
                cursor.execute('''
                    SELECT MAX(posted_date) 
                    FROM job_opportunities 
                    WHERE posted_date >= date('now', '-7 days')
                ''')
                recent_data = cursor.fetchone()[0]
                
                if not recent_data:
                    return {
                        'status': 'degraded',
                        'message': 'No new opportunities in the last 7 days'
                    }
                
                # Check monitoring freshness
                cursor.execute('''
                    SELECT MAX(last_checked) 
                    FROM website_monitoring 
                    WHERE last_checked >= datetime('now', '-1 day')
                ''')
                monitoring_data = cursor.fetchone()[0]
                
                if not monitoring_data:
                    return {
                        'status': 'degraded',
                        'message': 'Website monitoring data is stale'
                    }
                
                return {
                    'status': 'healthy',
                    'message': 'Data is fresh and up-to-date'
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f"Data freshness check failed: {str(e)}"
            }
    
    def _check_website_health(self) -> Dict:
        """Check website monitoring status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total,
                        COUNT(CASE WHEN accessible = 1 THEN 1 END) as accessible,
                        AVG(response_time) as avg_time
                    FROM website_monitoring
                    WHERE last_checked >= datetime('now', '-1 day')
                ''')
                
                stats = cursor.fetchone()
                total, accessible, avg_time = stats
                
                if total == 0:
                    return {
                        'status': 'unhealthy',
                        'message': 'No website monitoring data available'
                    }
                
                accessibility_rate = accessible / total if total > 0 else 0
                
                if accessibility_rate < 0.8:  # Less than 80% accessible
                    return {
                        'status': 'degraded',
                        'message': f'Only {accessibility_rate:.1%} of websites accessible'
                    }
                
                return {
                    'status': 'healthy',
                    'message': f'{accessibility_rate:.1%} websites accessible, avg response: {avg_time:.1f}s'
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f"Website health check failed: {str(e)}"
            }

class BackupManager:
    """Manage database backups and data export"""
    
    def __init__(self, db_path: str = "data/academic_directory.db"):
        self.db_path = db_path
        self.backup_dir = "data/backups"
        os.makedirs(self.backup_dir, exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def create_backup(self) -> str:
        """Create a timestamped database backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"academic_directory_backup_{timestamp}.db"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            # SQLite backup
            with sqlite3.connect(self.db_path) as source:
                with sqlite3.connect(backup_path) as backup:
                    source.backup(backup)
            
            self.logger.info(f"Database backup created: {backup_path}")
            
            # Clean old backups (keep last 10)
            self._cleanup_old_backups()
            
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            raise
    
    def _cleanup_old_backups(self, keep_count: int = 10):
        """Remove old backup files, keeping only the most recent ones"""
        try:
            backup_files = []
            for filename in os.listdir(self.backup_dir):
                if filename.startswith("academic_directory_backup_") and filename.endswith(".db"):
                    filepath = os.path.join(self.backup_dir, filename)
                    backup_files.append((filepath, os.path.getctime(filepath)))
            
            # Sort by creation time, newest first
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Remove old backups
            for filepath, _ in backup_files[keep_count:]:
                os.remove(filepath)
                self.logger.info(f"Removed old backup: {filepath}")
                
        except Exception as e:
            self.logger.warning(f"Backup cleanup failed: {e}")
    
    def export_to_csv(self, output_dir: str = "data/exports") -> Dict[str, str]:
        """Export all data to CSV files"""
        os.makedirs(output_dir, exist_ok=True)
        exported_files = {}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Export opportunities
                opportunities_df = pd.read_sql_query('''
                    SELECT title, institution, location, application_deadline, 
                           posted_date, description, url, source
                    FROM job_opportunities
                    ORDER BY posted_date DESC
                ''', conn)
                
                opp_file = os.path.join(output_dir, "opportunities.csv")
                opportunities_df.to_csv(opp_file, index=False)
                exported_files['opportunities'] = opp_file
                
                # Export website monitoring
                monitoring_df = pd.read_sql_query('''
                    SELECT url, accessible, response_time, has_job_section, last_checked
                    FROM website_monitoring
                    ORDER BY last_checked DESC
                ''', conn)
                
                monitoring_file = os.path.join(output_dir, "website_monitoring.csv")
                monitoring_df.to_csv(monitoring_file, index=False)
                exported_files['monitoring'] = monitoring_file
                
                # Export performance logs if available
                try:
                    perf_df = pd.read_sql_query('''
                        SELECT timestamp, operation, duration_seconds, success, error_message
                        FROM performance_logs
                        ORDER BY timestamp DESC
                        LIMIT 1000
                    ''', conn)
                    
                    perf_file = os.path.join(output_dir, "performance_logs.csv")
                    perf_df.to_csv(perf_file, index=False)
                    exported_files['performance'] = perf_file
                except:
                    pass  # Table might not exist
                
            self.logger.info(f"Data exported to CSV files: {list(exported_files.keys())}")
            return exported_files
            
        except Exception as e:
            self.logger.error(f"CSV export failed: {e}")
            raise

class EnhancedRunner:
    """Enhanced runner with monitoring, notifications, and error handling"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.performance_monitor = PerformanceMonitor()
        self.health_checker = HealthChecker()
        self.backup_manager = BackupManager()
        self.logger = self._setup_logging()
        
        # Setup notifications
        self.email_notifier = None
        self.webhook_notifier = None
        self._setup_notifications()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger('academic_directory')
        logger.setLevel(logging.INFO)
        
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler('logs/academic_directory.log')
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _setup_notifications(self):
        """Setup notification handlers"""
        # Email notifications
        email_config = self.config_manager.get_notification_config()
        if email_config:
            self.email_notifier = EmailNotifier(email_config)
        
        # Webhook notifications
        webhook_url = os.getenv('WEBHOOK_URL')
        if webhook_url:
            self.webhook_notifier = WebhookNotifier(webhook_url)
    
    def run_with_monitoring(self, operation_name: str, operation_func, *args, **kwargs):
        """Run an operation with performance monitoring"""
        start_time = time.time()
        success = False
        error_message = None
        result = None
        
        try:
            self.logger.info(f"Starting operation: {operation_name}")
            result = operation_func(*args, **kwargs)
            success = True
            self.logger.info(f"Completed operation: {operation_name}")
            
        except Exception as e:
            error_message = str(e)
            self.logger.error(f"Operation failed: {operation_name} - {error_message}")
            raise
        
        finally:
            duration = time.time() - start_time
            self.performance_monitor.log_operation(
                operation_name, duration, success, error_message
            )
        
        return result
    
    def run_full_update_with_notifications(self):
        """Run complete update cycle with notifications and monitoring"""
        try:
            # Pre-flight health check
            health_status = self.health_checker.check_system_health()
            self.logger.info(f"System health: {health_status['overall']}")
            
            # Create backup before major operations
            if self.config_manager.config.get('database', {}).get('backup_interval', 24) <= 24:
                self.run_with_monitoring("database_backup", self.backup_manager.create_backup)
            
            # Import the main tracker
            from enhanced_academic_tracker import EnhancedAcademicTracker
            tracker = EnhancedAcademicTracker()
            
            # Get baseline opportunity count
            with sqlite3.connect(tracker.db.db_path) as conn:
                baseline_count = conn.execute("SELECT COUNT(*) FROM job_opportunities").fetchone()[0]
            
            # Run data collection
            self.run_with_monitoring("full_scan", tracker.run_full_scan)
            
            # Check for new opportunities
            with sqlite3.connect(tracker.db.db_path) as conn:
                new_count = conn.execute("SELECT COUNT(*) FROM job_opportunities").fetchone()[0]
                
                if new_count > baseline_count:
                    # Get new opportunities for notification
                    new_opportunities = conn.execute('''
                        SELECT title, institution, location, posted_date, url, source
                        FROM job_opportunities
                        ORDER BY rowid DESC
                        LIMIT ?
                    ''', (new_count - baseline_count,)).fetchall()
                    
                    new_opps_dict = [
                        {
                            'title': opp[0],
                            'institution': opp[1], 
                            'location': opp[2],
                            'posted_date': opp[3],
                            'url': opp[4],
                            'source': opp[5]
                        }
                        for opp in new_opportunities
                    ]
                    
                    # Send notifications
                    if self.email_notifier:
                        self.run_with_monitoring(
                            "email_notification", 
                            self.email_notifier.send_opportunity_alert,
                            new_opps_dict
                        )
                    
                    if self.webhook_notifier:
                        self.run_with_monitoring(
                            "webhook_notification",
                            self.webhook_notifier.send_slack_notification,
                            new_opps_dict
                        )
                    
                    self.logger.info(f"Found {len(new_opps_dict)} new opportunities")
            
            # Generate reports
            from web_report_generator import WebReportGenerator
            report_generator = WebReportGenerator()
            
            self.run_with_monitoring("generate_dashboard", report_generator.generate_html_dashboard)
            self.run_with_monitoring("generate_api", report_generator.generate_api_endpoints)
            self.run_with_monitoring("generate_rss", report_generator.generate_rss_feed)
            
            # Record system statistics
            self.performance_monitor.record_system_stats()
            
            # Final health check
            final_health = self.health_checker.check_system_health()
            self.logger.info(f"Final system health: {final_health['overall']}")
            
            # Clean up
            tracker.cleanup()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Full update cycle failed: {e}")
            
            # Send error notification
            if self.email_notifier:
                try:
                    error_msg = MimeText(f"Academic Directory update failed: {str(e)}")
                    error_msg['Subject'] = "🚨 Academic Directory Error"
                    error_msg['From'] = self.email_notifier.config.email_user
                    error_msg['To'] = self.email_notifier.config.recipient_email
                    
                    with smtplib.SMTP(
                        self.email_notifier.config.smtp_server, 
                        self.email_notifier.config.smtp_port
                    ) as server:
                        server.starttls()
                        server.login(
                            self.email_notifier.config.email_user,
                            self.email_notifier.config.email_password
                        )
                        server.send_message(error_msg)
                except:
                    pass  # Don't let notification errors break the error handling
            
            return False
    
    def generate_health_report(self) -> Dict:
        """Generate comprehensive health and performance report"""
        health_status = self.health_checker.check_system_health()
        performance_report = self.performance_monitor.get_performance_report()
        
        return {
            'health': health_status,
            'performance': performance_report,
            'generated_at': datetime.now().isoformat()
        }

def main():
    """Main entry point for enhanced runner"""
    runner = EnhancedRunner()
    
    try:
        success = runner.run_full_update_with_notifications()
        
        if success:
            print("✅ Update completed successfully!")
            
            # Generate health report
            health_report = runner.generate_health_report()
            with open("logs/health_report.json", "w") as f:
                json.dump(health_report, f, indent=2)
            
            print("📊 Health report saved to logs/health_report.json")
        else:
            print("❌ Update failed - check logs for details")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Update interrupted by user")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import sys
    main()

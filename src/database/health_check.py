"""
Database health check functionality

This module provides comprehensive health checks for the database
to ensure system reliability and monitoring.
"""

from datetime import datetime, timedelta
from src.models.user import db
from src.models.customer import Customer
from src.models.crew_member import CrewMember
from src.models.crew import Crew
from src.models.appointment import Appointment
from sqlalchemy import text
import logging
import time

logger = logging.getLogger(__name__)

class DatabaseHealthChecker:
    """Comprehensive database health checker"""
    
    def __init__(self):
        self.checks = []
        self.results = {}
    
    def check_connection(self):
        """Test basic database connection"""
        try:
            start_time = time.time()
            db.session.execute(text('SELECT 1'))
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            return {
                'status': 'healthy',
                'response_time_ms': round(response_time, 2),
                'message': 'Database connection successful'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'message': 'Database connection failed'
            }
    
    def check_tables_exist(self):
        """Verify all required tables exist"""
        try:
            required_tables = ['customer', 'crew_member', 'crew', 'appointment']
            existing_tables = []
            
            for table in required_tables:
                try:
                    db.session.execute(text(f'SELECT COUNT(*) FROM {table}'))
                    existing_tables.append(table)
                except Exception:
                    pass
            
            missing_tables = set(required_tables) - set(existing_tables)
            
            if not missing_tables:
                return {
                    'status': 'healthy',
                    'tables': existing_tables,
                    'message': 'All required tables exist'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'existing_tables': existing_tables,
                    'missing_tables': list(missing_tables),
                    'message': f'Missing tables: {", ".join(missing_tables)}'
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'message': 'Failed to check table existence'
            }
    
    def check_data_integrity(self):
        """Check basic data integrity"""
        try:
            issues = []
            
            # Check for orphaned appointments (appointments without customers)
            orphaned_appointments = db.session.query(Appointment).filter(
                ~Appointment.customer_id.in_(db.session.query(Customer.id))
            ).count()
            
            if orphaned_appointments > 0:
                issues.append(f'{orphaned_appointments} appointments without valid customers')
            
            # Check for crew members without crews (if crew_id is set)
            orphaned_crew_members = db.session.query(CrewMember).filter(
                CrewMember.crew_id.isnot(None),
                ~CrewMember.crew_id.in_(db.session.query(Crew.id))
            ).count()
            
            if orphaned_crew_members > 0:
                issues.append(f'{orphaned_crew_members} crew members with invalid crew references')
            
            if not issues:
                return {
                    'status': 'healthy',
                    'message': 'Data integrity checks passed'
                }
            else:
                return {
                    'status': 'warning',
                    'issues': issues,
                    'message': f'Data integrity issues found: {len(issues)}'
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'message': 'Failed to check data integrity'
            }
    
    def check_performance_metrics(self):
        """Check basic performance metrics"""
        try:
            metrics = {}
            
            # Count records in each table
            start_time = time.time()
            metrics['customers'] = Customer.query.count()
            metrics['customer_query_time_ms'] = round((time.time() - start_time) * 1000, 2)
            
            start_time = time.time()
            metrics['appointments'] = Appointment.query.count()
            metrics['appointment_query_time_ms'] = round((time.time() - start_time) * 1000, 2)
            
            start_time = time.time()
            metrics['crew_members'] = CrewMember.query.count()
            metrics['crew_member_query_time_ms'] = round((time.time() - start_time) * 1000, 2)
            
            start_time = time.time()
            metrics['crews'] = Crew.query.count()
            metrics['crew_query_time_ms'] = round((time.time() - start_time) * 1000, 2)
            
            # Check for slow queries (> 100ms)
            slow_queries = []
            for key, value in metrics.items():
                if key.endswith('_query_time_ms') and value > 100:
                    slow_queries.append(f"{key}: {value}ms")
            
            status = 'healthy' if not slow_queries else 'warning'
            message = 'Performance metrics normal' if not slow_queries else f'Slow queries detected: {", ".join(slow_queries)}'
            
            return {
                'status': status,
                'metrics': metrics,
                'slow_queries': slow_queries,
                'message': message
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'message': 'Failed to collect performance metrics'
            }
    
    def check_recent_activity(self):
        """Check for recent database activity"""
        try:
            now = datetime.now()
            last_24h = now - timedelta(hours=24)
            
            # Count recent appointments
            recent_appointments = Appointment.query.filter(
                Appointment.created_at >= last_24h
            ).count()
            
            # Count recent customers
            recent_customers = Customer.query.filter(
                Customer.created_at >= last_24h
            ).count()
            
            activity = {
                'recent_appointments': recent_appointments,
                'recent_customers': recent_customers,
                'period': '24 hours'
            }
            
            return {
                'status': 'healthy',
                'activity': activity,
                'message': f'Recent activity: {recent_appointments} appointments, {recent_customers} customers'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'message': 'Failed to check recent activity'
            }
    
    def run_all_checks(self):
        """Run all health checks and return comprehensive report"""
        checks = {
            'connection': self.check_connection,
            'tables': self.check_tables_exist,
            'data_integrity': self.check_data_integrity,
            'performance': self.check_performance_metrics,
            'activity': self.check_recent_activity
        }
        
        results = {}
        overall_status = 'healthy'
        
        for check_name, check_func in checks.items():
            try:
                result = check_func()
                results[check_name] = result
                
                # Determine overall status
                if result['status'] == 'unhealthy':
                    overall_status = 'unhealthy'
                elif result['status'] == 'warning' and overall_status == 'healthy':
                    overall_status = 'warning'
                    
            except Exception as e:
                results[check_name] = {
                    'status': 'unhealthy',
                    'error': str(e),
                    'message': f'Health check failed: {check_name}'
                }
                overall_status = 'unhealthy'
        
        return {
            'overall_status': overall_status,
            'timestamp': datetime.now().isoformat(),
            'checks': results,
            'summary': self._generate_summary(results)
        }
    
    def _generate_summary(self, results):
        """Generate a summary of health check results"""
        healthy_count = sum(1 for r in results.values() if r['status'] == 'healthy')
        warning_count = sum(1 for r in results.values() if r['status'] == 'warning')
        unhealthy_count = sum(1 for r in results.values() if r['status'] == 'unhealthy')
        
        return {
            'total_checks': len(results),
            'healthy': healthy_count,
            'warnings': warning_count,
            'unhealthy': unhealthy_count
        }

def get_database_health():
    """Convenience function to get database health status"""
    checker = DatabaseHealthChecker()
    return checker.run_all_checks()

if __name__ == '__main__':
    # This allows running health checks directly
    from src.main import app
    
    with app.app_context():
        health_report = get_database_health()
        print(f"Database Health Status: {health_report['overall_status']}")
        for check_name, result in health_report['checks'].items():
            print(f"  {check_name}: {result['status']} - {result['message']}")


"""
Health check API endpoints

Provides comprehensive health monitoring for the moving scheduling server
including database health, system status, and performance metrics.
"""

from flask import Blueprint, jsonify
from datetime import datetime
from src.database.health_check import get_database_health
import logging
import os
import psutil

health_bp = Blueprint('health', __name__)
logger = logging.getLogger(__name__)

@health_bp.route('/health', methods=['GET'])
def basic_health_check():
    """Basic health check endpoint for load balancers"""
    try:
        # Quick database connection test
        from src.models.user import db
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'moving-scheduling-server',
            'version': '1.0.0'
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'moving-scheduling-server',
            'error': str(e)
        }), 503

@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """Comprehensive health check with detailed information"""
    try:
        # Get database health
        db_health = get_database_health()
        
        # Get system information
        system_info = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'uptime': datetime.now().isoformat()
        }
        
        # Determine overall status
        overall_status = 'healthy'
        if db_health['overall_status'] == 'unhealthy':
            overall_status = 'unhealthy'
        elif db_health['overall_status'] == 'warning':
            overall_status = 'warning'
        
        # Check system resources
        if system_info['cpu_percent'] > 80 or system_info['memory_percent'] > 80:
            if overall_status == 'healthy':
                overall_status = 'warning'
        
        if system_info['cpu_percent'] > 95 or system_info['memory_percent'] > 95:
            overall_status = 'unhealthy'
        
        response = {
            'status': overall_status,
            'timestamp': datetime.now().isoformat(),
            'service': 'moving-scheduling-server',
            'version': '1.0.0',
            'database': db_health,
            'system': system_info,
            'environment': {
                'python_version': os.sys.version,
                'flask_env': os.environ.get('FLASK_ENV', 'production')
            }
        }
        
        status_code = 200 if overall_status == 'healthy' else (503 if overall_status == 'unhealthy' else 200)
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'moving-scheduling-server',
            'error': str(e)
        }), 503

@health_bp.route('/health/database', methods=['GET'])
def database_health_check():
    """Database-specific health check"""
    try:
        db_health = get_database_health()
        status_code = 200 if db_health['overall_status'] == 'healthy' else (503 if db_health['overall_status'] == 'unhealthy' else 200)
        return jsonify(db_health), status_code
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return jsonify({
            'overall_status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 503

@health_bp.route('/health/metrics', methods=['GET'])
def system_metrics():
    """System performance metrics"""
    try:
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'percent': psutil.cpu_percent(interval=1),
                'count': psutil.cpu_count(),
                'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else None
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent,
                'used': psutil.virtual_memory().used
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent
            },
            'network': {
                'bytes_sent': psutil.net_io_counters().bytes_sent,
                'bytes_recv': psutil.net_io_counters().bytes_recv,
                'packets_sent': psutil.net_io_counters().packets_sent,
                'packets_recv': psutil.net_io_counters().packets_recv
            }
        }
        
        return jsonify(metrics), 200
    except Exception as e:
        logger.error(f"System metrics check failed: {str(e)}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@health_bp.route('/health/ready', methods=['GET'])
def readiness_check():
    """Kubernetes-style readiness check"""
    try:
        # Check if the service is ready to accept requests
        from src.models.user import db
        from sqlalchemy import text
        
        # Test database connection
        db.session.execute(text('SELECT 1'))
        
        # Check if all required tables exist
        required_tables = ['customer', 'appointment', 'crew', 'crew_member']
        for table in required_tables:
            db.session.execute(text(f'SELECT COUNT(*) FROM {table}'))
        
        return jsonify({
            'status': 'ready',
            'timestamp': datetime.now().isoformat(),
            'message': 'Service is ready to accept requests'
        }), 200
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return jsonify({
            'status': 'not_ready',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 503

@health_bp.route('/health/live', methods=['GET'])
def liveness_check():
    """Kubernetes-style liveness check"""
    try:
        # Basic liveness check - just verify the service is running
        return jsonify({
            'status': 'alive',
            'timestamp': datetime.now().isoformat(),
            'message': 'Service is alive'
        }), 200
    except Exception as e:
        logger.error(f"Liveness check failed: {str(e)}")
        return jsonify({
            'status': 'dead',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 503


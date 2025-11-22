"""
Production Health Check and Monitoring Module
GenHealth.AI Clinical Document Processing API
"""

from flask import jsonify, request
import psutil
import os
import sys
from datetime import datetime, timedelta
import subprocess

def get_system_health():
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Process info
        process = psutil.Process()
        process_memory = process.memory_info()
        
        return {
            'system': {
                'cpu_usage_percent': cpu_percent,
                'memory_total_gb': round(memory.total / (1024**3), 2),
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'memory_usage_percent': memory.percent,
                'disk_total_gb': round(disk.total / (1024**3), 2),
                'disk_free_gb': round(disk.free / (1024**3), 2),
                'disk_usage_percent': round((disk.used / disk.total) * 100, 1)
            },
            'process': {
                'memory_rss_mb': round(process_memory.rss / (1024**2), 2),
                'memory_vms_mb': round(process_memory.vms / (1024**2), 2),
                'threads': process.num_threads(),
                'connections': len(process.connections()),
                'open_files': len(process.open_files()) if hasattr(process, 'open_files') else 0
            },
            'python': {
                'version': sys.version,
                'executable': sys.executable,
                'platform': sys.platform
            }
        }
    except Exception as e:
        return {'error': f'Failed to get system metrics: {str(e)}'}

def check_dependencies():
    dependencies = {}
    
    # Check Tesseract OCR
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            dependencies['tesseract'] = {
                'status': 'healthy',
                'version': version_line,
                'path': subprocess.run(['which', 'tesseract'], 
                                     capture_output=True, text=True).stdout.strip()
            }
        else:
            dependencies['tesseract'] = {'status': 'error', 'message': 'Command failed'}
    except Exception as e:
        dependencies['tesseract'] = {'status': 'error', 'message': str(e)}
    
    # Check MongoDB connection (if applicable)
    try:
        from pymongo import MongoClient
        client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'), 
                           serverSelectionTimeoutMS=3000)
        client.admin.command('ismaster')
        dependencies['mongodb'] = {'status': 'healthy', 'connection': 'active'}
        client.close()
    except Exception as e:
        dependencies['mongodb'] = {'status': 'degraded', 'message': str(e), 'fallback': 'in-memory'}
    
    # Check file system permissions
    upload_dir = os.getenv('UPLOAD_FOLDER', 'uploads')
    try:
        os.makedirs(upload_dir, exist_ok=True)
        test_file = os.path.join(upload_dir, '.health_check')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        dependencies['filesystem'] = {'status': 'healthy', 'upload_dir': upload_dir}
    except Exception as e:
        dependencies['filesystem'] = {'status': 'error', 'message': str(e)}
    
    return dependencies

def create_detailed_health_response():
    start_time = datetime.utcnow()
    
    # Basic health info
    health_data = {
        'service': 'GenHealth.AI Clinical Document Processing API',
        'version': '1.0.0',
        'status': 'healthy',
        'environment': os.getenv('FLASK_ENV', 'production'),
        'timestamp': start_time.isoformat(),
        'uptime': get_uptime(),
        'deployment': {
            'platform': 'AWS',
            'region': os.getenv('AWS_REGION', 'us-east-1'),
            'instance_type': os.getenv('AWS_INSTANCE_TYPE', 'unknown')
        }
    }
    
    # Add system metrics
    health_data['system_health'] = get_system_health()
    
    # Add dependency checks
    health_data['dependencies'] = check_dependencies()
    
    # Determine overall status
    dep_statuses = [dep.get('status', 'unknown') for dep in health_data['dependencies'].values()]
    if any(status == 'error' for status in dep_statuses):
        health_data['status'] = 'degraded'
    elif any(status == 'degraded' for status in dep_statuses):
        health_data['status'] = 'degraded'
    
    # Add response time
    health_data['response_time_ms'] = int((datetime.utcnow() - start_time).total_seconds() * 1000)
    
    return health_data

def get_uptime():
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            return str(timedelta(seconds=int(uptime_seconds)))
    except:
        return "unknown"
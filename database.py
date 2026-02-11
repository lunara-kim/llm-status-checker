import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os

# 데이터 디렉토리 생성
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "status_history.db")

def init_db():
    """데이터베이스 초기화"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS status_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            model_name TEXT NOT NULL,
            status TEXT NOT NULL,
            response_time REAL,
            error TEXT
        )
    """)
    
    # 인덱스 생성 (쿼리 성능 향상)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp 
        ON status_history(timestamp DESC)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_model_timestamp 
        ON status_history(model_name, timestamp DESC)
    """)
    
    conn.commit()
    conn.close()

def save_status(model_name: str, status: str, response_time: float = None, error: str = None):
    """상태 기록 저장"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO status_history (model_name, status, response_time, error)
        VALUES (?, ?, ?, ?)
    """, (model_name, status, response_time, error))
    
    conn.commit()
    conn.close()

def get_history(hours: int = 24) -> Dict[str, List[Dict[str, Any]]]:
    """최근 N시간 동안의 히스토리 조회"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    cursor.execute("""
        SELECT 
            timestamp,
            model_name,
            status,
            response_time,
            error
        FROM status_history
        WHERE timestamp > ?
        ORDER BY timestamp ASC
    """, (cutoff_time.isoformat(),))
    
    rows = cursor.fetchall()
    conn.close()
    
    # 모델별로 그룹화
    history = {}
    for row in rows:
        model = row['model_name']
        if model not in history:
            history[model] = []
        
        history[model].append({
            'timestamp': row['timestamp'],
            'status': row['status'],
            'response_time': row['response_time'],
            'error': row['error']
        })
    
    return history

def get_uptime_stats(hours: int = 24) -> Dict[str, Dict[str, Any]]:
    """모델별 가동률 통계"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    cursor.execute("""
        SELECT 
            model_name,
            COUNT(*) as total_checks,
            SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
            AVG(CASE WHEN status = 'success' THEN response_time END) as avg_response_time,
            MIN(CASE WHEN status = 'success' THEN response_time END) as min_response_time,
            MAX(CASE WHEN status = 'success' THEN response_time END) as max_response_time
        FROM status_history
        WHERE timestamp > ?
        GROUP BY model_name
    """, (cutoff_time.isoformat(),))
    
    rows = cursor.fetchall()
    conn.close()
    
    stats = {}
    for row in rows:
        model_name = row[0]
        total = row[1]
        success = row[2]
        
        stats[model_name] = {
            'total_checks': total,
            'success_count': success,
            'uptime_percent': round((success / total * 100) if total > 0 else 0, 2),
            'avg_response_time': round(row[3], 2) if row[3] else None,
            'min_response_time': round(row[4], 2) if row[4] else None,
            'max_response_time': round(row[5], 2) if row[5] else None
        }
    
    return stats

def cleanup_old_data(days: int = 7):
    """오래된 데이터 정리"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cutoff_time = datetime.now() - timedelta(days=days)
    
    cursor.execute("""
        DELETE FROM status_history
        WHERE timestamp < ?
    """, (cutoff_time.isoformat(),))
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    return deleted

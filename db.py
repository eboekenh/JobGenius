import sqlite3
from datetime import datetime
from typing import Optional, List, Dict

DB_PATH = 'jobgenius.db'

def get_conn(path: str = DB_PATH):
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables(path: str = DB_PATH):
    conn = get_conn(path)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        row_index INTEGER,
        raw_requirements TEXT,
        created_at TEXT,
        status TEXT
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS requirements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER,
        requirement_text TEXT,
        normalized_text TEXT,
        FOREIGN KEY(job_id) REFERENCES jobs(id)
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER,
        model TEXT,
        prompt TEXT,
        result_text TEXT,
        created_at TEXT,
        FOREIGN KEY(job_id) REFERENCES jobs(id)
    )
    ''')
    conn.commit()
    conn.close()

def insert_job(source: str, row_index: Optional[int], raw_requirements: str, status: str = 'new', path: str = DB_PATH) -> int:
    conn = get_conn(path)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute('''INSERT INTO jobs (source, row_index, raw_requirements, created_at, status)
                   VALUES (?, ?, ?, ?, ?)''', (source, row_index, raw_requirements, now, status))
    job_id = cur.lastrowid
    conn.commit()
    conn.close()
    return job_id

def insert_requirement(job_id: int, requirement_text: str, normalized_text: Optional[str] = None, path: str = DB_PATH) -> int:
    conn = get_conn(path)
    cur = conn.cursor()
    cur.execute('''INSERT INTO requirements (job_id, requirement_text, normalized_text)
                   VALUES (?, ?, ?)''', (job_id, requirement_text, normalized_text))
    req_id = cur.lastrowid
    conn.commit()
    conn.close()
    return req_id

def insert_analysis(job_id: int, model: str, prompt: str, result_text: str, path: str = DB_PATH) -> int:
    conn = get_conn(path)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute('''INSERT INTO analyses (job_id, model, prompt, result_text, created_at)
                   VALUES (?, ?, ?, ?, ?)''', (job_id, model, prompt, result_text, now))
    aid = cur.lastrowid
    conn.commit()
    conn.close()
    return aid

def list_jobs(path: str = DB_PATH) -> List[Dict]:
    conn = get_conn(path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM jobs ORDER BY created_at DESC')
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_job(job_id: int, path: str = DB_PATH) -> Optional[Dict]:
    conn = get_conn(path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_analyses_for_job(job_id: int, path: str = DB_PATH) -> List[Dict]:
    conn = get_conn(path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM analyses WHERE job_id = ? ORDER BY created_at DESC', (job_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

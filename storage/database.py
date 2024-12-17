# File: storage/database.py
# Database Management Module for MindMap Pro

import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
import os

class DatabaseManager:
    def __init__(self, db_path: str = "mindmap_pro.db"):
        self.db_path = db_path
        self.initialize_database()
    
    def initialize_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 사용자 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """)
            
            # 지식맵 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_maps (
                    map_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    subject TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # 개념 노드 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS concept_nodes (
                    node_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    map_id INTEGER,
                    concept TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    level INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (map_id) REFERENCES knowledge_maps (map_id)
                )
            """)
            
            # 개념 연결 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS concept_edges (
                    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    map_id INTEGER,
                    source_node_id INTEGER,
                    target_node_id INTEGER,
                    relationship_type TEXT,
                    strength FLOAT DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (map_id) REFERENCES knowledge_maps (map_id),
                    FOREIGN KEY (source_node_id) REFERENCES concept_nodes (node_id),
                    FOREIGN KEY (target_node_id) REFERENCES concept_nodes (node_id)
                )
            """)
            
            # 학습 기록 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS study_records (
                    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    subject TEXT NOT NULL,
                    study_time INTEGER NOT NULL,  -- in minutes
                    score FLOAT,
                    stress_level INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # 실수 기록 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mistake_records (
                    mistake_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    subject TEXT NOT NULL,
                    mistake_type TEXT NOT NULL,
                    problem_difficulty TEXT,
                    time_spent INTEGER,  -- in minutes
                    is_repeated BOOLEAN,
                    stress_level INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            conn.commit()

    def add_user(self, username: str, password_hash: str) -> int:
        """새로운 사용자 추가"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            conn.commit()
            return cursor.lastrowid

    def get_user(self, username: str) -> Dict:
        """사용자 정보 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            )
            result = cursor.fetchone()
            if result:
                return {
                    'user_id': result[0],
                    'username': result[1],
                    'password_hash': result[2],
                    'created_at': result[3],
                    'last_login': result[4]
                }
            return None

    def add_knowledge_map(self, user_id: int, subject: str) -> int:
        """새로운 지식맵 추가"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO knowledge_maps (user_id, subject) VALUES (?, ?)",
                (user_id, subject)
            )
            conn.commit()
            return cursor.lastrowid

    def add_concept_node(self, map_id: int, concept: str, subject: str, level: int = 1) -> int:
        """새로운 개념 노드 추가"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO concept_nodes (map_id, concept, subject, level) VALUES (?, ?, ?, ?)",
                (map_id, concept, subject, level)
            )
            conn.commit()
            return cursor.lastrowid

    def add_concept_edge(self, map_id: int, source_id: int, target_id: int,
                        relationship_type: str = None, strength: float = 1.0) -> int:
        """개념 간 연결 추가"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO concept_edges 
                   (map_id, source_node_id, target_node_id, relationship_type, strength)
                   VALUES (?, ?, ?, ?, ?)""",
                (map_id, source_id, target_id, relationship_type, strength)
            )
            conn.commit()
            return cursor.lastrowid

    def get_knowledge_map(self, map_id: int) -> Dict:
        """지식맵 전체 데이터 조회"""
        with sqlite3.connect(self.db_path) as conn:
            # 노드 조회
            nodes = pd.read_sql_query(
                "SELECT * FROM concept_nodes WHERE map_id = ?",
                conn,
                params=(map_id,)
            )
            
            # 엣지 조회
            edges = pd.read_sql_query(
                "# File: storage/database.py (continued)

                "SELECT * FROM concept_edges WHERE map_id = ?",
                conn,
                params=(map_id,)
            )
            
            return {
                'nodes': nodes.to_dict('records'),
                'edges': edges.to_dict('records')
            }

    def add_study_record(self, user_id: int, subject: str, study_time: int,
                        score: float = None, stress_level: int = None) -> int:
        """학습 기록 추가"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO study_records 
                   (user_id, subject, study_time, score, stress_level)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, subject, study_time, score, stress_level)
            )
            conn.commit()
            return cursor.lastrowid

    def add_mistake_record(self, user_id: int, subject: str, mistake_type: str,
                          problem_difficulty: str, time_spent: int,
                          is_repeated: bool, stress_level: int) -> int:
        """실수 기록 추가"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO mistake_records 
                   (user_id, subject, mistake_type, problem_difficulty,
                    time_spent, is_repeated, stress_level)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (user_id, subject, mistake_type, problem_difficulty,
                 time_spent, is_repeated, stress_level)
            )
            conn.commit()
            return cursor.lastrowid

    def get_study_statistics(self, user_id: int, start_date: datetime = None,
                           end_date: datetime = None) -> Dict[str, Any]:
        """학습 통계 분석"""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT 
                    subject,
                    COUNT(*) as study_sessions,
                    SUM(study_time) as total_time,
                    AVG(study_time) as avg_time,
                    AVG(score) as avg_score,
                    AVG(stress_level) as avg_stress
                FROM study_records
                WHERE user_id = ?
            """
            params = [user_id]
            
            if start_date:
                query += " AND created_at >= ?"
                params.append(start_date)
            if end_date:
                query += " AND created_at <= ?"
                params.append(end_date)
                
            query += " GROUP BY subject"
            
            return pd.read_sql_query(query, conn, params=params).to_dict('records')

    def get_mistake_patterns(self, user_id: int, start_date: datetime = None,
                           end_date: datetime = None) -> Dict[str, Any]:
        """실수 패턴 분석"""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT 
                    subject,
                    mistake_type,
                    COUNT(*) as frequency,
                    AVG(time_spent) as avg_time_spent,
                    SUM(CASE WHEN is_repeated THEN 1 ELSE 0 END) as repeated_count,
                    AVG(stress_level) as avg_stress
                FROM mistake_records
                WHERE user_id = ?
            """
            params = [user_id]
            
            if start_date:
                query += " AND created_at >= ?"
                params.append(start_date)
            if end_date:
                query += " AND created_at <= ?"
                params.append(end_date)
                
            query += " GROUP BY subject, mistake_type"
            
            return pd.read_sql_query(query, conn, params=params).to_dict('records')

    def get_learning_efficiency(self, user_id: int) -> Dict[str, float]:
        """학습 효율성 분석"""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT 
                    subject,
                    AVG(score / study_time) as efficiency_score,
                    AVG(CASE WHEN stress_level <= 3 THEN score ELSE 0 END) /
                    AVG(CASE WHEN stress_level <= 3 THEN study_time ELSE NULL END) 
                    as optimal_efficiency
                FROM study_records
                WHERE user_id = ? AND study_time > 0 AND score IS NOT NULL
                GROUP BY subject
            """
            return pd.read_sql_query(query, conn, params=[user_id]).to_dict('records')

    def backup_database(self, backup_path: str = None) -> str:
        """데이터베이스 백업"""
        if not backup_path:
            backup_path = f"backup_mindmap_pro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            
        with sqlite3.connect(self.db_path) as conn:
            backup = sqlite3.connect(backup_path)
            conn.backup(backup)
            backup.close()
            
        return backup_path

    def restore_database(self, backup_path: str) -> bool:
        """데이터베이스 복원"""
        try:
            with sqlite3.connect(backup_path) as backup:
                conn = sqlite3.connect(self.db_path)
                backup.backup(conn)
                conn.close()
                return True
        except Exception as e:
            print(f"Database restoration failed: {str(e)}")
            return False

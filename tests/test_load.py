# File: tests/test_load.py
# Load Testing Scenarios for MindMap Pro

import pytest
import concurrent.futures
import time
import random
from datetime import datetime, timedelta
from modules.knowledge_map import KnowledgeMap
from modules.learning_analysis import LearningAnalysis
from modules.mistake_pattern import MistakePatternAnalysis
from storage.database import DatabaseManager
from storage.cache_manager import CacheManager

class TestLoadScenarios:
    @pytest.fixture
    def setup_system(self):
        """시스템 컴포넌트 초기화"""
        return {
            "db": DatabaseManager(":memory:"),
            "cache": CacheManager(host="localhost", port=6379, db=0),
            "knowledge_map": KnowledgeMap(),
            "learning_analysis": LearningAnalysis(),
            "mistake_analysis": MistakePatternAnalysis()
        }

    def simulate_user_activity(self, system, user_id: int):
        """단일 사용자 활동 시뮬레이션"""
        try:
            # 지식맵 작업
            knowledge_map = system["knowledge_map"]
            knowledge_map.G.add_node(f"개념_{user_id}", subject="수학")
            
            # 학습 데이터 생성
            study_record = {
                "subject": random.choice(["수학", "물리", "화학", "영어", "국어"]),
                "study_time": random.randint(30, 180),
                "score": random.randint(70, 100),
                "stress_level": random.randint(1, 5)
            }
            system["db"].add_study_record(user_id, **study_record)
            
            # 캐시 조회 및 저장
            system["cache"].set_user_data(user_id, study_record)
            cached_data = system["cache"].get_user_data(user_id)
            
            return True
        except Exception as e:
            print(f"Error in user activity simulation: {str(e)}")
            return False

    def test_concurrent_users(self, setup_system):
        """동시 사용자 처리 테스트"""
        system = setup_system
        num_users = 100
        
        start_time = time.time()
        success_count = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [
                executor.submit(self.simulate_user_activity, system, user_id)
                for user_id in range(1, num_users + 1)
            ]
            
            for future in concurrent.futures.as_completed(futures):
                if future.result():
                    success_count += 1
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 성능 기준 검증
        assert success_count >= 0.95 * num_users  # 95% 이상 성공
        assert execution_time < 30  # 30초 이내 완료

    def test_data_intensive_operations(self, setup_system):
        """대용량 데이터 처리 테스트"""
        system = setup_system
        num_records = 10000
        
        # 대량의 학습 데이터 생성
        start_time = time.time()
        
        study_records = [
            {
                "user_id": random.randint(1, 100),
                "subject": random.choice(["수학", "물리", "화학", "영어", "국어"]),
                "study_time": random.randint(30, 180),
                "score": random.randint(70, 100),
                "stress_level": random.randint(1, 5)
            }
            for _ in range(num_records)
        ]
        
        # 벌크 데이터 처리
        for record in study_records:
            system["db"].add_study_record(**record)
        
        end_time = time.time()
        data_processing_time = end_time - start_time
        
        # 성능 기준 검증
        assert data_processing_time < 60  # 60초 이내 완료

    def test_cache_performance(self, setup_system):
        """캐시 성능 테스트"""
        system = setup_system
        num_operations = 1000
        
        start_time = time.time()
        success_count = 0
        
        # 캐시 작업 수행
        for i in range(num_operations):
            try:
                # 캐시 쓰기
                system["cache"].set_user_data(
                    i,
                    {"test_data": f"value_{i}"},
                    expire_time=300
                )
                
                # 캐시 읽기
                cached_data = system["cache"].get_user_data(i)
                if cached_data and cached_data["test_data"] == f"value_{i}":
                    success_count += 1
            except Exception:
                continue
        
        end_time = time.time()
        cache_operation_time = end_time - start_time
        
        # 성능 기준 검증
        assert success_count >= 0.98 * num_operations  # 98% 이상 성공
        assert cache_operation_time < 10  # 10초 이내 완료

    def test_system_stability(self, setup_system):
        """시스템 안정성 테스트"""
        system = setup_system
        test_duration = 300  # 5분
        check_interval = 10  # 10초
        
        start_time = time.time()
        error_count = 0
        
        while time.time() - start_time < test_duration:
            try:
                # 다양한 시스템 작업 수행
                self.simulate_user_activity(system, random.randint(1, 100))
                time.sleep(check_interval)
            except Exception:
                error_count += 1
        
        # 안정성 기준 검증
        assert error_count == 0  # 테스트 기간 동안 오류 없음

    def test_recovery_scenarios(self, setup_system):
        """장애 복구 시나리오 테스트"""
        system = setup_system
        
        # 캐시 서버 다운 시뮬레이션
        system["cache"].redis_client.connection_pool.disconnect()
        
        # 복구 시도
        retry_count = 0
        max_retries = 3
        success = False
        
        while retry_count < max_retries:
            try:
                system["cache"].redis_client.ping()
                success = True
                break
            except Exception:
                retry_count += 1
                time.sleep(1)
        
        # 복구 성공 여부 검증
        assert success, "Cache recovery failed"

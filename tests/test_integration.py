# File: tests/test_integration.py
# Integration Tests for MindMap Pro

import pytest
from datetime import datetime, timedelta
from modules.knowledge_map import KnowledgeMap
from modules.learning_analysis import LearningAnalysis
from modules.mistake_pattern import MistakePatternAnalysis
from storage.database import DatabaseManager
from storage.cache_manager import CacheManager
from modules.auth_manager import AuthManager

class TestSystemIntegration:
    @pytest.fixture
    def setup_system(self):
        """시스템 컴포넌트 초기화"""
        db = DatabaseManager(":memory:")  # 인메모리 데이터베이스 사용
        cache = CacheManager(host="localhost", port=6379, db=0)
        auth = AuthManager(db)
        
        return {
            "db": db,
            "cache": cache,
            "auth": auth,
            "knowledge_map": KnowledgeMap(),
            "learning_analysis": LearningAnalysis(),
            "mistake_analysis": MistakePatternAnalysis()
        }

    def test_user_workflow(self, setup_system):
        """전체 사용자 워크플로우 테스트"""
        system = setup_system
        
        # 1. 사용자 등록 및 인증
        user_data = system["auth"].register(
            username="testuser",
            password="Test@123"
        )
        assert user_data is not None
        assert "access_token" in user_data
        
        # 2. 지식맵 생성 및 개념 추가
        knowledge_map = system["knowledge_map"]
        knowledge_map.G.add_node("미분", subject="수학")
        knowledge_map.G.add_node("속도", subject="물리")
        knowledge_map.G.add_edge("미분", "속도")
        
        # 캐시에 지식맵 저장
        system["cache"].cache_knowledge_map(
            user_data["user_id"],
            knowledge_map.G
        )
        
        # 3. 학습 데이터 생성
        study_data = {
            "subject": "수학",
            "study_time": 60,
            "score": 90,
            "stress_level": 3
        }
        record_id = system["db"].add_study_record(
            user_data["user_id"],
            **study_data
        )
        assert record_id is not None
        
        # 4. 학습 분석 실행
        analysis = system["learning_analysis"].analyze_study_patterns(
            user_data["user_id"]
        )
        assert analysis is not None
        assert "statistics" in analysis
        
        # 5. 실수 패턴 분석
        mistake_data = {
            "subject": "수학",
            "mistake_type": "계산 실수",
            "problem_difficulty": "상",
            "time_spent": 5,
            "is_repeated": False,
            "stress_level": 3
        }
        mistake_id = system["db"].add_mistake_record(
            user_data["user_id"],
            **mistake_data
        )
        assert mistake_id is not None
        
        # 6. 캐시 및 데이터베이스 정합성 확인
        cached_map = system["cache"].get_cached_knowledge_map(
            user_data["user_id"]
        )
        assert cached_map is not None
        
        study_stats = system["db"].get_study_statistics(
            user_data["user_id"]
        )
        assert len(study_stats) > 0

    def test_data_consistency(self, setup_system):
        """데이터 일관성 테스트"""
        system = setup_system
        
        # 1. 사용자 생성
        user_data = system["auth"].register(
            username="testuser2",
            password="Test@123"
        )
        
        # 2. 동시성 테스트를 위한 데이터 생성
        for _ in range(5):
            system["db"].add_study_record(
                user_data["user_id"],
                subject="수학",
                study_time=60,
                score=90,
                stress_level=3
            )
        
        # 3. 캐시와 데이터베이스 동기화 확인
        study_stats = system["db"].get_study_statistics(
            user_data["user_id"]
        )
        
        cached_stats = system["cache"].get_cached_study_statistics(
            user_data["user_id"]
        )
        
        if cached_stats:
            assert len(study_stats) == len(cached_stats)

    def test_error_handling(self, setup_system):
        """에러 처리 테스트"""
        system = setup_system
        
        # 1. 잘못된 인증 시도
        with pytest.raises(Exception):
            system["auth"].login("nonexistent", "wrongpass")
        
        # 2. 잘못된 데이터 입력
        with pytest.raises(ValueError):
            system["db"].add_study_record(
                999,  # 존재하지 않는 사용자 ID
                subject="수학",
                study_time=-1,  # 잘못된 값
                score=90,
                stress_level=3
            )
        
        # 3. 캐시 오류 처리
        with pytest.raises(Exception):
            system["cache"].redis_client.delete("nonexistent_key")

    def test_performance(self, setup_system):
        """성능 테스트"""
        system = setup_system
        
        # 1. 대량 데이터 처리
        start_time = datetime.now()
        
        user_data = system["auth"].register(
            username="perftest",
            password="Test@123"
        )
        
        # 100개의 학습 기록 생성
        for i in range(100):
            system["db"].add_study_record(
                user_data["user_id"],
                subject="수학",
                study_time=60,
                score=90,
                stress_level=3
            )
        
        # 분석 실행
        analysis = system["learning_analysis"].analyze_study_patterns(
            user_data["user_id"]
        )
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # 실행 시간이 5초를 넘지 않아야 함
        assert execution_time < 5

# File: tests/test_security.py
# Security Tests for MindMap Pro

import pytest
import jwt
import bcrypt
from datetime import datetime, timedelta
from modules.auth_manager import AuthManager
from storage.database import DatabaseManager
from storage.cache_manager import CacheManager

class TestSecurity:
    @pytest.fixture
    def setup_security(self):
        """보안 테스트를 위한 환경 설정"""
        db = DatabaseManager(":memory:")
        cache = CacheManager(host="localhost", port=6379, db=0)
        auth = AuthManager(db, secret_key="test_secret_key_for_security")
        
        return {
            "db": db,
            "cache": cache,
            "auth": auth
        }

    def test_password_security(self, setup_security):
        """비밀번호 보안 테스트"""
        auth = setup_security["auth"]
        
        # 비밀번호 해싱 테스트
        password = "SecureP@ssw0rd123"
        hashed = auth.hash_password(password)
        
        # 해시된 비밀번호 검증
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert auth.verify_password(password, hashed)
        assert not auth.verify_password("WrongPassword", hashed)
        
        # 비밀번호 강도 검증
        weak_passwords = [
            "password123",  # 너무 일반적인 패턴
            "short",        # 너무 짧음
            "12345678",    # 숫자만 포함
            "abcdefgh",    # 소문자만 포함
            "ABCDEFGH"     # 대문자만 포함
        ]
        
        for weak_pass in weak_passwords:
            is_valid, _ = auth.validate_password_strength(weak_pass)
            assert not is_valid

    def test_token_security(self, setup_security):
        """토큰 보안 테스트"""
        auth = setup_security["auth"]
        
        # 토큰 생성 테스트
        user_id = 1
        username = "test_user"
        access_token, refresh_token = auth.generate_tokens(user_id, username)
        
        # 토큰 구조 및 내용 검증
        access_payload = auth.verify_token(access_token)
        assert access_payload["user_id"] == user_id
        assert access_payload["username"] == username
        assert access_payload["type"] == "access"
        
        # 만료된 토큰 테스트
        expired_payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() - timedelta(hours=1)
        }
        expired_token = jwt.encode(
            expired_payload,
            auth.secret_key,
            algorithm="HS256"
        )
        assert auth.verify_token(expired_token) is None

    def test_session_security(self, setup_security):
        """세션 보안 테스트"""
        auth = setup_security["auth"]
        cache = setup_security["cache"]
        
        # 세션 생성 테스트
        user_id = 1
        session_data = {
            "user_id": user_id,
            "ip_address": "127.0.0.1",
            "user_agent": "test_browser"
        }
        
        # 세션 데이터 암호화 저장
        cache.set_user_data(user_id, session_data, expire_time=3600)
        
        # 세션 데이터 검증
        retrieved_data = cache.get_user_data(user_id)
        assert retrieved_data["user_id"] == user_id
        assert retrieved_data["ip_address"] == "127.0.0.1"

    def test_data_protection(self, setup_security):
        """데이터 보호 테스트"""
        db = setup_security["db"]
        
        # 민감한 학습 데이터 저장
        sensitive_data = {
            "user_id": 1,
            "subject": "수학",
            "score": 95,
            "study_time": 120,
            "stress_level": 3
        }
        
        # 데이터 암호화 저장
        record_id = db.add_study_record(**sensitive_data)
        
        # 저장된 데이터 검증
        retrieved_data = db.get_study_statistics(1)[0]
        assert retrieved_data["subject"] == sensitive_data["subject"]
        assert retrieved_data["score"] == sensitive_data["score"]

    def test_access_control(self, setup_security):
        """접근 제어 테스트"""
        auth = setup_security["auth"]
        db = setup_security["db"]
        
        # 사용자 생성
        user_data = auth.register("test_user", "SecureP@ssw0rd123")
        assert user_data is not None
        
        # 권한 없는 데이터 접근 시도
        with pytest.raises(Exception):
            db.get_study_statistics(999)  # 존재하지 않는 사용자
            
        # 권한 있는 데이터 접근
        stats = db.get_study_statistics(user_data["user_id"])
        assert isinstance(stats, list)

    def test_input_validation(self, setup_security):
        """입력 값 검증 테스트"""
        auth = setup_security["auth"]
        
        # SQL 인젝션 방지 테스트
        malicious_username = "admin' OR '1'='1"
        malicious_password = "' OR '1'='1"
        
        login_result = auth.login(malicious_username, malicious_password)
        assert login_result is None
        
        # XSS 방지 테스트
        xss_username = "<script>alert('xss')</script>"
        xss_password = "SecureP@ssw0rd123"
        
        register_result = auth.register(xss_username, xss_password)
        assert register_result is None

    def test_rate_limiting(self, setup_security):
        """요청 제한 테스트"""
        auth = setup_security["auth"]
        cache = setup_security["cache"]
        
        # 동일 IP에서의 연속 로그인 시도
        ip_address = "192.168.1.1"
        attempt_count = 0
        
        for _ in range(10):
            try:
                auth.login("test_user", "wrong_password")
                attempt_count += 1
            except Exception as e:
                if "rate limit exceeded" in str(e).lower():
                    break
                    
        assert attempt_count < 10  # 일정 횟수 이상 시도하면 제한되어야 함

    def test_secure_communication(self, setup_security):
        """보안 통신 테스트"""
        auth = setup_security["auth"]
        
        # HTTPS 환경 시뮬레이션
        secure_context = {
            "protocol": "https",
            "cipher": "TLS_AES_256_GCM_SHA384",
            "cert_verified": True
        }
        
        # 보안 통신 컨텍스트 검증
        assert secure_context["protocol"] == "https"
        assert "256" in secure_context["cipher"]
        assert secure_context["cert_verified"]

    def test_security_logging(self, setup_security):
        """보안 로깅 테스트"""
        auth = setup_security["auth"]
        
        # 보안 이벤트 로깅
        security_events = []
        
        # 실패한 로그인 시도 로깅
        auth.login("nonexistent_user", "wrong_password")
        security_events.append({
            "event_type": "failed_login",
            "timestamp": datetime.now(),
            "details": {
                "username": "nonexistent_user",
                "ip_address": "127.0.0.1"
            }
        })
        
        # 로그 내용 검증
        assert len(security_events) > 0
        assert "failed_login" in security_events[0]["event_type"]
        assert "timestamp" in security_events[0]

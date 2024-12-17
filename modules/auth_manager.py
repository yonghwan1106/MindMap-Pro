# File: modules/auth_manager.py
# Authentication Management System for MindMap Pro

import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from storage.database import DatabaseManager

class AuthManager:
    def __init__(self, db_manager: DatabaseManager, secret_key: str = None):
        self.db = db_manager
        self.secret_key = secret_key or secrets.token_hex(32)
        self.token_expiry = timedelta(hours=24)
        self.refresh_token_expiry = timedelta(days=30)

    def hash_password(self, password: str) -> str:
        """비밀번호 해싱"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """비밀번호 검증"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False

    def generate_tokens(self, user_id: int, username: str) -> Tuple[str, str]:
        """액세스 토큰과 리프레시 토큰 생성"""
        # 액세스 토큰 생성
        access_token_payload = {
            'user_id': user_id,
            'username': username,
            'exp': datetime.utcnow() + self.token_expiry,
            'type': 'access'
        }
        access_token = jwt.encode(
            access_token_payload,
            self.secret_key,
            algorithm='HS256'
        )

        # 리프레시 토큰 생성
        refresh_token_payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + self.refresh_token_expiry,
            'type': 'refresh'
        }
        refresh_token = jwt.encode(
            refresh_token_payload,
            self.secret_key,
            algorithm='HS256'
        )

        return access_token, refresh_token

    def verify_token(self, token: str) -> Optional[Dict]:
        """토큰 검증"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """리프레시 토큰을 사용하여 새로운 액세스 토큰 발급"""
        payload = self.verify_token(refresh_token)
        if not payload or payload.get('type') != 'refresh':
            return None

        user_id = payload.get('user_id')
        user = self.db.get_user_by_id(user_id)
        if not user:
            return None

        # 새로운 액세스 토큰 생성
        access_token_payload = {
            'user_id': user_id,
            'username': user['username'],
            'exp': datetime.utcnow() + self.token_expiry,
            'type': 'access'
        }
        return jwt.encode(
            access_token_payload,
            self.secret_key,
            algorithm='HS256'
        )

    def login(self, username: str, password: str) -> Optional[Dict]:
        """사용자 로그인"""
        user = self.db.get_user(username)
        if not user:
            return None

        if not self.verify_password(password, user['password_hash']):
            return None

        # 토큰 생성
        access_token, refresh_token = self.generate_tokens(
            user['user_id'],
            user['username']
        )

        # 로그인 시간 업데이트
        self.db.update_last_login(user['user_id'])

        return {
            'user_id': user['user_id'],
            'username': user['username'],
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    def register(self, username: str, password: str) -> Optional[Dict]:
        """새로운 사용자 등록"""
        # 사용자명 중복 확인
        existing_user = self.db.get_user(username)
        if existing_user:
            return None

        # 비밀번호 해싱 및 사용자 생성
        hashed_password = self.hash_password(password)
        user_id = self.db.add_user(username, hashed_password)

        # 토큰 생성
        access_token, refresh_token = self.generate_tokens(user_id, username)

        return {
            'user_id': user_id,
            'username': username,
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """비밀번호 강도 검증"""
        if len(password) < 8:
            return False, "비밀번호는 최소 8자 이상이어야 합니다."
            
        if not any(c.isupper() for c in password):
            return False, "비밀번호는 최소 하나의 대문자를 포함해야 합니다."
            
        if not any(c.islower() for c in password):
            return False, "비밀번호는 최소 하나의 소문자를 포함해야 합니다."
            
        if not any(c.isdigit() for c in password):
            return False, "비밀번호는 최소 하나의 숫자를 포함해야 합니다."
            
        if not any(c in "!@#$%^&*(),.?\":{}|<>" for c in password):
            return False, "비밀번호는 최소 하나의 특수문자를 포함해야 합니다."
            
        return True, "유효한 비밀번호입니다."

    def change_password(self, user_id: int, old_password: str,
                       new_password: str) -> Tuple[bool, str]:
        """비밀번호 변경"""
        user = self.db.get_user_by_id(user_id)
        if not user:
            return False, "사용자를 찾을 수 없습니다."

        if not self.verify_password(old_password, user['password_hash']):
            return False, "현재 비밀번호가 일치하지 않습니다."

        # 새 비밀번호 유효성 검사
        is_valid, message = self.validate_password_strength(new_password)
        if not is_valid:
            return False, message

        # 새 비밀번호 해싱 및 업데이트
        new_hash = self.hash_password(new_password)
        self.db.update_password(user_id, new_hash)

        return True, "비밀번호가 성공적으로 변경되었습니다."

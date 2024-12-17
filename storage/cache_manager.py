# File: storage/cache_manager.py
# Cache Management System for MindMap Pro

import redis
import json
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import pickle

class CacheManager:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True,
            encoding='utf-8'
        )
        self.binary_redis = redis.Redis(
            host=host,
            port=port,
            db=db
        )
        
    def _get_key(self, prefix: str, identifier: str) -> str:
        """캐시 키 생성"""
        return f"mindmap_pro:{prefix}:{identifier}"

    def set_user_data(self, user_id: int, data: Dict, expire_time: int = 3600) -> bool:
        """사용자 데이터 캐싱"""
        key = self._get_key("user", str(user_id))
        try:
            self.redis_client.setex(
                key,
                expire_time,
                json.dumps(data)
            )
            return True
        except Exception as e:
            print(f"Error caching user data: {str(e)}")
            return False

    def get_user_data(self, user_id: int) -> Optional[Dict]:
        """사용자 데이터 조회"""
        key = self._get_key("user", str(user_id))
        try:
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Error retrieving user data: {str(e)}")
            return None

    def cache_knowledge_map(self, map_id: int, graph_data: Any, expire_time: int = 3600) -> bool:
        """지식맵 데이터 캐싱"""
        key = self._get_key("knowledge_map", str(map_id))
        try:
            self.binary_redis.setex(
                key,
                expire_time,
                pickle.dumps(graph_data)
            )
            return True
        except Exception as e:
            print(f"Error caching knowledge map: {str(e)}")
            return False

    def get_cached_knowledge_map(self, map_id: int) -> Optional[Any]:
        """캐시된 지식맵 조회"""
        key = self._get_key("knowledge_map", str(map_id))
        try:
            data = self.binary_redis.get(key)
            return pickle.loads(data) if data else None
        except Exception as e:
            print(f"Error retrieving knowledge map: {str(e)}")
            return None

    def cache_analysis_results(self, user_id: int, analysis_type: str,
                             results: Dict, expire_time: int = 1800) -> bool:
        """분석 결과 캐싱"""
        key = self._get_key(f"analysis:{analysis_type}", str(user_id))
        try:
            self.redis_client.setex(
                key,
                expire_time,
                json.dumps(results)
            )
            return True
        except Exception as e:
            print(f"Error caching analysis results: {str(e)}")
            return False

    def get_cached_analysis(self, user_id: int, analysis_type: str) -> Optional[Dict]:
        """캐시된 분석 결과 조회"""
        key = self._get_key(f"analysis:{analysis_type}", str(user_id))
        try:
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Error retrieving analysis results: {str(e)}")
            return None

    def cache_study_statistics(self, user_id: int, stats: Dict,
                             expire_time: int = 3600) -> bool:
        """학습 통계 캐싱"""
        key = self._get_key("study_stats", str(user_id))
        try:
            self.redis_client.setex(
                key,
                expire_time,
                json.dumps(stats)
            )
            return True
        except Exception as e:
            print(f"Error caching study statistics: {str(e)}")
            return False

    def get_cached_study_statistics(self, user_id: int) -> Optional[Dict]:
        """캐시된 학습 통계 조회"""
        key = self._get_key("study_stats", str(user_id))
        try:
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Error retrieving study statistics: {str(e)}")
            return None

    def invalidate_user_cache(self, user_id: int) -> bool:
        """사용자 관련 캐시 무효화"""
        try:
            pattern = self._get_key("*", str(user_id))
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            print(f"Error invalidating user cache: {str(e)}")
            return False

    def clear_all_cache(self) -> bool:
        """전체 캐시 삭제"""
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            print(f"Error clearing cache: {str(e)}")
            return False

    def get_cache_stats(self) -> Dict[str, Any]:
        """캐시 상태 통계"""
        try:
            info = self.redis_client.info()
            return {
                'used_memory': info['used_memory_human'],
                'connected_clients': info['connected_clients'],
                'total_keys': self.redis_client.dbsize(),
                'uptime_days': info['uptime_in_days']
            }
        except Exception as e:
            print(f"Error getting cache stats: {str(e)}")
            return {}

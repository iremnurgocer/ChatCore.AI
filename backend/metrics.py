# -*- coding: utf-8 -*-
"""
Monitoring ve Metrics Modülü

Bu modül sistem metriklerini toplar ve expose eder.
Prometheus metrics formatında hazırlanmıştır.
"""
from typing import Dict, Any
from datetime import datetime
from collections import defaultdict
import threading

class MetricsCollector:
    """Sistem metriklerini toplayan sınıf"""
    
    def __init__(self):
        self.request_count = defaultdict(int)
        self.error_count = defaultdict(int)
        self.response_times = defaultdict(list)
        self.active_users = set()
        self.lock = threading.Lock()
    
    def record_request(self, endpoint: str, method: str, response_time: float, status_code: int):
        """Request metriği kaydet"""
        with self.lock:
            key = f"{method} {endpoint}"
            self.request_count[key] += 1
            
            if status_code >= 400:
                self.error_count[key] += 1
            
            self.response_times[key].append(response_time)
            
            # Son 1000 response time'ı tut
            if len(self.response_times[key]) > 1000:
                self.response_times[key] = self.response_times[key][-1000:]
    
    def record_active_user(self, user_id: str):
        """Aktif kullanıcı kaydet"""
        with self.lock:
            self.active_users.add(user_id)
    
    def remove_active_user(self, user_id: str):
        """Aktif kullanıcıyı kaldır"""
        with self.lock:
            self.active_users.discard(user_id)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Metrikleri getir (Prometheus formatına yakın)"""
        with self.lock:
            metrics = {
                "requests_total": sum(self.request_count.values()),
                "errors_total": sum(self.error_count.values()),
                "active_users": len(self.active_users),
                "endpoints": {}
            }
            
            # Endpoint bazlı metrikler
            for endpoint, count in self.request_count.items():
                error_count = self.error_count.get(endpoint, 0)
                response_times = self.response_times.get(endpoint, [])
                
                avg_response_time = sum(response_times) / len(response_times) if response_times else 0
                p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)] if len(response_times) > 0 else 0
                
                metrics["endpoints"][endpoint] = {
                    "requests": count,
                    "errors": error_count,
                    "success_rate": ((count - error_count) / count * 100) if count > 0 else 0,
                    "avg_response_time_ms": avg_response_time * 1000,
                    "p95_response_time_ms": p95_response_time * 1000
                }
            
            return metrics

# Global metrics collector
metrics_collector = MetricsCollector()


# -*- coding: utf-8 -*-
"""
Analytics ve İstatistik Modülü

Bu modül API kullanım istatistiklerini takip eder ve analiz eder.
Endpoint çağrı sayıları, hata oranları, yanıt süreleri gibi metrikleri kaydeder.

Ne İşe Yarar:
- API endpoint kullanım istatistikleri
- Hata oranları ve kategorileri
- Ortalama yanıt süreleri
- Başarılı/başarısız istek sayıları
- Zaman bazlı trend analizi

Kullanım:
- analytics.record_request() - İstek kaydet
- analytics.record_error() - Hata kaydet
- analytics.get_stats() - İstatistikleri getir
"""
from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict
import threading

class Analytics:
    """
    API kullanım istatistiklerini takip eden Analytics sınıfı

    Thread-safe implementasyon, race condition'ları önlemek için lock kullanır
    """
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
        self.endpoint_stats = defaultdict(int)
        self.error_log: List[Dict] = []
        self.daily_requests = defaultdict(int)
        self.lock = threading.Lock()
    
    def record_request(self, endpoint: str, response_time: float, success: bool = True):
        """
        Yeni bir API isteğini kaydeder
        
        Args:
            endpoint: API endpoint yolu
            response_time: İstek işleme süresi (saniye cinsinden)
            success: İsteğin başarılı olup olmadığı
        """
        with self.lock:
            self.request_count += 1
            self.total_response_time += response_time
            self.endpoint_stats[endpoint] += 1
            today = datetime.now().date().isoformat()
            self.daily_requests[today] += 1
            
            if not success:
                self.error_count += 1
    
    def record_error(self, endpoint: str, error_type: str, error_message: str):
        """
        Hata oluşumunu kaydeder
        
        Args:
            endpoint: Hatanın oluştuğu API endpoint'i
            error_type: Hata tipi (exception class adı)
            error_message: Hata mesajı
        """
        with self.lock:
            self.error_log.append({
                "timestamp": datetime.now().isoformat(),
                "endpoint": endpoint,
                "error_type": error_type,
                "error_message": error_message
            })
            # Son 100 hatayı sakla
            if len(self.error_log) > 100:
                self.error_log = self.error_log[-100:]
    
    def get_stats(self) -> Dict:
        """
        Mevcut analytics istatistiklerini getirir
        
        Returns:
            İstek sayıları, hata oranları, yanıt süreleri vs. içeren dictionary
        """
        with self.lock:
            avg_response_time = (
                self.total_response_time / self.request_count 
                if self.request_count > 0 else 0
            )
            
            return {
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "success_rate": (
                    (self.request_count - self.error_count) / self.request_count * 100 
                    if self.request_count > 0 else 0
                ),
                "average_response_time_ms": avg_response_time * 1000,
                "endpoint_breakdown": dict(self.endpoint_stats),
                "daily_requests": dict(self.daily_requests),
                "recent_errors": self.error_log[-10:]  # Son 10 hata
            }
    
    def reset(self):
        """
        Tüm istatistikleri sıfırlar

        Tüm sayacıları ve logları temizler. Test veya periyodik sıfırlamalar için kullanılır.
        """
        with self.lock:
            self.request_count = 0
            self.error_count = 0
            self.total_response_time = 0.0
            self.endpoint_stats.clear()
            self.error_log.clear()
            self.daily_requests.clear()

# Global analytics instance
analytics = Analytics()

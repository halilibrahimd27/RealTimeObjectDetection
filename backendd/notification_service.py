"""
Push Notification Service
Firebase Cloud Messaging (FCM) ve Pushover ile mobil bildirim gönderme servisi
"""

import json
import os
import requests
from typing import Optional, List, Dict
from dataclasses import dataclass
from datetime import datetime

# Firebase Admin SDK - opsiyonel
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("ℹ️ Firebase Admin SDK yüklü değil (opsiyonel)")

# Pushover Ayarları - .env dosyasından veya direkt buradan
PUSHOVER_USER_KEY = os.environ.get('PUSHOVER_USER_KEY', '')
PUSHOVER_API_TOKEN = os.environ.get('PUSHOVER_API_TOKEN', '')
PUSHOVER_ENABLED = bool(PUSHOVER_USER_KEY and PUSHOVER_API_TOKEN)

if PUSHOVER_ENABLED:
    print("✅ Pushover bildirimleri aktif")
else:
    print("⚠️ Pushover yapılandırılmamış. Mobil bildirimler için:")
    print("   PUSHOVER_USER_KEY ve PUSHOVER_API_TOKEN ayarlayın")


@dataclass
class NotificationPayload:
    """Bildirim içeriği"""
    title: str
    body: str
    image_url: Optional[str] = None
    data: Optional[Dict] = None


class PushoverService:
    """Pushover ile iPhone/Android'e bildirim gönderme"""
    
    API_URL = "https://api.pushover.net/1/messages.json"
    
    def __init__(self, user_key: str, api_token: str):
        self.user_key = user_key
        self.api_token = api_token
    
    def send(self, title: str, message: str, priority: int = 0, sound: str = "pushover") -> Dict:
        """
        Pushover bildirimi gönder
        
        Args:
            title: Bildirim başlığı
            message: Bildirim içeriği
            priority: -2 (sessiz) ile 2 (acil) arası
            sound: Bildirim sesi (pushover, bike, bugle, cashregister, classical, cosmic, etc.)
        
        Returns:
            API yanıtı
        """
        try:
            payload = {
                "token": self.api_token,
                "user": self.user_key,
                "title": title,
                "message": message,
                "priority": priority,
                "sound": sound
            }
            
            response = requests.post(self.API_URL, data=payload, timeout=10)
            result = response.json()
            
            if response.status_code == 200 and result.get("status") == 1:
                print(f"📱 Pushover bildirim gönderildi: {title}")
                return {"success": True, "message": "Bildirim gönderildi"}
            else:
                print(f"❌ Pushover hatası: {result}")
                return {"success": False, "message": str(result.get("errors", "Bilinmeyen hata"))}
                
        except Exception as e:
            print(f"❌ Pushover bağlantı hatası: {e}")
            return {"success": False, "message": str(e)}


class NotificationService:
    """
    Push Notification servisi
    Pushover ve Firebase Cloud Messaging kullanarak mobil cihazlara bildirim gönderir
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if NotificationService._initialized:
            return
            
        self.firebase_app = None
        self.pushover = None
        self.device_tokens: List[str] = []
        self._load_tokens()
        
        # Pushover'ı başlat
        if PUSHOVER_ENABLED:
            self.pushover = PushoverService(PUSHOVER_USER_KEY, PUSHOVER_API_TOKEN)
        
        # Firebase'i başlat
        if FIREBASE_AVAILABLE:
            self._init_firebase()
        
        NotificationService._initialized = True
    
    def _init_firebase(self):
        """Firebase Admin SDK'yı başlat"""
        try:
            # Firebase credentials dosyası
            cred_path = os.path.join(os.path.dirname(__file__), 'firebase-credentials.json')
            
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                self.firebase_app = firebase_admin.initialize_app(cred)
                print("✅ Firebase başarıyla başlatıldı")
            else:
                print("ℹ️ Firebase credentials dosyası bulunamadı (opsiyonel)")
        except Exception as e:
            print(f"❌ Firebase başlatma hatası: {e}")
    
    def _load_tokens(self):
        """Kayıtlı device token'ları yükle"""
        tokens_file = os.path.join(os.path.dirname(__file__), 'device_tokens.json')
        try:
            if os.path.exists(tokens_file):
                with open(tokens_file, 'r') as f:
                    data = json.load(f)
                    self.device_tokens = data.get('tokens', [])
                    print(f"📱 {len(self.device_tokens)} kayıtlı cihaz token'ı yüklendi")
        except Exception as e:
            print(f"Token yükleme hatası: {e}")
            self.device_tokens = []
    
    def _save_tokens(self):
        """Device token'ları kaydet"""
        tokens_file = os.path.join(os.path.dirname(__file__), 'device_tokens.json')
        try:
            with open(tokens_file, 'w') as f:
                json.dump({'tokens': self.device_tokens, 'updated': datetime.now().isoformat()}, f)
        except Exception as e:
            print(f"Token kaydetme hatası: {e}")
    
    def register_token(self, token: str) -> bool:
        """Yeni device token kaydet"""
        if token and token not in self.device_tokens:
            self.device_tokens.append(token)
            self._save_tokens()
            print(f"✅ Yeni cihaz kaydedildi. Toplam: {len(self.device_tokens)}")
            return True
        return False
    
    def unregister_token(self, token: str) -> bool:
        """Device token'ı sil"""
        if token in self.device_tokens:
            self.device_tokens.remove(token)
            self._save_tokens()
            return True
        return False
    
    def send_detection_notification(self, detected_objects: Dict[str, int], image_url: Optional[str] = None) -> Dict:
        """
        Nesne tespiti sonucunda bildirim gönder
        
        Args:
            detected_objects: {"insan": 2, "laptop": 1} gibi tespit edilen nesneler
            image_url: Tespit edilen görselin URL'i (opsiyonel)
        
        Returns:
            Gönderim sonucu
        """
        if not detected_objects:
            return {"success": False, "message": "Nesne tespit edilmedi"}
        
        # Bildirim içeriği oluştur
        total_objects = sum(detected_objects.values())
        object_list = ", ".join([f"{count} {name}" for name, count in detected_objects.items()])
        
        title = f"🎯 {total_objects} Nesne Tespit Edildi!"
        body = f"Tespit: {object_list}"
        
        results = {
            "pushover": None,
            "firebase": None,
            "success": False
        }
        
        # Pushover ile iPhone/Android'e gönder
        if self.pushover:
            results["pushover"] = self.pushover.send(title, body, priority=0, sound="magic")
            if results["pushover"].get("success"):
                results["success"] = True
        
        # Firebase ile de gönder (varsa)
        payload = NotificationPayload(
            title=title,
            body=body,
            image_url=image_url,
            data={
                "type": "detection",
                "objects": json.dumps(detected_objects),
                "timestamp": datetime.now().isoformat()
            }
        )
        
        firebase_result = self._send_firebase_notification(payload)
        results["firebase"] = firebase_result
        if firebase_result.get("success"):
            results["success"] = True
        
        if not results["success"]:
            results["message"] = "Bildirim gönderilemedi (Pushover/Firebase yapılandırılmamış)"
        else:
            results["message"] = "Bildirim gönderildi"
            
        return results
    
    def _send_firebase_notification(self, payload: NotificationPayload, tokens: Optional[List[str]] = None) -> Dict:
        """Firebase ile bildirim gönder"""
        target_tokens = tokens or self.device_tokens
        
        if not target_tokens:
            return {"success": False, "message": "Kayıtlı cihaz yok"}
        
        if not FIREBASE_AVAILABLE or not self.firebase_app:
            return {"success": False, "message": "Firebase yapılandırılmamış", "simulated": True}
        
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=payload.title,
                    body=payload.body,
                    image=payload.image_url
                ),
                data=payload.data or {},
                tokens=target_tokens
            )
            
            response = messaging.send_multicast(message)
            return {
                "success": True,
                "message": f"{response.success_count} cihaza gönderildi",
                "success_count": response.success_count,
                "failure_count": response.failure_count
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def send_notification(self, payload: NotificationPayload, tokens: Optional[List[str]] = None) -> Dict:
        """
        Bildirim gönder
        
        Args:
            payload: Bildirim içeriği
            tokens: Hedef cihaz token'ları (None ise tüm kayıtlı cihazlara gönderir)
        
        Returns:
            Gönderim sonucu
        """
        target_tokens = tokens or self.device_tokens
        
        if not target_tokens:
            return {
                "success": False, 
                "message": "Kayıtlı cihaz bulunamadı",
                "tokens_count": 0
            }
        
        if not FIREBASE_AVAILABLE or not self.firebase_app:
            # Firebase yoksa simüle et (geliştirme için)
            print(f"📤 [SİMÜLASYON] Bildirim gönderildi:")
            print(f"   Başlık: {payload.title}")
            print(f"   İçerik: {payload.body}")
            print(f"   Hedef: {len(target_tokens)} cihaz")
            
            return {
                "success": True,
                "message": "Bildirim simüle edildi (Firebase yapılandırılmamış)",
                "tokens_count": len(target_tokens),
                "simulated": True
            }
        
        # Firebase ile gerçek bildirim gönder
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=payload.title,
                    body=payload.body,
                    image=payload.image_url
                ),
                data=payload.data or {},
                tokens=target_tokens
            )
            
            response = messaging.send_multicast(message)
            
            # Başarısız token'ları temizle
            if response.failure_count > 0:
                self._cleanup_failed_tokens(target_tokens, response.responses)
            
            return {
                "success": True,
                "message": f"{response.success_count} cihaza bildirim gönderildi",
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "tokens_count": len(target_tokens)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Bildirim gönderme hatası: {str(e)}",
                "tokens_count": len(target_tokens)
            }
    
    def _cleanup_failed_tokens(self, tokens: List[str], responses: List):
        """Geçersiz token'ları temizle"""
        for idx, response in enumerate(responses):
            if not response.success:
                error = response.exception
                if hasattr(error, 'code') and error.code in ['UNREGISTERED', 'INVALID_ARGUMENT']:
                    token = tokens[idx]
                    if token in self.device_tokens:
                        self.device_tokens.remove(token)
        self._save_tokens()
    
    def get_stats(self) -> Dict:
        """Bildirim servisi istatistikleri"""
        return {
            "registered_devices": len(self.device_tokens),
            "firebase_available": FIREBASE_AVAILABLE,
            "firebase_initialized": self.firebase_app is not None,
            "pushover_enabled": self.pushover is not None,
            "pushover_configured": bool(PUSHOVER_USER_KEY and PUSHOVER_API_TOKEN)
        }


# Singleton instance
notification_service = NotificationService()

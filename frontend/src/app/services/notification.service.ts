import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { isPlatformBrowser } from '@angular/common';
import { BehaviorSubject, Observable } from 'rxjs';

export interface NotificationStats {
  registered_devices: number;
  firebase_available: boolean;
  firebase_initialized: boolean;
}

export interface NotificationResult {
  success: boolean;
  message: string;
  tokens_count?: number;
  simulated?: boolean;
}

export interface LocalNotification {
  id: number;
  title: string;
  body: string;
  timestamp: Date;
  read: boolean;
  type: 'detection' | 'info' | 'warning';
  data?: any;
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private apiUrl = 'http://localhost:5001';
  private isBrowser: boolean;
  
  // Yerel bildirimler (tarayıcıda gösterim için)
  private notifications = new BehaviorSubject<LocalNotification[]>([]);
  notifications$ = this.notifications.asObservable();
  
  private unreadCount = new BehaviorSubject<number>(0);
  unreadCount$ = this.unreadCount.asObservable();
  
  // Bildirim izni durumu
  private permissionGranted = new BehaviorSubject<boolean>(false);
  permissionGranted$ = this.permissionGranted.asObservable();

  constructor(
    private http: HttpClient,
    @Inject(PLATFORM_ID) platformId: Object
  ) {
    this.isBrowser = isPlatformBrowser(platformId);
    
    if (this.isBrowser) {
      this.loadNotifications();
      this.checkPermission();
    }
  }

  /**
   * Bildirim izni iste
   */
  async requestPermission(): Promise<boolean> {
    if (!this.isBrowser || !('Notification' in window)) {
      console.warn('Bu tarayıcı bildirimleri desteklemiyor');
      return false;
    }

    try {
      const permission = await Notification.requestPermission();
      const granted = permission === 'granted';
      this.permissionGranted.next(granted);
      
      if (granted) {
        this.showBrowserNotification('Bildirimler Aktif', 'Artık nesne tespiti bildirimlerini alacaksınız.');
      }
      
      return granted;
    } catch (error) {
      console.error('Bildirim izni hatası:', error);
      return false;
    }
  }

  /**
   * Mevcut izin durumunu kontrol et
   */
  private checkPermission(): void {
    if ('Notification' in window) {
      this.permissionGranted.next(Notification.permission === 'granted');
    }
  }

  /**
   * Tarayıcı bildirimi göster
   */
  showBrowserNotification(title: string, body: string, icon?: string): void {
    if (!this.isBrowser || !this.permissionGranted.value) return;

    try {
      const notification = new Notification(title, {
        body,
        icon: icon || '/assets/icon.png',
        tag: 'yolo-detection'
      });

      notification.onclick = () => {
        window.focus();
        notification.close();
      };

      // 5 saniye sonra otomatik kapat
      setTimeout(() => notification.close(), 5000);
    } catch (error) {
      console.error('Bildirim gösterme hatası:', error);
    }
  }

  /**
   * Tespit bildirimi ekle ve göster
   */
  addDetectionNotification(objectCount: { [key: string]: number }): void {
    const total = Object.values(objectCount).reduce((a, b) => a + b, 0);
    const objectList = Object.entries(objectCount)
      .map(([name, count]) => `${count} ${name}`)
      .join(', ');

    const notification: LocalNotification = {
      id: Date.now(),
      title: `🎯 ${total} Nesne Tespit Edildi!`,
      body: objectList,
      timestamp: new Date(),
      read: false,
      type: 'detection',
      data: objectCount
    };

    // Listeye ekle
    const current = this.notifications.value;
    const updated = [notification, ...current].slice(0, 50); // Max 50 bildirim
    this.notifications.next(updated);
    this.updateUnreadCount();
    this.saveNotifications();

    // Tarayıcı bildirimi göster
    this.showBrowserNotification(notification.title, notification.body);
  }

  /**
   * Bildirimi okundu olarak işaretle
   */
  markAsRead(id: number): void {
    const current = this.notifications.value;
    const updated = current.map(n => 
      n.id === id ? { ...n, read: true } : n
    );
    this.notifications.next(updated);
    this.updateUnreadCount();
    this.saveNotifications();
  }

  /**
   * Tüm bildirimleri okundu olarak işaretle
   */
  markAllAsRead(): void {
    const current = this.notifications.value;
    const updated = current.map(n => ({ ...n, read: true }));
    this.notifications.next(updated);
    this.updateUnreadCount();
    this.saveNotifications();
  }

  /**
   * Bildirimi sil
   */
  deleteNotification(id: number): void {
    const current = this.notifications.value;
    const updated = current.filter(n => n.id !== id);
    this.notifications.next(updated);
    this.updateUnreadCount();
    this.saveNotifications();
  }

  /**
   * Tüm bildirimleri temizle
   */
  clearAll(): void {
    this.notifications.next([]);
    this.unreadCount.next(0);
    this.saveNotifications();
  }

  private updateUnreadCount(): void {
    const count = this.notifications.value.filter(n => !n.read).length;
    this.unreadCount.next(count);
  }

  private saveNotifications(): void {
    if (!this.isBrowser) return;
    try {
      localStorage.setItem('yolo_notifications', JSON.stringify(this.notifications.value));
    } catch (e) {
      console.error('Bildirimler kaydedilemedi:', e);
    }
  }

  private loadNotifications(): void {
    if (!this.isBrowser) return;
    try {
      const saved = localStorage.getItem('yolo_notifications');
      if (saved) {
        const parsed = JSON.parse(saved);
        this.notifications.next(parsed);
        this.updateUnreadCount();
      }
    } catch (e) {
      console.error('Bildirimler yüklenemedi:', e);
    }
  }

  // ==================== API METHODS ====================

  /**
   * Backend'e cihaz token'ı kaydet (Firebase için)
   */
  registerToken(token: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/notifications/register`, { token });
  }

  /**
   * Backend bildirim istatistikleri
   */
  getStats(): Observable<NotificationStats> {
    return this.http.get<NotificationStats>(`${this.apiUrl}/notifications/stats`);
  }

  /**
   * Test bildirimi gönder
   */
  sendTestNotification(): Observable<NotificationResult> {
    return this.http.post<NotificationResult>(`${this.apiUrl}/notifications/test`, {});
  }
}

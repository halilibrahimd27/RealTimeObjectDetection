import { Component, OnInit, OnDestroy } from '@angular/core';
import { NotificationService, LocalNotification } from '../services/notification.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-notification-panel',
  templateUrl: './notification-panel.component.html',
  styleUrls: ['./notification-panel.component.css']
})
export class NotificationPanelComponent implements OnInit, OnDestroy {
  notifications: LocalNotification[] = [];
  unreadCount = 0;
  isOpen = false;
  permissionGranted = false;

  private subscriptions: Subscription[] = [];

  constructor(private notificationService: NotificationService) {}

  ngOnInit(): void {
    this.subscriptions.push(
      this.notificationService.notifications$.subscribe(
        notifications => this.notifications = notifications
      ),
      this.notificationService.unreadCount$.subscribe(
        count => this.unreadCount = count
      ),
      this.notificationService.permissionGranted$.subscribe(
        granted => this.permissionGranted = granted
      )
    );
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }

  toggle(): void {
    this.isOpen = !this.isOpen;
  }

  close(): void {
    this.isOpen = false;
  }

  async requestPermission(): Promise<void> {
    await this.notificationService.requestPermission();
  }

  markAsRead(notification: LocalNotification): void {
    this.notificationService.markAsRead(notification.id);
  }

  markAllAsRead(): void {
    this.notificationService.markAllAsRead();
  }

  deleteNotification(event: Event, notification: LocalNotification): void {
    event.stopPropagation();
    this.notificationService.deleteNotification(notification.id);
  }

  clearAll(): void {
    this.notificationService.clearAll();
  }

  getTimeAgo(date: Date): string {
    const now = new Date();
    const then = new Date(date);
    const seconds = Math.floor((now.getTime() - then.getTime()) / 1000);

    if (seconds < 60) return 'Az önce';
    if (seconds < 3600) return `${Math.floor(seconds / 60)} dk önce`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} saat önce`;
    return `${Math.floor(seconds / 86400)} gün önce`;
  }

  getNotificationIcon(type: string): string {
    switch (type) {
      case 'detection': return '🎯';
      case 'warning': return '⚠️';
      default: return 'ℹ️';
    }
  }
}

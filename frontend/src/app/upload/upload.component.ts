import { Component, ElementRef, ViewChild, Inject, PLATFORM_ID } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { isPlatformBrowser } from '@angular/common';
import { NotificationService } from '../services/notification.service';

interface PredictionResponse {
  image: string;
  object_count: { [key: string]: number };
  notification?: any;
}

interface DetectionHistory {
  id: number;
  timestamp: Date;
  imageUrl: string;
  objects: { [key: string]: number };
  totalObjects: number;
}

@Component({
  selector: 'app-upload',
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.css']
})
export class UploadComponent {
  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;

  selectedFile: File | null = null;
  previewUrl: string | null = null;
  resultImageUrl: string | null = null;
  objectCounts: { [key: string]: number } = {};
  isLoading: boolean = false;
  isDragOver: boolean = false;
  errorMessage: string | null = null;
  detectionHistory: DetectionHistory[] = [];
  showHistory: boolean = false;

  // Stats
  totalDetections: number = 0;
  totalImages: number = 0;

  private isBrowser: boolean;

  constructor(
    private http: HttpClient,
    private notificationService: NotificationService,
    @Inject(PLATFORM_ID) platformId: Object
  ) {
    this.isBrowser = isPlatformBrowser(platformId);
    if (this.isBrowser) {
      this.loadHistory();
    }
  }

  // Drag & Drop handlers
  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = true;
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = false;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = false;

    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.handleFile(files[0]);
    }
  }

  // Dosya seçimi
  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.handleFile(file);
    }
  }

  handleFile(file: File): void {
    if (!file.type.startsWith('image/')) {
      this.errorMessage = 'Lütfen geçerli bir görsel dosyası seçin.';
      return;
    }

    this.selectedFile = file;
    this.errorMessage = null;
    this.resultImageUrl = null;
    this.objectCounts = {};

    // Preview oluştur
    const reader = new FileReader();
    reader.onload = (e) => {
      this.previewUrl = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }

  triggerFileInput(): void {
    this.fileInput.nativeElement.click();
  }

  clearSelection(): void {
    this.selectedFile = null;
    this.previewUrl = null;
    this.resultImageUrl = null;
    this.objectCounts = {};
    this.errorMessage = null;
    if (this.fileInput) {
      this.fileInput.nativeElement.value = '';
    }
  }

  // Formu gönderme
  onSubmit(): void {
    if (!this.selectedFile) {
      this.errorMessage = 'Lütfen bir dosya seçin';
      return;
    }

    const formData = new FormData();
    formData.append('image', this.selectedFile);

    this.isLoading = true;
    this.errorMessage = null;

    // HTTP isteği
    this.http.post<PredictionResponse>('http://localhost:5001/predict', formData)
      .subscribe({
        next: (response: PredictionResponse) => {
          this.isLoading = false;
          this.resultImageUrl = 'data:image/jpeg;base64,' + response.image;
          this.objectCounts = response.object_count || {};

          // Geçmişe ekle
          this.addToHistory(response);
          
          // Bildirim gönder
          if (Object.keys(this.objectCounts).length > 0) {
            this.notificationService.addDetectionNotification(this.objectCounts);
          }
        },
        error: (err: HttpErrorResponse) => {
          this.isLoading = false;
          this.errorMessage = 'Görsel işlenirken bir hata oluştu. Lütfen tekrar deneyin.';
          console.error('Hata:', err);
        }
      });
  }

  addToHistory(response: PredictionResponse): void {
    const totalObjects = Object.values(response.object_count || {}).reduce((a, b) => a + b, 0);
    
    const historyItem: DetectionHistory = {
      id: Date.now(),
      timestamp: new Date(),
      imageUrl: 'data:image/jpeg;base64,' + response.image,
      objects: response.object_count || {},
      totalObjects
    };

    this.detectionHistory.unshift(historyItem);
    if (this.detectionHistory.length > 10) {
      this.detectionHistory.pop();
    }

    this.totalDetections += totalObjects;
    this.totalImages++;

    this.saveHistory();
  }

  saveHistory(): void {
    if (!this.isBrowser) return;
    try {
      localStorage.setItem('detectionHistory', JSON.stringify(this.detectionHistory));
      localStorage.setItem('totalDetections', this.totalDetections.toString());
      localStorage.setItem('totalImages', this.totalImages.toString());
    } catch (e) {
      console.error('Geçmiş kaydedilemedi:', e);
    }
  }

  loadHistory(): void {
    if (!this.isBrowser) return;
    try {
      const history = localStorage.getItem('detectionHistory');
      if (history) {
        this.detectionHistory = JSON.parse(history);
      }
      this.totalDetections = parseInt(localStorage.getItem('totalDetections') || '0', 10);
      this.totalImages = parseInt(localStorage.getItem('totalImages') || '0', 10);
    } catch (e) {
      console.error('Geçmiş yüklenemedi:', e);
    }
  }

  clearHistory(): void {
    if (!this.isBrowser) return;
    this.detectionHistory = [];
    this.totalDetections = 0;
    this.totalImages = 0;
    localStorage.removeItem('detectionHistory');
    localStorage.removeItem('totalDetections');
    localStorage.removeItem('totalImages');
  }

  toggleHistory(): void {
    this.showHistory = !this.showHistory;
  }

  loadFromHistory(item: DetectionHistory): void {
    this.resultImageUrl = item.imageUrl;
    this.objectCounts = item.objects;
    this.showHistory = false;
  }

  // objectCounts anahtarlarını almak için yardımcı fonksiyon
  getObjectKeys(): string[] {
    return Object.keys(this.objectCounts);
  }

  getTotalObjectCount(): number {
    return Object.values(this.objectCounts).reduce((a, b) => a + b, 0);
  }

  getObjectIcon(name: string): string {
    const icons: { [key: string]: string } = {
      'insan': '👤',
      'laptop': '💻',
      'monitor': '🖥️',
      'klavye': '⌨️',
      'mause': '🖱️',
      'masa': '🪑',
      'sandalye': '🪑',
      'canta': '👜',
      'cuzdan': '👛',
      'gozluk': '👓',
      'kalem': '✏️',
      'kolsaati': '⌚',
      'sise': '🍾',
      'dolap': '🗄️'
    };
    return icons[name.toLowerCase()] || '📦';
  }
}

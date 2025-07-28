import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-upload',
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.css']
})
export class UploadComponent {
  selectedFile: File | null = null;
  imageUrl: string | null = null;
  objectCounts: { [key: string]: number } = {};  // Nesneleri sayan bir yapı
  isLoading: boolean = false;

  constructor(private http: HttpClient) {}

  // Dosya seçimi
  onFileSelected(event: any): void {
    this.selectedFile = event.target.files[0];
  }

  // Formu gönderme
  onSubmit(): void {
    if (!this.selectedFile) {
      return;
    }

    const formData = new FormData();
    formData.append('image', this.selectedFile);

    // Yükleme işlemi başlatılıyor
    this.isLoading = true;

    // HTTP isteği
    this.http.post('http://localhost:5001/predict', formData)
      .subscribe({
        next: (response: any) => {
          this.isLoading = false;
          this.imageUrl = 'data:image/jpeg;base64,' + response.image;  // Base64 görseli URL'ye dönüştür
          
          // object_counts geldiğinde, doğru şekilde nesne yapılandırmasını yapar
          this.objectCounts = response.object_count || {};  // 'object_count' verisini burada alıyoruz
        },
        error: (err) => {
          this.isLoading = false;
          console.error('Hata:', err);
        }
      });
  }

  // objectCounts anahtarlarını almak için yardımcı bir fonksiyon
  getObjectKeys(): string[] {
    return Object.keys(this.objectCounts);
  }
}

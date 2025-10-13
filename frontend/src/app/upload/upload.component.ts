import { Component } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';

interface PredictionResponse {
  image: string;
  object_count: { [key: string]: number };
}

@Component({
  selector: 'app-upload',
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.css']
})
export class UploadComponent {
  selectedFile: File | null = null;
  imageUrl: string | null = null;
  objectCounts: { [key: string]: number } = {};
  isLoading: boolean = false;
  errorMessage: string | null = null;

  constructor(private http: HttpClient) {}

  // Dosya seçimi
  onFileSelected(event: any): void {
    this.selectedFile = event.target.files[0];
    this.errorMessage = null;
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
          this.imageUrl = 'data:image/jpeg;base64,' + response.image;
          this.objectCounts = response.object_count || {};
        },
        error: (err: HttpErrorResponse) => {
          this.isLoading = false;
          this.errorMessage = 'Görsel işlenirken bir hata oluştu. Lütfen tekrar deneyin.';
          console.error('Hata:', err);
        }
      });
  }

  // objectCounts anahtarlarını almak için yardımcı bir fonksiyon
  getObjectKeys(): string[] {
    return Object.keys(this.objectCounts);
  }
}

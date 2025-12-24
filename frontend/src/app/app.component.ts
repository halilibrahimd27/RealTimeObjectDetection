import { Component, ViewChild } from '@angular/core';
import { UploadComponent } from './upload/upload.component';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  @ViewChild(UploadComponent) uploadComponent!: UploadComponent;
  
  title = 'Real-Time Object Detection';

  onNavigate(section: string): void {
    switch (section) {
      case 'home':
        window.scrollTo({ top: 0, behavior: 'smooth' });
        break;
      case 'upload':
        const uploadSection = document.querySelector('.upload-section');
        if (uploadSection) {
          uploadSection.scrollIntoView({ behavior: 'smooth' });
        }
        break;
      case 'history':
        if (this.uploadComponent) {
          this.uploadComponent.toggleHistory();
        }
        break;
    }
  }
}

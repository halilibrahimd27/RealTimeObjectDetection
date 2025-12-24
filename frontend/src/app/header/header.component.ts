import { Component, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent {
  @Output() navigateTo = new EventEmitter<string>();
  
  isMenuOpen = false;
  activeLink = 'home';

  toggleMenu(): void {
    this.isMenuOpen = !this.isMenuOpen;
  }

  navigate(section: string): void {
    this.activeLink = section;
    this.isMenuOpen = false;
    this.navigateTo.emit(section);
  }
}

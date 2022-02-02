import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  title = 'web-app';

  constructor(private router: Router) {}

  openHomePage() {
    this.router.navigate(['']);
  }

  openListPage() {
    this.router.navigate(['/list']);
  }

  openNewDataPage() {
    this.router.navigate(['/new-data']);
  }

  openAddNewCompanyPage() {
    this.router.navigate(['/add-company']);
  }
}

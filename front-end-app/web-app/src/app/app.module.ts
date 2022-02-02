import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSortModule } from '@angular/material/sort';
import { ChartViewerComponent } from './chart-viewer/chart-viewer.component';
import { NgxChartsModule } from '@swimlane/ngx-charts';
import { HttpClientModule } from '@angular/common/http';
import { CompaniesListComponent } from './companies-list/companies-list.component';
import { MatTableModule } from '@angular/material/table';
import { Routes, RouterModule } from '@angular/router';
import { CompanyComponent } from './company/company.component';
import { HomeComponent } from './home/home.component';
import { DialogAddCompanyDialog } from './companies-list/companies-list.component';
import { MatPaginatorModule } from '@angular/material/paginator';
import { NewDataComponent } from './new-data/new-data.component';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDialogModule } from '@angular/material/dialog';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatStepperModule } from '@angular/material/stepper';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AddNewCompanyComponent } from './add-new-company/add-new-company.component';

const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'list', component: CompaniesListComponent },
  { path: 'new-data', component: NewDataComponent },
  { path: 'add-company', component: AddNewCompanyComponent },
  { path: 'company/:id', component: CompanyComponent },
];
@NgModule({
  declarations: [
    AppComponent,
    ChartViewerComponent,
    CompaniesListComponent,
    CompanyComponent,
    HomeComponent,
    NewDataComponent,
    DialogAddCompanyDialog,
    AddNewCompanyComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    MatToolbarModule,
    MatButtonModule,
    MatSortModule,
    MatIconModule,
    MatSelectModule,
    MatInputModule,
    MatFormFieldModule,
    MatProgressBarModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
    MatStepperModule,
    MatDialogModule,
    FormsModule,
    ReactiveFormsModule,
    NgxChartsModule,
    HttpClientModule,
    MatTableModule,
    MatGridListModule,
    MatPaginatorModule,
    RouterModule.forRoot(routes),
  ],
  providers: [],
  bootstrap: [AppComponent],
  exports: [RouterModule, MatButtonModule, MatFormFieldModule, MatInputModule],
})
export class AppModule {}

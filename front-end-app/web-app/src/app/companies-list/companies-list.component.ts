import {
  Component,
  OnInit,
  AfterViewInit,
  ViewChild,
  Input,
  Inject,
} from '@angular/core';
import { StockDataService } from '../services/stock-data.service';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';
import { Router } from '@angular/router';
import { MatSort } from '@angular/material/sort';

import {
  MatDialog,
  MatDialogRef,
  MAT_DIALOG_DATA,
} from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';

export interface CompanyElement {
  name: string;
  symbol: string;
  growing: string;
  growing_by: number;
  value: number;
}

export interface DialogData {
  name: string;
}

@Component({
  selector: 'app-companies-list',
  templateUrl: './companies-list.component.html',
  styleUrls: ['./companies-list.component.css'],
})
export class CompaniesListComponent implements OnInit {
  companies: Array<any> = [];
  displayedColumns: string[] = [
    'number',
    'name',
    'symbol',
    'value',
    'growing',
    'growing_by',
    'details',
  ];
  dataSource = new MatTableDataSource(this.companies);
  name?: string;

  @ViewChild(MatPaginator) paginator?: MatPaginator;
  @ViewChild(MatSort) sort?: MatSort;

  constructor(
    private stockDataService: StockDataService,
    private router: Router,
    public dialog: MatDialog
  ) {}
  ngOnInit(): void {
    this.getData();
  }

  ngAfterViewInit() {
    this.dataSource.paginator = this.paginator!;
    this.dataSource.sort = this.sort!;
  }

  openCompanyPage(companyName: any) {
    // this.router.navigate(['/' + companyName]);
    this.router.navigate(['/company/' + companyName]);
  }

  async openAdditionForm() {
    const dialogRef = this.dialog.open(DialogAddCompanyDialog, {
      width: '450px',
      data: { name: this.name },
    });

    dialogRef.afterClosed().subscribe((result) => {
      console.log('The dialog was closed');
      this.name = result;
    });
  }

  getData() {
    this.stockDataService.getCompaniesList().subscribe((response) => {
      this.companies = response.companies;
      this.companies = this.companies.filter((s: any) => {
        return s.growing != 'unknown';
      });
      this.dataSource.data = this.companies;
    });
  }

  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();

    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }
}

@Component({
  selector: 'dialog-add-company-dialog',
  templateUrl: './dialog-add-company-dialog.component.html',
  styleUrls: ['./dialog-add-company-dialog.component.css'],
})
export class DialogAddCompanyDialog {
  flag: boolean = false;

  constructor(
    public dialogRef: MatDialogRef<DialogAddCompanyDialog>,
    private stockDataService: StockDataService,
    @Inject(MAT_DIALOG_DATA) public data: DialogData,
    private _snackBar: MatSnackBar
  ) {}

  delay(ms: number) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  async onAddClick() {
    this.flag = true;
    this.stockDataService.addNewCompany(this.data?.name || '').subscribe(
      async (response) => {
        if (response.msg == 'present') {
          this._snackBar.open('Wybrana spółka jest już dodana', '', {
            duration: 5000,
            panelClass: ['blue-snackbar'],
            verticalPosition: 'top',
          });
          this.dialogRef.close();
        } else {
          this.flag = true;
          await this.delay(5000);
          window.location.reload();
          this.dialogRef.close();
        }
      },
      (error) => {
        this._snackBar.open('Wybrana spółka nie istnieje', '', {
          duration: 5000,
          panelClass: ['blue-snackbar'],
          verticalPosition: 'top',
        });
        this.dialogRef.close();
      }
    );

    this.flag = false;
  }
}

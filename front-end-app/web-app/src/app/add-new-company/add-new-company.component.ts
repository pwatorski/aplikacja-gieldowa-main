import { Component, OnInit } from '@angular/core';
import { StockDataService } from '../services/stock-data.service';

@Component({
  selector: 'app-add-new-company',
  templateUrl: './add-new-company.component.html',
  styleUrls: ['./add-new-company.component.css'],
})
export class AddNewCompanyComponent implements OnInit {
  candidates: any;
  filteredCandidates: any;

  constructor(private stockDataService: StockDataService) {}

  ngOnInit(): void {
    this.stockDataService.getCandidatesList().subscribe((response) => {
      this.candidates = response.candidates;
      this.filteredCandidates = this.candidates;
    });
  }

  addCompany(name: string) {
    this.candidates = this.candidates.filter((s: any) => {
      return s[1] != name;
    });
    this.filteredCandidates = this.filteredCandidates.filter((s: any) => {
      return s[1] != name;
    });
    this.stockDataService.addNewCompany(name).subscribe();
  }

  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value
      .trim()
      .toLowerCase();

    this.filteredCandidates = this.candidates.filter((s: any) => {
      return (
        s[0].trim().toLowerCase().includes(filterValue) ||
        s[1].trim().toLowerCase().includes(filterValue)
      );
    });
  }
}

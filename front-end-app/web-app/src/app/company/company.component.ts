import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { StockDataService } from '../services/stock-data.service';

@Component({
  selector: 'app-company',
  templateUrl: './company.component.html',
  styleUrls: ['./company.component.css'],
})
export class CompanyComponent implements OnInit {
  companyName: string = 'test';
  id: string = '';
  data: any[] = [];

  constructor(
    private route: ActivatedRoute,
    private stockDataService: StockDataService
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      this.id = params.id;
      this.stockDataService.getCompanyData(this.id).subscribe((response) => {
        this.companyName = response.company;
      });
    });
  }
}

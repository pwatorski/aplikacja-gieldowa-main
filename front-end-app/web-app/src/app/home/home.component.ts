import { Component, HostListener, OnInit } from '@angular/core';
import { StockDataService } from '../services/stock-data.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
})
export class HomeComponent implements OnInit {
  popularList: any = undefined;
  innerWidth: number = 1200;
  chartWidth: number = 500;
  chartHeigh: number = 250;

  constructor(private stockDataService: StockDataService) {}

  ngOnInit(): void {
    this.stockDataService.getPopularCompanies().subscribe((response) => {
      //next() callback
      this.popularList = response.popular;
    });
    this.onResize(window);
  }

  @HostListener('window:resize', ['$event'])
  onResize(event: any) {
    this.innerWidth = window.innerWidth;
    this.chartWidth = window.innerWidth / 2 - 200;
    this.chartHeigh = this.chartWidth / 2;
  }

  isSmallWindowSize() {
    return this.innerWidth < 1100;
  }
}

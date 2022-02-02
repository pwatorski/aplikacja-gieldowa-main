import { Component, Input, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { HistoricalData } from '../model';
import { StockDataService } from '../services/stock-data.service';

@Component({
  selector: 'app-chart-viewer',
  templateUrl: './chart-viewer.component.html',
  styleUrls: ['./chart-viewer.component.css'],
})
export class ChartViewerComponent implements OnInit {
  historicalData: Observable<HistoricalData[]> =
    this.stockDataService.historicalData;

  @Input()
  companyName: string = '';

  multi: any[] = [];
  data: Array<Array<{ name: string; value: number }>> = [];

  @Input()
  viewSize: [number, number] = [800, 360];

  @Input()
  newData?: any = false;

  // options
  showXAxis = true;
  showYAxis = true;
  gradient = false;
  showXAxisLabel = true;
  xAxisLabel = 'Data';
  showYAxisLabel = true;
  yAxisLabel = 'Wartość';
  scale = true;

  colorScheme = {
    domain: ['#5AA454', '#A10A28', '#C7B42C', '#AAAAAA'],
  };

  constructor(private stockDataService: StockDataService) {
    this.multi = [];

    // if (this.newData != []) {

    // this.data = this.createList(this.newData);
    // this.multi = [
    //   {
    //     name: 'Wartość',
    //     series: this.data[0],
    //   },
    //   {
    //     name: 'Predykcja',
    //     series: this.data[1],
    //   },
    // ];
    // }
  }
  ngOnInit(): void {
    if (this.newData != false) {
      console.log(this.newData);
      this.data = this.createList(this.newData);
      this.multi = [
        {
          name: 'Wartość',
          series: this.data[0],
        },
        {
          name: 'Predykcja',
          series: this.data[1],
        },
      ];
    } else {
      this.stockDataService
        .getCompanyData(this.companyName)
        .subscribe((response) => {
          //next() callback
          this.data = this.createList(response);

          this.multi = [
            {
              name: 'Wartość',
              series: this.data[0],
            },
            {
              name: 'Predykcja',
              series: this.data[1],
            },
          ];
        });
    }
  }

  public onSelect(event: any): void {}

  public onRefresh(): void {}

  createList(object: any) {
    let data: Array<{ name: string; value: number }> = [];
    let dataPred: Array<{ name: string; value: number }> = [];

    const keys = Object.keys(object.data);
    const values = Object.values(object.data);
    for (let n = 0; n < keys.length; n++) {
      data.push({ name: keys[n], value: values[n] as number });
    }

    const keysPred = Object.keys(object.predict);
    const valuesPred = Object.values(object.predict);
    for (let n = 0; n < keysPred.length; n++) {
      dataPred.push({
        name: keysPred[n],
        value: valuesPred[n] as number,
      });
    }

    return [data, dataPred];
  }
}

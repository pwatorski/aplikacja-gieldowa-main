import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { StockDataService } from '../services/stock-data.service';
import { delay } from 'rxjs/operators';
import { interval } from 'rxjs';

export interface Model {
  value: number;
  viewValue: string;
}
@Component({
  selector: 'app-new-data',
  templateUrl: './new-data.component.html',
  styleUrls: ['./new-data.component.css'],
})
export class NewDataComponent implements OnInit {
  firstFormGroup!: FormGroup;

  fileName: string = '';
  file?: File;
  models: Array<Model> = [];
  selectedModelID: number = 0;
  predictionID: number = 0;
  newData: any = undefined;

  constructor(
    private stockDataService: StockDataService,
    private _formBuilder: FormBuilder
  ) {}

  ngOnInit(): void {
    this.firstFormGroup = this._formBuilder.group({
      firstCtrl: ['', Validators.required],
    });

    this.stockDataService.getModels().subscribe((response) => {
      this.models = this.reformatModels(response);
    });
  }

  csvInputChange(fileInputEvent: any) {
    this.file = fileInputEvent.target.files[0];
    this.fileName = fileInputEvent.target.files[0].name;
    // console.log(fileInputEvent.target.files[0]);
    // this.stockDataService
    //   .postFileWithData(fileInputEvent.target.files[0])
    //   .subscribe((response) => {
    //     this.fileName = fileInputEvent.target.files[0].name;
    //   });
  }

  sendDataToBackend() {
    this.stockDataService
      .postFileWithData(this.file, this.selectedModelID)
      .subscribe(async (response: any) => {
        this.predictionID = response.request_id;
        const source = interval(2000);
        const sub = source.subscribe((val) => {
          this.stockDataService
            .getPrediction(this.predictionID)
            .pipe(delay(1000))
            .subscribe((response) => {
              if (!(response.state && response.state == 'processing')) {
                this.newData = response;
                sub.unsubscribe();
              }
            });
        });
      });
  }

  setNewData() {
    const sub = this.stockDataService
      .getPrediction(this.predictionID)
      .pipe(delay(1000))
      .subscribe((response) => {
        if (!(response.state && response.state == 'processing')) {
          this.newData = response;
        }
      });
    sub.unsubscribe();
    if (this.newData == undefined) {
      this.setNewData();
    }
  }

  delay(ms: number) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  downloadFile() {
    const blob = new Blob(
      [
        'data:\t',
        JSON.stringify(this.newData.data),
        '\n',
        'predict:\t',
        JSON.stringify(this.newData.predict),
      ],
      { type: 'text/csv' }
    );
    const url = window.URL.createObjectURL(blob);
    window.open(url);
  }

  reformatModels(models: Array<any>) {
    let returnArray: Array<Model> = [];
    models.forEach((m: any) => {
      returnArray.push({ value: m.id, viewValue: m.name });
    });
    return returnArray;
  }
}

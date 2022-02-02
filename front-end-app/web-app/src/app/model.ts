export interface NameValPair {
  name: string;
  value: number;
}

export interface HistoricalData {
  name: string;
  series: NameValPair[];
}

import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule, KeyValuePipe, DecimalPipe } from '@angular/common';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, KeyValuePipe, DecimalPipe],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit, OnDestroy {
  stats: any = null;
  loading = true;
  error = '';
  loadMsg = 'Connecting to AI engine...';
  private msgTimer: any;
  private msgs = [
    'Connecting to AI engine...',
    'Loading customer segments...',
    'Fetching order analytics...',
    'Calculating revenue metrics...',
    'Almost ready...'
  ];
  private msgIdx = 0;

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.msgTimer = setInterval(() => {
      this.msgIdx = (this.msgIdx + 1) % this.msgs.length;
      this.loadMsg = this.msgs[this.msgIdx];
    }, 800);

    this.api.getDashboardStats().subscribe({
      next: (res) => { clearInterval(this.msgTimer); this.stats = res.stats; this.loading = false; },
      error: ()   => { clearInterval(this.msgTimer); this.error = 'Flask API not running. Open a new terminal and run: python api/app.py'; this.loading = false; }
    });
  }

  ngOnDestroy(): void { clearInterval(this.msgTimer); }

  fmt(val: number): string { return 'Rs.' + Math.round(val).toLocaleString('en-IN'); }

  segColor(seg: string): string {
    const m: any = { 'High Value':'#1d4ed8','Loyal':'#15803d','At Risk':'#b91c1c','New Customer':'#b45309' };
    return m[seg] || '#475569';
  }
  segBg(seg: string): string {
    const m: any = { 'High Value':'#dbeafe','Loyal':'#dcfce7','At Risk':'#fee2e2','New Customer':'#fef3c7' };
    return m[seg] || '#f1f5f9';
  }
}

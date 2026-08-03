import { Component, OnInit } from '@angular/core';
import { CommonModule, KeyValuePipe, DecimalPipe } from '@angular/common';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, KeyValuePipe, DecimalPipe],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  stats: any = null;
  loading = true;
  error = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.getDashboardStats().subscribe({
      next: (res) => { this.stats = res.stats; this.loading = false; },
      error: ()   => { this.error = 'Flask API not running. Open a new terminal and run: python api/app.py'; this.loading = false; }
    });
  }

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

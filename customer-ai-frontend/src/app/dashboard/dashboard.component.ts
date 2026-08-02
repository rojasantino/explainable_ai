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
      error: ()    => { this.error = 'Cannot connect to API. Start Flask: python api/app.py'; this.loading = false; }
    });
  }

  formatCurrency(val: number): string {
    return 'Rs.' + Math.round(val).toLocaleString('en-IN');
  }

  getSegmentColor(seg: string): string {
    const map: any = { 'High Value':'#185FA5','Loyal':'#3B6D11','At Risk':'#A32D2D','New Customer':'#854F0B' };
    return map[seg] || '#888';
  }
}




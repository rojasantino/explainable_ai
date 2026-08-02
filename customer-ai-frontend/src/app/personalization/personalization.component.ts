import { Component } from '@angular/core';
import { CommonModule, DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-personalization',
  standalone: true,
  imports: [CommonModule, FormsModule, DecimalPipe],
  templateUrl: './personalization.component.html',
  styleUrls: ['./personalization.component.css']
})
export class PersonalizationComponent {
  userId = 101;
  profile: any = null;
  loading = false;
  error = '';

  constructor(private api: ApiService) {}

  search(): void {
    if (!this.userId) return;
    this.loading = true;
    this.error = '';
    this.profile = null;
    this.api.getCustomerProfile(this.userId).subscribe({
      next: (res) => { this.profile = res.profile; this.loading = false; },
      error: ()   => { this.error = 'User ' + this.userId + ' not found. Try IDs 101 to 600.'; this.loading = false; }
    });
  }

  getProbColor(prob: number): string {
    if (prob >= 0.7) return '#3B6D11';
    if (prob >= 0.4) return '#854F0B';
    return '#A32D2D';
  }

  getSegStyle(seg: string): object {
    const c: any = { 'High Value':'#185FA5','Loyal':'#3B6D11','At Risk':'#A32D2D','New Customer':'#854F0B' };
    return { background: c[seg]||'#888', color:'white', padding:'3px 10px', borderRadius:'12px', fontSize:'12px', fontWeight:'500' };
  }

  pct(prob: number): string { return (prob * 100).toFixed(1) + '%'; }
}



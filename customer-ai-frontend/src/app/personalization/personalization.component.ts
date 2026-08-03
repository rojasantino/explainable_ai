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
      error: ()   => { this.error = 'Customer ID ' + this.userId + ' not found. Valid IDs: 101 to 600.'; this.loading = false; }
    });
  }

  probColor(p: number): string {
    if (p >= 0.7) return '#15803d'; if (p >= 0.4) return '#b45309'; return '#b91c1c';
  }
  probBg(p: number): string {
    if (p >= 0.7) return '#dcfce7'; if (p >= 0.4) return '#fef3c7'; return '#fee2e2';
  }
  probLabel(p: number): string {
    if (p >= 0.7) return 'High'; if (p >= 0.4) return 'Medium'; return 'Low';
  }
  segStyle(seg: string): object {
    const c: any = { 'High Value':'#1d4ed8','Loyal':'#15803d','At Risk':'#b91c1c','New Customer':'#b45309' };
    const b: any = { 'High Value':'#dbeafe','Loyal':'#dcfce7','At Risk':'#fee2e2','New Customer':'#fef3c7' };
    return { color: c[seg]||'#475569', background: b[seg]||'#f1f5f9',
             padding:'4px 12px', borderRadius:'20px', fontSize:'12px', fontWeight:'600' };
  }
  pct(p: number): string { return (p * 100).toFixed(1) + '%'; }
}

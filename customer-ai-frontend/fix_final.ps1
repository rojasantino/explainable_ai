# fix_final.ps1 - Run from customer-ai-frontend folder
# powershell -ExecutionPolicy Bypass -File fix_final.ps1

Write-Host "Fixing Angular app..." -ForegroundColor Cyan

# ── app.config.ts — withFetch + no SSR zone issue ──────────
[System.IO.File]::WriteAllText("$PWD\src\app\app.config.ts",
"import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withFetch } from '@angular/common/http';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(withFetch()),
  ]
};
")
Write-Host "  app.config.ts" -ForegroundColor Green

# ── app.routes.server.ts — Server not Prerender ─────────────
[System.IO.File]::WriteAllText("$PWD\src\app\app.routes.server.ts",
"import { RenderMode, ServerRoute } from '@angular/ssr';
export const serverRoutes: ServerRoute[] = [
  { path: '**', renderMode: RenderMode.Server }
];
")
Write-Host "  app.routes.server.ts" -ForegroundColor Green

# ── main.ts ─────────────────────────────────────────────────
[System.IO.File]::WriteAllText("$PWD\src\main.ts",
"import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { App } from './app/app';

bootstrapApplication(App, appConfig).catch((err) => console.error(err));
")
Write-Host "  main.ts" -ForegroundColor Green

# ── app.ts ──────────────────────────────────────────────────
[System.IO.File]::WriteAllText("$PWD\src\app\app.ts",
"import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NavbarComponent } from './navbar/navbar.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, NavbarComponent],
  template: ``<app-navbar></app-navbar><router-outlet></router-outlet>``
})
export class App {}
")
Write-Host "  app.ts" -ForegroundColor Green

# ── api.service.ts ───────────────────────────────────────────
[System.IO.File]::WriteAllText("$PWD\src\app\services\api.service.ts",
"import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private base = 'http://localhost:5000/api';
  constructor(private http: HttpClient) {}
  getCustomerProfile(userId: number): Observable<any> {
    return this.http.get(this.base + '/customer/' + userId);
  }
  getDashboardStats(): Observable<any> {
    return this.http.get(this.base + '/dashboard/stats');
  }
}
")
Write-Host "  api.service.ts" -ForegroundColor Green

# ── navbar ───────────────────────────────────────────────────
[System.IO.File]::WriteAllText("$PWD\src\app\navbar\navbar.component.ts",
"import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  template: ``
    <nav class='navbar'>
      <div class='brand'>
        <span class='brand-icon'>AI</span>
        <span class='brand-text'>Personalization System</span>
      </div>
      <div class='links'>
        <a routerLink='/' routerLinkActive='active' [routerLinkActiveOptions]='{exact:true}'>Dashboard</a>
        <a routerLink='/customer' routerLinkActive='active'>Customer View</a>
      </div>
    </nav>
  ``,
  styles: [``
    .navbar { display:flex; justify-content:space-between; align-items:center;
              padding:0 32px; height:60px; background:#0f172a; color:white;
              box-shadow:0 1px 3px rgba(0,0,0,0.4); position:sticky; top:0; z-index:100; }
    .brand { display:flex; align-items:center; gap:10px; }
    .brand-icon { background:#3b82f6; color:white; font-size:11px; font-weight:800;
                  padding:4px 7px; border-radius:6px; letter-spacing:.5px; }
    .brand-text { font-size:15px; font-weight:600; color:#f1f5f9; }
    .links a { color:#94a3b8; text-decoration:none; margin-left:28px; font-size:13px;
               font-weight:500; transition:color .2s; padding-bottom:2px; }
    .links a:hover { color:#f1f5f9; }
    .links a.active { color:#3b82f6; border-bottom:2px solid #3b82f6; }
  ``]
})
export class NavbarComponent {}
")
Write-Host "  navbar.component.ts" -ForegroundColor Green

# ── dashboard.component.ts ───────────────────────────────────
[System.IO.File]::WriteAllText("$PWD\src\app\dashboard\dashboard.component.ts",
"import { Component, OnInit } from '@angular/core';
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
")
Write-Host "  dashboard.component.ts" -ForegroundColor Green

# ── dashboard.component.html ─────────────────────────────────
[System.IO.File]::WriteAllText("$PWD\src\app\dashboard\dashboard.component.html",
"<div class='page'>

  <div class='page-header'>
    <h1 class='page-title'>Analytics Dashboard</h1>
    <p class='page-sub'>Real-time customer behavior insights</p>
  </div>

  <div *ngIf='loading' class='state-box'>
    <div class='spinner'></div>
    <p>Loading dashboard data...</p>
  </div>

  <div *ngIf='error' class='error-card'>
    <div class='error-icon'>!</div>
    <div>
      <strong>Connection Failed</strong>
      <p>{{ error }}</p>
    </div>
  </div>

  <div *ngIf='stats && !loading'>

    <div class='kpi-grid'>
      <div class='kpi-card'>
        <div class='kpi-icon blue'>C</div>
        <div class='kpi-label'>Total Customers</div>
        <div class='kpi-value'>{{ stats.total_customers | number }}</div>
      </div>
      <div class='kpi-card'>
        <div class='kpi-icon green'>O</div>
        <div class='kpi-label'>Total Orders</div>
        <div class='kpi-value'>{{ stats.total_orders | number }}</div>
      </div>
      <div class='kpi-card'>
        <div class='kpi-icon purple'>R</div>
        <div class='kpi-label'>Total Revenue</div>
        <div class='kpi-value'>{{ fmt(stats.total_revenue) }}</div>
      </div>
      <div class='kpi-card'>
        <div class='kpi-icon orange'>A</div>
        <div class='kpi-label'>Avg Order Value</div>
        <div class='kpi-value'>{{ fmt(stats.avg_order_value) }}</div>
      </div>
    </div>

    <div class='row-2'>
      <div class='card'>
        <h3 class='card-title'>Customer Segments</h3>
        <div class='seg-list'>
          <div class='seg-row' *ngFor='let seg of stats.segments | keyvalue'
               [style.borderLeftColor]='segColor(seg.key.toString())'>
            <div class='seg-info'>
              <span class='seg-badge' [style.color]='segColor(seg.key.toString())'
                    [style.background]='segBg(seg.key.toString())'>{{ seg.key }}</span>
            </div>
            <span class='seg-num'>{{ seg.value }} customers</span>
          </div>
        </div>
      </div>

      <div class='card'>
        <h3 class='card-title'>Top Products</h3>
        <div class='prod-list'>
          <div class='prod-row' *ngFor='let p of stats.top_products; let i = index'>
            <span class='prod-rank'># {{ i + 1 }}</span>
            <span class='prod-id'>{{ p.product_id }}</span>
            <div class='prod-bar-wrap'>
              <div class='prod-bar' [style.width.%]='(p.total_sold / stats.top_products[0].total_sold) * 100'></div>
            </div>
            <span class='prod-sold'>{{ p.total_sold }}</span>
          </div>
        </div>
      </div>
    </div>

  </div>
</div>
")
Write-Host "  dashboard.component.html" -ForegroundColor Green

# ── dashboard.component.css ──────────────────────────────────
[System.IO.File]::WriteAllText("$PWD\src\app\dashboard\dashboard.component.css",
".page { padding:32px; max-width:1100px; margin:0 auto; font-family:'Segoe UI',sans-serif; }
.page-header { margin-bottom:28px; }
.page-title { font-size:24px; font-weight:700; color:#0f172a; margin:0 0 4px; }
.page-sub { font-size:14px; color:#64748b; margin:0; }

.state-box { display:flex; flex-direction:column; align-items:center;
             padding:60px; color:#64748b; gap:16px; }
.spinner { width:36px; height:36px; border:3px solid #e2e8f0;
           border-top-color:#3b82f6; border-radius:50%; animation:spin 1s linear infinite; }
@keyframes spin { to { transform:rotate(360deg); } }

.error-card { display:flex; align-items:flex-start; gap:14px; background:#fff1f2;
              border:1px solid #fecaca; border-radius:12px; padding:18px 20px; margin-bottom:24px; }
.error-icon { background:#ef4444; color:white; font-weight:800; font-size:13px;
              width:28px; height:28px; border-radius:50%; display:flex;
              align-items:center; justify-content:center; flex-shrink:0; }
.error-card strong { font-size:14px; color:#991b1b; }
.error-card p { font-size:13px; color:#dc2626; margin:4px 0 0; }

.kpi-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:24px; }
.kpi-card { background:white; border:1px solid #e2e8f0; border-radius:14px;
            padding:20px; display:flex; flex-direction:column; gap:8px;
            box-shadow:0 1px 3px rgba(0,0,0,0.05); }
.kpi-icon { width:36px; height:36px; border-radius:10px; font-size:12px; font-weight:800;
            display:flex; align-items:center; justify-content:center; color:white; }
.kpi-icon.blue { background:#3b82f6; }
.kpi-icon.green { background:#22c55e; }
.kpi-icon.purple { background:#8b5cf6; }
.kpi-icon.orange { background:#f97316; }
.kpi-label { font-size:12px; color:#64748b; font-weight:500; }
.kpi-value { font-size:22px; font-weight:700; color:#0f172a; }

.row-2 { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.card { background:white; border:1px solid #e2e8f0; border-radius:14px;
        padding:20px; box-shadow:0 1px 3px rgba(0,0,0,0.05); }
.card-title { font-size:15px; font-weight:600; color:#0f172a; margin:0 0 16px; }

.seg-list { display:flex; flex-direction:column; gap:10px; }
.seg-row { display:flex; justify-content:space-between; align-items:center;
           padding:10px 14px; border-radius:8px; background:#f8fafc;
           border-left:3px solid #cbd5e1; }
.seg-badge { padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }
.seg-num { font-size:13px; color:#475569; font-weight:500; }

.prod-list { display:flex; flex-direction:column; gap:10px; }
.prod-row { display:flex; align-items:center; gap:10px; }
.prod-rank { font-size:12px; color:#94a3b8; width:28px; font-weight:600; }
.prod-id { font-size:13px; font-weight:600; color:#0f172a; width:56px; }
.prod-bar-wrap { flex:1; background:#f1f5f9; border-radius:4px; height:8px; }
.prod-bar { background:#3b82f6; border-radius:4px; height:100%; transition:width .4s; }
.prod-sold { font-size:12px; color:#64748b; min-width:40px; text-align:right; }

@media(max-width:768px) { .kpi-grid { grid-template-columns:1fr 1fr; } .row-2 { grid-template-columns:1fr; } }
")
Write-Host "  dashboard.component.css" -ForegroundColor Green

# ── personalization.component.ts ─────────────────────────────
[System.IO.File]::WriteAllText("$PWD\src\app\personalization\personalization.component.ts",
"import { Component } from '@angular/core';
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
")
Write-Host "  personalization.component.ts" -ForegroundColor Green

# ── personalization.component.html ───────────────────────────
[System.IO.File]::WriteAllText("$PWD\src\app\personalization\personalization.component.html",
"<div class='page'>

  <!-- Login-style search card -->
  <div class='login-wrap'>
    <div class='login-card'>
      <div class='login-icon'>AI</div>
      <h2 class='login-title'>Customer Lookup</h2>
      <p class='login-sub'>Enter a Customer ID to view personalized AI insights</p>

      <div class='field'>
        <label class='field-label'>Customer ID</label>
        <input class='field-input' type='number' [(ngModel)]='userId'
               placeholder='e.g. 101, 150, 250, 400'
               (keyup.enter)='search()' />
        <p class='field-hint'>Valid range: 101 to 600</p>
      </div>

      <button class='btn-primary' (click)='search()' [disabled]='loading'>
        <span *ngIf='!loading'>Analyze Customer</span>
        <span *ngIf='loading'>Analyzing...</span>
      </button>

      <div *ngIf='error' class='error-msg'>{{ error }}</div>
    </div>
  </div>

  <!-- Results -->
  <div *ngIf='profile && !loading' class='results'>

    <!-- Profile card -->
    <div class='result-card profile-card'>
      <div class='profile-left'>
        <div class='avatar'>{{ profile.user_id }}</div>
        <div>
          <div class='profile-name'>Customer #{{ profile.user_id }}</div>
          <div class='profile-meta'>{{ profile.age }} yrs &nbsp;|&nbsp; {{ profile.gender }} &nbsp;|&nbsp; {{ profile.location }}</div>
          <span [ngStyle]='segStyle(profile.segment)'>{{ profile.segment }}</span>
        </div>
      </div>
      <div class='profile-stats'>
        <div class='stat'>
          <div class='stat-label'>Total Orders</div>
          <div class='stat-val'>{{ profile.total_orders }}</div>
        </div>
        <div class='stat'>
          <div class='stat-label'>Total Spent</div>
          <div class='stat-val'>Rs.{{ profile.total_spend | number:'1.0-0' }}</div>
        </div>
        <div class='stat'>
          <div class='stat-label'>Segment</div>
          <div class='stat-val'>{{ profile.segment }}</div>
        </div>
      </div>
    </div>

    <!-- Probability card -->
    <div class='result-card'>
      <h3 class='rc-title'>Purchase Probability</h3>
      <div class='prob-row'>
        <div class='prob-circle' [style.background]='probBg(profile.buy_probability)'
             [style.color]='probColor(profile.buy_probability)'>
          <span class='prob-pct'>{{ pct(profile.buy_probability) }}</span>
          <span class='prob-lbl'>{{ probLabel(profile.buy_probability) }}</span>
        </div>
        <div class='prob-detail'>
          <p class='prob-desc'>Likelihood this customer will make a purchase in the next 30 days.</p>
          <div class='bar-wrap'>
            <div class='bar-fill' [style.width]='pct(profile.buy_probability)'
                 [style.background]='probColor(profile.buy_probability)'></div>
          </div>
          <p class='bar-label'>{{ pct(profile.buy_probability) }} chance of purchasing</p>
        </div>
      </div>
    </div>

    <!-- Recommendations -->
    <div class='result-card'>
      <h3 class='rc-title'>Recommended Products</h3>
      <p class='rc-sub'>Based on customers with similar purchase history</p>
      <div class='rec-grid'>
        <div class='rec-card' *ngFor='let pid of profile.recommendations; let i = index'>
          <div class='rec-rank'>#{{ i + 1 }}</div>
          <div class='rec-id'>{{ pid }}</div>
          <div class='rec-tag'>Recommended</div>
        </div>
      </div>
    </div>

    <!-- SHAP Explanation -->
    <div class='result-card explanation-card'>
      <div class='exp-header'>
        <h3 class='rc-title'>Why these recommendations?</h3>
        <span class='shap-badge'>Powered by SHAP AI</span>
      </div>
      <p class='rc-sub'>Top factors driving the prediction for this customer</p>
      <div class='reason-list'>
        <div class='reason-row' *ngFor='let r of profile.reasons; let i = index'>
          <div class='reason-num'>{{ i + 1 }}</div>
          <div class='reason-text'>{{ r }}</div>
        </div>
      </div>
    </div>

  </div>
</div>
")
Write-Host "  personalization.component.html" -ForegroundColor Green

# ── personalization.component.css ────────────────────────────
[System.IO.File]::WriteAllText("$PWD\src\app\personalization\personalization.component.css",
".page { padding:32px; max-width:820px; margin:0 auto; font-family:'Segoe UI',sans-serif; }

/* Login card */
.login-wrap { display:flex; justify-content:center; margin-bottom:32px; }
.login-card { background:white; border:1px solid #e2e8f0; border-radius:20px;
              padding:40px; width:100%; max-width:440px;
              box-shadow:0 4px 24px rgba(0,0,0,0.08); }
.login-icon { width:52px; height:52px; background:#3b82f6; color:white; font-weight:800;
              font-size:14px; border-radius:14px; display:flex; align-items:center;
              justify-content:center; margin:0 auto 16px; }
.login-title { font-size:20px; font-weight:700; color:#0f172a; text-align:center; margin:0 0 6px; }
.login-sub { font-size:13px; color:#64748b; text-align:center; margin:0 0 28px; }

.field { margin-bottom:20px; }
.field-label { display:block; font-size:13px; font-weight:600; color:#374151; margin-bottom:6px; }
.field-input { width:100%; padding:11px 14px; border:1px solid #d1d5db; border-radius:10px;
               font-size:15px; color:#0f172a; outline:none; transition:border .2s; box-sizing:border-box; }
.field-input:focus { border-color:#3b82f6; box-shadow:0 0 0 3px rgba(59,130,246,0.15); }
.field-hint { font-size:12px; color:#9ca3af; margin:5px 0 0; }

.btn-primary { width:100%; padding:12px; background:#3b82f6; color:white; font-size:15px;
               font-weight:600; border:none; border-radius:10px; cursor:pointer; transition:background .2s; }
.btn-primary:hover:not(:disabled) { background:#2563eb; }
.btn-primary:disabled { opacity:.7; cursor:not-allowed; }

.error-msg { margin-top:14px; background:#fef2f2; color:#dc2626; border-radius:8px;
             padding:10px 14px; font-size:13px; text-align:center; }

/* Result cards */
.results { display:flex; flex-direction:column; gap:16px; }
.result-card { background:white; border:1px solid #e2e8f0; border-radius:16px;
               padding:24px; box-shadow:0 1px 3px rgba(0,0,0,0.05); }
.rc-title { font-size:15px; font-weight:700; color:#0f172a; margin:0 0 4px; }
.rc-sub { font-size:13px; color:#64748b; margin:0 0 16px; }

/* Profile */
.profile-card { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:20px; }
.profile-left { display:flex; align-items:center; gap:16px; }
.avatar { width:56px; height:56px; border-radius:50%; background:#1e40af; color:white;
          display:flex; align-items:center; justify-content:center; font-size:13px; font-weight:700; }
.profile-name { font-size:17px; font-weight:700; color:#0f172a; margin-bottom:3px; }
.profile-meta { font-size:13px; color:#64748b; margin-bottom:7px; }
.profile-stats { display:flex; gap:28px; }
.stat { text-align:center; }
.stat-label { font-size:11px; color:#94a3b8; font-weight:500; margin-bottom:3px; }
.stat-val { font-size:18px; font-weight:700; color:#0f172a; }

/* Probability */
.prob-row { display:flex; align-items:center; gap:24px; }
.prob-circle { width:90px; height:90px; border-radius:50%; display:flex; flex-direction:column;
               align-items:center; justify-content:center; flex-shrink:0; }
.prob-pct { font-size:20px; font-weight:800; }
.prob-lbl { font-size:11px; font-weight:600; }
.prob-detail { flex:1; }
.prob-desc { font-size:13px; color:#64748b; margin:0 0 12px; }
.bar-wrap { background:#f1f5f9; border-radius:6px; height:10px; margin-bottom:6px; overflow:hidden; }
.bar-fill { height:100%; border-radius:6px; transition:width .6s ease; }
.bar-label { font-size:12px; color:#64748b; }

/* Recommendations */
.rec-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:10px; }
.rec-card { background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px;
            padding:12px 8px; text-align:center; }
.rec-rank { font-size:10px; color:#94a3b8; font-weight:600; margin-bottom:4px; }
.rec-id { font-size:14px; font-weight:700; color:#1d4ed8; margin-bottom:4px; }
.rec-tag { font-size:10px; color:#3b82f6; background:#eff6ff; border-radius:10px; padding:2px 6px; }

/* SHAP Explanation */
.explanation-card { background:linear-gradient(135deg,#f0f9ff,#e0f2fe); border-color:#bae6fd; }
.exp-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:4px; }
.shap-badge { background:#0ea5e9; color:white; font-size:11px; font-weight:600;
              padding:3px 10px; border-radius:20px; }
.reason-list { display:flex; flex-direction:column; gap:10px; }
.reason-row { display:flex; align-items:center; gap:14px; background:white;
              border-radius:10px; padding:12px 16px; }
.reason-num { width:26px; height:26px; background:#0ea5e9; color:white; font-size:12px;
              font-weight:700; border-radius:50%; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.reason-text { font-size:14px; color:#0c4a6e; font-weight:500; }

@media(max-width:600px) { .rec-grid { grid-template-columns:repeat(3,1fr); }
  .profile-card { flex-direction:column; } .prob-row { flex-direction:column; } }
")
Write-Host "  personalization.component.css" -ForegroundColor Green

# ── Clear cache ──────────────────────────────────────────────
if (Test-Path ".angular") {
  Remove-Item -Recurse -Force ".angular"
  Write-Host "  Cache cleared" -ForegroundColor Green
}

Write-Host ""
Write-Host "DONE! Now run: ng serve" -ForegroundColor Cyan

# Run: powershell -ExecutionPolicy Bypass -File setup_v19_fixed.ps1

$base = "src\app"

# Force create all folders first
md -Force "$base\services"        | Out-Null
md -Force "$base\navbar"          | Out-Null
md -Force "$base\dashboard"       | Out-Null
md -Force "$base\personalization" | Out-Null
Write-Host "Folders OK" -ForegroundColor Green

# ── app.config.ts ──────────────────────────────────────────
$content = @"
import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideHttpClient(),
  ]
};
"@
[System.IO.File]::WriteAllText("$PWD\src\app\app.config.ts", $content)
Write-Host "app.config.ts" -ForegroundColor Green

# ── app.routes.ts ───────────────────────────────────────────
$content = @"
import { Routes } from '@angular/router';
import { DashboardComponent } from './dashboard/dashboard.component';
import { PersonalizationComponent } from './personalization/personalization.component';

export const routes: Routes = [
  { path: '',         component: DashboardComponent },
  { path: 'customer', component: PersonalizationComponent },
];
"@
[System.IO.File]::WriteAllText("$PWD\src\app\app.routes.ts", $content)
Write-Host "app.routes.ts" -ForegroundColor Green

# ── app.ts ──────────────────────────────────────────────────
$content = @"
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NavbarComponent } from './navbar/navbar.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, NavbarComponent],
  template: ``
    <app-navbar></app-navbar>
    <router-outlet></router-outlet>
  ``
})
export class App {}
"@
[System.IO.File]::WriteAllText("$PWD\src\app\app.ts", $content)
Write-Host "app.ts" -ForegroundColor Green

# ── app.html ────────────────────────────────────────────────
$content = @"
<app-navbar></app-navbar>
<router-outlet></router-outlet>
"@
[System.IO.File]::WriteAllText("$PWD\src\app\app.html", $content)
Write-Host "app.html" -ForegroundColor Green

# ── services/api.service.ts ─────────────────────────────────
$content = @"
import { Injectable } from '@angular/core';
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
"@
[System.IO.File]::WriteAllText("$PWD\src\app\services\api.service.ts", $content)
Write-Host "services/api.service.ts" -ForegroundColor Green

# ── navbar/navbar.component.ts ──────────────────────────────
$content = @"
import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  template: ``
    <nav class="navbar">
      <div class="brand">AI Personalization</div>
      <div class="links">
        <a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{exact:true}">Dashboard</a>
        <a routerLink="/customer" routerLinkActive="active">Customer View</a>
      </div>
    </nav>
  ``,
  styles: [``
    .navbar { display:flex; justify-content:space-between; align-items:center;
              padding:12px 24px; background:#185FA5; color:white; }
    .brand { font-size:18px; font-weight:600; }
    .links a { color:rgba(255,255,255,0.85); text-decoration:none; margin-left:20px; font-size:14px; }
    .links a.active { color:white; font-weight:600; border-bottom:2px solid white; padding-bottom:2px; }
  ``]
})
export class NavbarComponent {}
"@
[System.IO.File]::WriteAllText("$PWD\src\app\navbar\navbar.component.ts", $content)
Write-Host "navbar/navbar.component.ts" -ForegroundColor Green

# ── dashboard/dashboard.component.ts ────────────────────────
$content = @"
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
"@
[System.IO.File]::WriteAllText("$PWD\src\app\dashboard\dashboard.component.ts", $content)
Write-Host "dashboard/dashboard.component.ts" -ForegroundColor Green

# ── dashboard/dashboard.component.html ──────────────────────
$content = @"
<div class="page">
  <h2 class="page-title">Analytics Dashboard</h2>
  <div *ngIf="loading" class="loading">Loading dashboard data...</div>
  <div *ngIf="error" class="error-msg">{{ error }}</div>
  <div *ngIf="stats && !loading">
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Total Customers</div>
        <div class="kpi-value">{{ stats.total_customers | number }}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Total Orders</div>
        <div class="kpi-value">{{ stats.total_orders | number }}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Total Revenue</div>
        <div class="kpi-value">{{ formatCurrency(stats.total_revenue) }}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Avg Order Value</div>
        <div class="kpi-value">{{ formatCurrency(stats.avg_order_value) }}</div>
      </div>
    </div>
    <div class="section-card">
      <h3>Customer Segments</h3>
      <div class="segment-grid">
        <div class="segment-pill"
             *ngFor="let seg of stats.segments | keyvalue"
             [style.background]="getSegmentColor(seg.key.toString())">
          <span class="seg-name">{{ seg.key }}</span>
          <span class="seg-count">{{ seg.value }}</span>
        </div>
      </div>
    </div>
    <div class="section-card">
      <h3>Top Products</h3>
      <div class="product-row" *ngFor="let p of stats.top_products; let i = index">
        <span class="rank">{{ i + 1 }}</span>
        <span class="prod-id">{{ p.product_id }}</span>
        <div class="bar-wrap">
          <div class="bar-fill" [style.width.%]="(p.total_sold / stats.top_products[0].total_sold) * 100"></div>
        </div>
        <span class="sold-count">{{ p.total_sold }} sold</span>
      </div>
    </div>
  </div>
</div>
"@
[System.IO.File]::WriteAllText("$PWD\src\app\dashboard\dashboard.component.html", $content)
Write-Host "dashboard/dashboard.component.html" -ForegroundColor Green

# ── dashboard/dashboard.component.css ───────────────────────
$content = @"
.page { padding:24px; max-width:960px; margin:0 auto; font-family:sans-serif; }
.page-title { font-size:22px; font-weight:600; margin-bottom:20px; color:#1a1a1a; }
.loading { text-align:center; padding:40px; color:#888; }
.error-msg { background:#FCEBEB; color:#A32D2D; padding:12px 16px; border-radius:8px; margin-bottom:16px; }
.kpi-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:20px; }
.kpi-card { background:#f5f5f3; border-radius:10px; padding:16px; }
.kpi-label { font-size:12px; color:#666; margin-bottom:6px; }
.kpi-value { font-size:22px; font-weight:600; color:#185FA5; }
.section-card { background:white; border:0.5px solid #ddd; border-radius:12px; padding:20px; margin-bottom:16px; }
.section-card h3 { font-size:15px; font-weight:600; margin-bottom:14px; }
.segment-grid { display:flex; flex-wrap:wrap; gap:10px; }
.segment-pill { border-radius:20px; padding:8px 16px; color:white; display:flex; align-items:center; gap:8px; }
.seg-name { font-size:13px; font-weight:500; }
.seg-count { font-size:16px; font-weight:700; }
.product-row { display:flex; align-items:center; gap:10px; padding:8px 0; border-bottom:0.5px solid #eee; }
.rank { width:20px; font-size:12px; color:#888; }
.prod-id { width:70px; font-size:13px; font-weight:500; }
.bar-wrap { flex:1; background:#eee; border-radius:4px; height:8px; }
.bar-fill { background:#185FA5; border-radius:4px; height:100%; }
.sold-count { font-size:12px; color:#666; min-width:60px; text-align:right; }
@media(max-width:600px) { .kpi-grid { grid-template-columns:1fr 1fr; } }
"@
[System.IO.File]::WriteAllText("$PWD\src\app\dashboard\dashboard.component.css", $content)
Write-Host "dashboard/dashboard.component.css" -ForegroundColor Green

# ── personalization/personalization.component.ts ────────────
$content = @"
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
"@
[System.IO.File]::WriteAllText("$PWD\src\app\personalization\personalization.component.ts", $content)
Write-Host "personalization/personalization.component.ts" -ForegroundColor Green

# ── personalization/personalization.component.html ──────────
$content = @"
<div class="page">
  <h2 class="page-title">Customer Personalization</h2>
  <div class="search-box">
    <input type="number" [(ngModel)]="userId" placeholder="Enter Customer ID (101 to 600)" (keyup.enter)="search()" />
    <button (click)="search()">Analyze Customer</button>
  </div>
  <div *ngIf="loading" class="loading">Analyzing customer...</div>
  <div *ngIf="error" class="error-msg">{{ error }}</div>
  <div *ngIf="profile && !loading">
    <div class="section-card">
      <div class="profile-header">
        <div class="avatar">{{ profile.user_id }}</div>
        <div>
          <div class="profile-name">Customer #{{ profile.user_id }}</div>
          <div class="profile-meta">{{ profile.age }} yrs | {{ profile.gender }} | {{ profile.location }}</div>
          <span [ngStyle]="getSegStyle(profile.segment)">{{ profile.segment }}</span>
        </div>
      </div>
      <div class="stats-row">
        <div class="stat"><div class="stat-label">Orders</div><div class="stat-value">{{ profile.total_orders }}</div></div>
        <div class="stat"><div class="stat-label">Total Spent</div><div class="stat-value">Rs.{{ profile.total_spend | number:'1.0-0' }}</div></div>
        <div class="stat"><div class="stat-label">Buy Probability</div>
          <div class="stat-value" [style.color]="getProbColor(profile.buy_probability)">{{ pct(profile.buy_probability) }}</div>
        </div>
      </div>
    </div>
    <div class="section-card">
      <h3>Purchase Probability</h3>
      <div class="prob-bar-wrap">
        <div class="prob-bar-fill" [style.width]="pct(profile.buy_probability)" [style.background]="getProbColor(profile.buy_probability)"></div>
      </div>
      <p class="prob-label">{{ pct(profile.buy_probability) }} chance of purchasing</p>
    </div>
    <div class="section-card">
      <h3>Recommended Products</h3>
      <p class="sub">Based on customers similar to you</p>
      <div class="rec-grid">
        <div class="rec-card" *ngFor="let pid of profile.recommendations">
          <div class="rec-id">{{ pid }}</div>
          <div class="rec-label">Recommended</div>
        </div>
      </div>
    </div>
    <div class="section-card explanation">
      <h3>Why these recommendations?</h3>
      <p class="sub">Powered by SHAP Explainable AI</p>
      <div class="reason" *ngFor="let r of profile.reasons; let i = index">
        <span class="reason-icon">{{ i === 0 ? '★' : i === 1 ? '▲' : '●' }}</span>
        {{ r }}
      </div>
    </div>
  </div>
</div>
"@
[System.IO.File]::WriteAllText("$PWD\src\app\personalization\personalization.component.html", $content)
Write-Host "personalization/personalization.component.html" -ForegroundColor Green

# ── personalization/personalization.component.css ───────────
$content = @"
.page { padding:24px; max-width:720px; margin:0 auto; font-family:sans-serif; }
.page-title { font-size:22px; font-weight:600; margin-bottom:20px; }
.search-box { display:flex; gap:10px; margin-bottom:20px; }
.search-box input { flex:1; padding:10px 14px; font-size:14px; border:1px solid #ddd; border-radius:8px; outline:none; }
.search-box button { padding:10px 20px; background:#185FA5; color:white; border:none; border-radius:8px; cursor:pointer; font-size:14px; }
.search-box button:hover { background:#0C447C; }
.loading { text-align:center; padding:40px; color:#888; }
.error-msg { background:#FCEBEB; color:#A32D2D; padding:12px 16px; border-radius:8px; margin-bottom:16px; }
.section-card { background:white; border:0.5px solid #ddd; border-radius:12px; padding:20px; margin-bottom:14px; }
.section-card h3 { font-size:15px; font-weight:600; margin-bottom:4px; }
.sub { font-size:12px; color:#888; margin-bottom:12px; }
.profile-header { display:flex; align-items:center; gap:16px; margin-bottom:16px; }
.avatar { width:52px; height:52px; border-radius:50%; background:#185FA5; color:white; display:flex; align-items:center; justify-content:center; font-size:14px; font-weight:600; }
.profile-name { font-size:16px; font-weight:600; margin-bottom:3px; }
.profile-meta { font-size:13px; color:#666; margin-bottom:6px; }
.stats-row { display:flex; gap:20px; padding-top:14px; border-top:0.5px solid #eee; }
.stat { flex:1; }
.stat-label { font-size:11px; color:#888; margin-bottom:3px; }
.stat-value { font-size:20px; font-weight:600; color:#1a1a1a; }
.prob-bar-wrap { background:#eee; border-radius:6px; height:12px; margin:10px 0; overflow:hidden; }
.prob-bar-fill { height:100%; border-radius:6px; transition:width .5s ease; }
.prob-label { font-size:13px; color:#555; }
.rec-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:8px; }
.rec-card { background:#EAF3DE; border-radius:8px; padding:10px 8px; text-align:center; }
.rec-id { font-size:13px; font-weight:600; color:#3B6D11; }
.rec-label { font-size:10px; color:#5a8a30; margin-top:2px; }
.explanation { background:#E6F1FB; border-color:#B5D4F4; }
.reason { display:flex; align-items:flex-start; gap:10px; padding:9px 0; border-bottom:0.5px solid rgba(24,95,165,0.2); font-size:13px; color:#0C447C; }
.reason:last-child { border-bottom:none; }
.reason-icon { color:#185FA5; font-size:14px; flex-shrink:0; }
@media(max-width:500px) { .rec-grid { grid-template-columns:repeat(3,1fr); } }
"@
[System.IO.File]::WriteAllText("$PWD\src\app\personalization\personalization.component.css", $content)
Write-Host "personalization/personalization.component.css" -ForegroundColor Green

Write-Host ""
Write-Host "ALL DONE!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Terminal 1 - Flask:" -ForegroundColor Yellow
Write-Host "  cd C:\Users\ROJAS\Downloads\customer-ai"
Write-Host "  python api\app.py"
Write-Host ""
Write-Host "Terminal 2 - Angular:" -ForegroundColor Yellow
Write-Host "  ng serve"
Write-Host ""
Write-Host "Browser: http://localhost:4200" -ForegroundColor Green

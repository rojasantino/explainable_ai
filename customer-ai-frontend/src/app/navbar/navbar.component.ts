import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  template: `
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
  `,
  styles: [`
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
  `]
})
export class NavbarComponent {}

import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  template: `
    <nav class="navbar">
      <div class="brand">AI Personalization</div>
      <div class="links">
        <a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{exact:true}">Dashboard</a>
        <a routerLink="/customer" routerLinkActive="active">Customer View</a>
      </div>
    </nav>
  `,
  styles: [`
    .navbar { display:flex; justify-content:space-between; align-items:center;
              padding:12px 24px; background:#185FA5; color:white; }
    .brand { font-size:18px; font-weight:600; }
    .links a { color:rgba(255,255,255,0.85); text-decoration:none; margin-left:20px; font-size:14px; }
    .links a.active { color:white; font-weight:600; border-bottom:2px solid white; padding-bottom:2px; }
  `]
})
export class NavbarComponent {}




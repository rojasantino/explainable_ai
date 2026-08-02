import { Routes } from '@angular/router';
import { DashboardComponent } from './dashboard/dashboard.component';
import { PersonalizationComponent } from './personalization/personalization.component';

export const routes: Routes = [
  { path: '',         component: DashboardComponent },
  { path: 'customer', component: PersonalizationComponent },
];
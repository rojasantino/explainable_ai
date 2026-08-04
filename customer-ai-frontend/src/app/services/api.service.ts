import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private base = '/api';
  constructor(private http: HttpClient) {}
  getCustomerProfile(userId: number): Observable<any> {
    return this.http.get(this.base + '/customer/' + userId);
  }
  getDashboardStats(): Observable<any> {
    return this.http.get(this.base + '/dashboard/stats');
  }
}

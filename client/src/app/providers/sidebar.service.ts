import { Injectable } from '@angular/core';
import { Router, Event, NavigationEnd } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class SidebarService {

  dropDown = 'closed';

  constructor(
    public router: Router
  ) {
    this.router.events.subscribe((event: Event) => {
      if (event instanceof NavigationEnd) {
        if (this.router.url == '/teams') this.dropDown = 'open';
        else this.dropDown = 'closed';
      }
    });
  }
}

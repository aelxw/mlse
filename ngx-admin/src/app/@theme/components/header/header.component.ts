import { Component, Input, OnInit } from '@angular/core';

import { NbMenuService, NbSidebarService } from '@nebular/theme';
import { AnalyticsService } from '../../../@core/utils/analytics.service';
import { LayoutService } from '../../../@core/data/layout.service';
import { NbAuthService, NbAuthJWTToken, NbTokenService } from '@nebular/auth';
import { Router } from '@angular/router';
import { UserService } from '../../../@core/data/users.service';

@Component({
  selector: 'ngx-header',
  styleUrls: ['./header.component.scss'],
  templateUrl: './header.component.html',
})
export class HeaderComponent implements OnInit {

  @Input() position = 'normal';

  user: any;

  constructor(
    private sidebarService: NbSidebarService,
    private menuService: NbMenuService,
    private analyticsService: AnalyticsService,
    private layoutService: LayoutService,
    private authService: NbAuthService,
    private router: Router,
    private tokenService: NbTokenService,
    private userService: UserService
  ) {

    this.authService.onTokenChange().subscribe((token: NbAuthJWTToken) => {
      if(token.isValid()){
        this.user = token.getPayload();
      }
    });

  }

  ngOnInit() {
  }

  toggleSidebar(): boolean {
    this.sidebarService.toggle(true, 'menu-sidebar');
    this.layoutService.changeLayoutSize();

    return false;
  }

  toggleSettings(): boolean {
    this.sidebarService.toggle(false, 'admin-sidebar');

    return false;
  }

  logout() {
    this.tokenService.clear();
    this.router.navigate(['/auth/login']);
  }

  goToHome() {
    this.menuService.navigateHome();
  }

  startSearch() {
    this.analyticsService.trackEvent('startSearch');
  }
}

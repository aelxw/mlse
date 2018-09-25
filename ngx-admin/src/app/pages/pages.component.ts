import { Component } from '@angular/core';

import { MENU_ITEMS } from './pages-menu';
import { NbMenuService } from '@nebular/theme';
import { NbAuthService } from '@nebular/auth';
import { NbMenuBag } from '@nebular/theme/components/menu/menu.service';

@Component({
  selector: 'ngx-pages',
  templateUrl: './pages.component.html'
})
export class PagesComponent {

  menu = MENU_ITEMS;
}

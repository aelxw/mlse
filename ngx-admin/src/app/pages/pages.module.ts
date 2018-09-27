import { NgModule } from '@angular/core';

import { PagesComponent } from './pages.component';
import { DashboardModule } from './dashboard/dashboard.module';
import { ECommerceModule } from './e-commerce/e-commerce.module';
import { PagesRoutingModule } from './pages-routing.module';
import { ThemeModule } from '../@theme/theme.module';
import { MiscellaneousModule } from './miscellaneous/miscellaneous.module';
import { RankingModule } from './ranking/ranking.module';
import { HomeModule } from './home/home.module';
import { AdminModule } from './admin/admin.module';

const PAGES_COMPONENTS = [
  PagesComponent,
];

@NgModule({
  imports: [
    PagesRoutingModule,
    ThemeModule,
    DashboardModule,
    ECommerceModule,
    MiscellaneousModule,
    RankingModule,
    HomeModule,
    AdminModule
  ],
  declarations: [
    ...PAGES_COMPONENTS
  ],
  providers: [
  ]
})
export class PagesModule {
}

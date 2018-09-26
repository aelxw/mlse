import { RouterModule, Routes } from '@angular/router';
import { NgModule } from '@angular/core';

import { PagesComponent } from './pages.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { ECommerceComponent } from './e-commerce/e-commerce.component';
import { NotFoundComponent } from './miscellaneous/not-found/not-found.component';
import { RankingComponent } from './ranking/ranking.component';
import { HomeComponent } from './home/home.component';
import { AdminComponent } from './admin/admin.component';

const routes: Routes = [{
  path: '',
  component: PagesComponent,
  children: [
    {
      path: 'home',
      component: HomeComponent
    },
    {
      path: 'ranking',
      component: RankingComponent
    },
    {
      path: 'admin',
      component: AdminComponent
    },
    {
      path: 'dashboard',
      component: ECommerceComponent,
    }, {
      path: 'iot-dashboard',
      component: DashboardComponent,
    }, {
      path: 'ui-features',
      loadChildren: './ui-features/ui-features.module#UiFeaturesModule',
    }, {
      path: 'components',
      loadChildren: './components/components.module#ComponentsModule',
    }, {
      path: 'maps',
      loadChildren: './maps/maps.module#MapsModule',
    }, {
      path: 'charts',
      loadChildren: './charts/charts.module#ChartsModule',
    }, {
      path: 'editors',
      loadChildren: './editors/editors.module#EditorsModule',
    }, {
      path: 'forms',
      loadChildren: './forms/forms.module#FormsModule',
    }, {
      path: 'tables',
      loadChildren: './tables/tables.module#TablesModule',
    }, {
      path: 'miscellaneous',
      loadChildren: './miscellaneous/miscellaneous.module#MiscellaneousModule',
    }, {
      path: '',
      redirectTo: 'dashboard',
      pathMatch: 'full',
    }, {
      path: '**',
      component: NotFoundComponent,
    }],
}];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class PagesRoutingModule {
}

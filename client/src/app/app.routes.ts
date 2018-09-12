import { Routes, RouterModule } from '@angular/router';

import {IndexComponent} from './index/index.component';
import {RankingComponent} from './ranking/ranking.component';

const appRoutes: Routes = [
  {
    path: '',
    component: IndexComponent
  },
  {
    path: 'ranking',
    component: RankingComponent
  },
];

export const AppRoutes = RouterModule.forRoot(appRoutes);

import { Routes, RouterModule } from '@angular/router';

import { LoginComponent } from './login/login.component';
import { HomeComponent } from './home/home.component';
import { AuthGuardService as authGuardService } from './providers/auth-guard.service';
import { RankingComponent } from './ranking/ranking.component';
import { TeamsComponent } from './teams/teams.component';

const appRoutes: Routes = [
  {
    path: '',
    component: LoginComponent
  },
  {
    path: 'home',
    component: HomeComponent,
    canActivate: [authGuardService],
    children: [
      { path: 'ranking', component: RankingComponent, canActivate: [authGuardService] },
      { path: 'teams', component: TeamsComponent, canActivate: [authGuardService] }
    ]
  },
];

export const AppRoutes = RouterModule.forRoot(appRoutes);

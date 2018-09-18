import { Routes, RouterModule } from '@angular/router';

import {LoginComponent} from './login/login.component';
import {HomeComponent} from './home/home.component';
import { AuthGuardService as authGuardService } from './providers/auth-guard.service';

const appRoutes: Routes = [
  {
    path: '',
    component: LoginComponent
  },
  {
    path: 'home',
    component: HomeComponent,
    canActivate: [authGuardService]
  },
];

export const AppRoutes = RouterModule.forRoot(appRoutes);

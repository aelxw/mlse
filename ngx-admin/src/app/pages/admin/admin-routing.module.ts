import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { AdminComponent } from './admin.component';
import { UsersComponent } from './users/users.component';
import { AdminGuard } from './admin-guard.service';
import { TeamsComponent } from './teams/teams.component';
import { GamesComponent } from './games/games.component';

const routes: Routes = [{
    path: '',
    component: AdminComponent,
    children: [
        {
            path: 'users',
            component: UsersComponent,
            canActivate: [AdminGuard]
        },
        {
            path: 'teams',
            component: TeamsComponent,
            canActivate: [AdminGuard]
        },
        {
            path: 'games',
            component: GamesComponent,
            canActivate: [AdminGuard]
        }
    ],
}];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule],
})
export class AdminRoutingModule { }

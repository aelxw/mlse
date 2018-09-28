import { NgModule } from '@angular/core';

import { ThemeModule } from '../../@theme/theme.module';
import { AdminComponent } from './admin.component';
import { UsersComponent } from './users/users.component';
import { Ng2SmartTableModule } from 'ng2-smart-table';
import { SmartTableService } from '../../@core/data/smart-table.service';
import { AdminRoutingModule } from './admin-routing.module';
import { AdminGuard } from './admin-guard.service';
import { LogoComponent } from './teams/logo.component';
import { TeamsComponent } from './teams/teams.component';
import { GamesComponent } from './games/games.component';

@NgModule({
  imports: [
    ThemeModule,
    Ng2SmartTableModule,
    AdminRoutingModule
  ],
  declarations: [
    AdminComponent,
    UsersComponent,
    TeamsComponent,
    LogoComponent,
    GamesComponent
  ],
  providers: [
    SmartTableService,
    AdminGuard
  ],
  entryComponents: [
    LogoComponent
  ]
})
export class AdminModule { }
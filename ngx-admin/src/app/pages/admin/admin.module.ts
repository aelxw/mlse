import { NgModule } from '@angular/core';

import { ThemeModule } from '../../@theme/theme.module';
import { AdminComponent } from './admin.component';
import { UsersComponent } from './users/users.component';
import { Ng2SmartTableModule } from 'ng2-smart-table';
import { SmartTableService } from '../../@core/data/smart-table.service';

@NgModule({
  imports: [
    ThemeModule,
    Ng2SmartTableModule,
  ],
  declarations: [
    AdminComponent,
    UsersComponent
  ],
  providers: [
    SmartTableService
  ],
})
export class AdminModule { }
import { NgModule } from '@angular/core';
import { Ng2SmartTableModule } from 'ng2-smart-table';

import { ThemeModule } from '../../@theme/theme.module';
import { TablesRoutingModule, routedComponents } from '../tables/tables-routing.module';
import { SmartTableService } from '../../@core/data/smart-table.service';

import { RankingComponent } from './ranking.component';

@NgModule({
  imports: [
    ThemeModule,
    TablesRoutingModule,
    Ng2SmartTableModule
  ],
  declarations: [
    RankingComponent,
    ...routedComponents
  ],
  providers: [
    SmartTableService
  ],
})
export class RankingModule { }

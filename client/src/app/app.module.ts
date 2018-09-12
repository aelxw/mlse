import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MaterialModule } from './material/material.module';
import { AgGridModule } from 'ag-grid-angular';
import { FlexLayoutModule } from '@angular/flex-layout';

import { AppRoutes } from './app.routes';

import { AppComponent } from './app.component';
import { IndexComponent } from './index/index.component';
import { RankingComponent } from './ranking/ranking.component';
import { GridImageComponent } from './gridElements/grid-image/grid-image.component';

import { RestService } from './providers/rest.service';
import { HttpModule } from '@angular/http';

@NgModule({
  declarations: [
    AppComponent,
    IndexComponent,
    RankingComponent,
    GridImageComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    MaterialModule,
    AgGridModule.withComponents([]),
    FlexLayoutModule,
    AppRoutes,
    HttpModule
  ],
  providers: [
    RestService
  ],
  entryComponents: [
    GridImageComponent
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }

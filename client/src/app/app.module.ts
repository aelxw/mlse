import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MaterialModule } from './material/material.module';
import { AgGridModule } from 'ag-grid-angular';
import { FlexLayoutModule } from '@angular/flex-layout';

import { AppRoutes } from './app.routes';

import { AppComponent } from './app.component';
import { RankingComponent } from './ranking/ranking.component';
import { GridImageComponent } from './gridElements/grid-image/grid-image.component';
import { LoginComponent } from './login/login.component';

import { RestService } from './providers/rest.service';
import { HttpModule } from '@angular/http';
import { HomeComponent } from './home/home.component';


@NgModule({
  declarations: [
    AppComponent,
    RankingComponent,
    GridImageComponent,
    LoginComponent,
    HomeComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
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

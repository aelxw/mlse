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
import { AuthGuardService } from './providers/auth-guard.service';
import { UserService } from './providers/user.service';
import { TeamsService } from './providers/teams.service';
import { GamesService } from './providers/games.service';

import { HttpModule } from '@angular/http';
import { HomeComponent } from './home/home.component';
import { SidebarComponent } from './sidebar/sidebar.component';
import { TeamsComponent } from './teams/teams.component';


@NgModule({
  declarations: [
    AppComponent,
    RankingComponent,
    GridImageComponent,
    LoginComponent,
    HomeComponent,
    SidebarComponent,
    TeamsComponent
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
    RestService,
    AuthGuardService,
    UserService,
    TeamsService
  ],
  entryComponents: [
    GridImageComponent
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }

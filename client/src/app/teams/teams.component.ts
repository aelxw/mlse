import { Component, OnInit } from '@angular/core';
import { TeamsService } from '../providers/teams.service';
import { FormControl } from '@angular/forms';
import { MatBottomSheet } from '@angular/material';
import { AddNhlComponent } from '../bottomSheet/add-nhl/add-nhl.component';

@Component({
  selector: 'app-teams',
  templateUrl: './teams.component.html',
  styleUrls: ['./teams.component.css']
})
export class TeamsComponent implements OnInit {

  nhlPlaying: string = "";
  nhlDate: FormControl = new FormControl(new Date());

  constructor(
    public teamsService: TeamsService,
    public bottomSheetService: MatBottomSheet
  ) { }

  ngOnInit() {
  }

  addGame(){
    let data = {
      teamsService: TeamsService
    }
    this.bottomSheetService.open(AddNhlComponent, {data: data});
  }

}

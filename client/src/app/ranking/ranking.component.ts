import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router'
import { UserService } from '../providers/user.service';

@Component({
  selector: 'app-ranking',
  templateUrl: './ranking.component.html',
  styleUrls: ['./ranking.component.css']
})
export class RankingComponent implements OnInit {

  constructor(
    public router: Router,
    public userService: UserService
  ) { }

  ngOnInit() {

  }


}

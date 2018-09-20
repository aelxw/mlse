import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { UserService } from '../providers/user.service';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css']
})
export class SidebarComponent implements OnInit {

  constructor(
    public router: Router,
    public userService: UserService
  ) { }

  ngOnInit() {
  }

  logout() {
    this.userService.logout();
  }

}

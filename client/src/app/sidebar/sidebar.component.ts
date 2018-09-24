import { Component, OnInit } from '@angular/core';
import { Router, Event, NavigationEnd } from '@angular/router';
import { UserService } from '../providers/user.service';
import { trigger, style, animate, transition, state } from '@angular/animations';
import { SidebarService } from '../providers/sidebar.service';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css'],
  animations: [
    trigger(
      'menuAnimation',
      [
        state("closed",
          style({ display: 'none', transform: 'translateX(-100%)' })
        ),
        state("open",
          style({ backgroundColor: 'black', transform: 'translateX(0)' })
        ),
        transition("closed => open", [animate('500ms')]),
        transition('open => closed', [animate('500ms')])
      ]
    )
  ]
})
export class SidebarComponent implements OnInit {

  constructor(
    public router: Router,
    public userService: UserService,
    public sidebarService: SidebarService
  ) {
  }

  ngOnInit() {
  }

  logout() {
    this.userService.logout();
  }

}

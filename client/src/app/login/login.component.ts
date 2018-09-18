import { Component } from '@angular/core';

import { Router } from '@angular/router';
import { RestService } from '../providers/rest.service';
import { Response } from '@angular/http';
import { UserService } from '../providers/user.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {

  email: string = "";
  password: string = "";
  failLogin: boolean = false;
  failMessage: string = "";

  constructor(
    public router: Router,
    public restService: RestService,
    public userService: UserService
  ) { }

  login() {
    this.failLogin = false;

    this.restService.login(this.email, this.password).then(
      (value: Response) => {
        let success = value.json();
        if (success) {
          this.userService.setAuthenticated(true);
          this.router.navigate(["home"]);
        }
        else {
          this.fail("Incorrect credentials");
        }
      }
    );
  }

  fail(msg: string) {
    this.failLogin = true;
    this.failMessage = msg;
  }

}

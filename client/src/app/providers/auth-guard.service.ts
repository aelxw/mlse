import { Injectable } from '@angular/core';
import { Router, CanActivate } from '@angular/router';
import { UserService } from './user.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuardService implements CanActivate {

  constructor(
    public router: Router,
    public userService: UserService
  ) { }

  canActivate(): boolean {
    if(!this.userService.isAuthenticated){
      this.router.navigate([""]);
      return false;
    }
    else{
      return true;
    }
  }
}

import { Injectable } from '@angular/core';
import { RestService } from './rest.service';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  isAuthenticated: boolean = true;
  
  constructor(
    public restService: RestService,
    public router: Router
  ) { }

  setAuthenticated(value: boolean){
    this.isAuthenticated = value;
  }

  logout(){
    this.isAuthenticated = false;
    this.router.navigate([""]);
  }

}

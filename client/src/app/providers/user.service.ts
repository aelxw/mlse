import { Injectable } from '@angular/core';
import { RestService } from './rest.service';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  isAuthenticated: boolean = false;
  
  constructor(
    public restService: RestService
  ) { }

  setAuthenticated(value: boolean){
    this.isAuthenticated = value;
  }

}

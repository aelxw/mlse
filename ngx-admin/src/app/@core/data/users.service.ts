
import { Injectable } from '@angular/core';
import { RestService } from './REST.service';

@Injectable()
export class UserService {

  public users: Array<any> = [];

  constructor(
    public restService: RestService
  ) {

  }

  getUsers(){
    return this.restService.getAllUsers();
  }

}


import { Injectable } from '@angular/core';
import { RestService } from './REST.service';
import { NbTokenService, NbAuthJWTToken } from '@nebular/auth';

@Injectable()
export class UserService {

  public user: any;

  constructor(
    public restService: RestService,
    private tokenService: NbTokenService
  ) {
    this.tokenService.tokenChange().subscribe((token: NbAuthJWTToken) => {
      this.user = token.getPayload();
    });
  }

  getUsers() {
    return this.restService.getAllUsers();
  }

  getUser(){
    return this.user;
  }

}

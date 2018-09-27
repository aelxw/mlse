import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { NbAuthService, NbAuthJWTToken, NbTokenService } from '@nebular/auth';
import { UserService } from '../../@core/data/users.service';

@Injectable()
export class AdminGuard implements CanActivate {

    constructor(
        private userService: UserService,
        private router: Router
    ) {

    }

    canActivate() {
        if(this.userService.getUser()["role"] == "admin"){
            return true;
        }
        else {
            this.router.navigate(['/pages/home']);
            return false;
        }

    }
}
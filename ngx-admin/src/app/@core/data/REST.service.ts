import { Injectable } from '@angular/core';
import { Http, RequestOptionsArgs, Headers, Response } from '@angular/http';
import { map } from 'rxjs/operators';
import { IUser, ITeam } from '../../@theme/interfaces';

@Injectable({
  providedIn: 'root'
})
export class RestService {

  server: string = "http://localhost:2000";

  constructor(
    public http: Http
  ) { }

  httpOptions: RequestOptionsArgs = {
    headers: new Headers({
      'Content-Type': 'application/json'
    })
  };

  private get(endpoint: string) {
    let url = this.server + endpoint;
    return this.http.get(url);
  }

  private post(endpoint: string, data: any) {
    let url = this.server + endpoint;
    return this.http.post(url, data, this.httpOptions);
  }

  deleteUser(email){
      return this.post("/user-delete", {email: email});
  }

  updateRole(data){
      return this.post("/role-update", data);
  }

  getAllUsers(){
      return this.get("/user-get-all").pipe(map<Response, Array<IUser>>(res => res.json()));
  }

  getNHLTeams(){
    return this.get("/teams-get-nhl").pipe(map<Response, Array<ITeam>>(res => res.json()));
  }

  getNBATeams(){
    return this.get("/teams-get-nba").pipe(map<Response, Array<ITeam>>(res => res.json()));
  }

  createTeam(data){
    return this.post("/team-create", data);
  }

  updateTeam(data){
    return this.post("/team-update", data);
  }

  deleteTeam(data){
    return this.post("/team-delete", data);
  }

}

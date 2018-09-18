import { Injectable } from '@angular/core';
import { Http, RequestOptionsArgs, Headers } from '@angular/http';

@Injectable({
  providedIn: 'root'
})
export class RestService {

  server: string = "http://192.168.1.6:2000";

  constructor(
    public http: Http
  ) { }

  httpOptions: RequestOptionsArgs = {
    headers: new Headers({
      'Content-Type': 'application/json'
    })
  };

  get(endpoint: string) {
    let url = this.server + endpoint;
    return this.http.get(url).toPromise();
  }

  post(endpoint: string, data: any) {
    let url = this.server + endpoint;
    return this.http.post(url, data, this.httpOptions).toPromise();
  }

  getTickets() {
    return this.get("/tickets");
  }

  login(email: string, password: string) {
    let data = {
      email: email,
      password: password
    }
    return this.post("/login", data);
  }

}

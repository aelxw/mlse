import { Injectable } from '@angular/core';
import { Http, Response } from '@angular/http';

@Injectable({
  providedIn: 'root'
})
export class RestService {

  server: string = "http://localhost:2000";

  constructor(
    public http: Http
  ) { }


  getTickets() {
    let url = this.server + "/tickets";
    this.http.get(url).toPromise().then(
      (res: Response) => {
        console.log(res.json());
      },
      reason => {
        console.log("/tickets request failed")
      }
    );
  }

}

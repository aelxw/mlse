import { Component, OnInit } from '@angular/core';

import {Router} from '@angular/router';
import { RestService } from '../providers/rest.service';

@Component({
  selector: 'app-index',
  templateUrl: './index.component.html',
  styleUrls: ['./index.component.css']
})
export class IndexComponent implements OnInit {

  constructor(
    public router: Router,
    public restService: RestService
  ) { }

  ngOnInit() {
    
  }

}

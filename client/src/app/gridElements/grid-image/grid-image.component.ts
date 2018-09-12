import { Component } from '@angular/core';

@Component({
  selector: 'app-grid-image',
  templateUrl: './grid-image.component.html',
  styleUrls: ['./grid-image.component.css']
})
export class GridImageComponent {

  constructor() { }

  o: any;
  agInit(params){
    this.o = params.data;
  }

}

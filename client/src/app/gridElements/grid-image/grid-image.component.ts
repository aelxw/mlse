import { Component } from '@angular/core';

@Component({
  selector: 'app-grid-image',
  templateUrl: './grid-image.component.html',
  styleUrls: ['./grid-image.component.css']
})
export class GridImageComponent {

  constructor() { }

  o: any;
  field: string;
  agInit(params){
    this.o = params.data;
    this.field = params.field;
  }

}

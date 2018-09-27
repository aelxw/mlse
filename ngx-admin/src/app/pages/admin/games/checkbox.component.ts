import { Component, Input, OnInit } from '@angular/core';

import { ViewCell } from 'ng2-smart-table';

@Component({
    template: `
    <img src="{{url}}" style="height: 100%">
  `,
})
export class CheckboxComponent implements ViewCell, OnInit {

    renderValue: string;
    url: string;

    @Input() value: string | number;
    @Input() rowData: any;

    ngOnInit() {
        this.url = this.rowData["logo"]
    }

    clicked(){
    }

}
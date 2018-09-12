import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router'

import { GridOptions } from 'ag-grid';
import { GridImageComponent } from '../gridElements/grid-image/grid-image.component';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-ranking',
  templateUrl: './ranking.component.html',
  styleUrls: ['./ranking.component.css']
})
export class RankingComponent implements OnInit {

  GO: GridOptions;
  data: Array<any> = [
    { name: "Toronto Maple Leafs", image: "https://mlse.com/wp-content/uploads/2016/10/16_Leafs_w.png" },
    { name: "Toronto Raptors", image: "http://cc8.980.myftpupload.com/wp-content/uploads/2015/06/211.png" },
    { name: "Toronto FC", image: "https://mlse.com/wp-content/uploads/2014/11/00_TorontoFC_w.png" },
    { name: "Toronto Argos", image: "https://mlse.com/wp-content/uploads/2018/02/Logo_Argos_w-1.png" }
  ];

  routerSubscription: Subscription;

  constructor(
    public router: Router
  ) { }

  ngOnInit() {

    this.GO = {
      onGridReady: (params) => {
        this.GO.api = params.api;
        this.GO.columnApi = params.columnApi;
        this.GO.rowData = this.data;
        this.GO.api.setRowData(this.data);
        this.GO.columnApi.autoSizeAllColumns();
      },
      rowDragManaged: true,
      suppressMovableColumns: true,
      rowHeight: 50,
      columnDefs: [
        {
          headerName: "", field: "name", rowDrag: true
        },
        {
          headerName: "", cellRendererFramework: GridImageComponent, suppressAutoSize: true
        }
      ]
    }

  }


}

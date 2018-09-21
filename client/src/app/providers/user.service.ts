import { Injectable } from '@angular/core';
import { RestService } from './rest.service';
import { Router } from '@angular/router';
import { GridOptions, RowNode } from 'ag-grid';
import { ValueGetterParams } from 'ag-grid/dist/lib/entities/colDef';
import { GridImageComponent } from '../gridElements/grid-image/grid-image.component';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  isAuthenticated: boolean = true;

  rankingGO: GridOptions;
  rankingData: Array<any> = [];


  constructor(
    public restService: RestService,
    public router: Router
  ) {

    this.loadData();

    this.rankingGO = {
      onGridReady: (params) => {
        this.rankingGO.api = params.api;
        this.rankingGO.columnApi = params.columnApi;
        this.rankingGO.rowData = this.rankingData;
        this.rankingGO.api.setRowData(this.rankingData);
        this.rankingGO.columnApi.autoSizeAllColumns();
      },
      suppressMovableColumns: true,
      rowDragManaged: true,
      rowHeight: 50,
      columnDefs: [
        {
          headerName: "Rank",
          valueGetter: (params: ValueGetterParams) => {
            return params.node.rowIndex + 1;
          },
          rowDrag: true,
          width: 100
        },
        {
          headerName: "Date", field: "name"
        },
        {
          headerName: "Game", cellRendererFramework: GridImageComponent
        }
      ]
    }

  }

  loadData(){
    this.rankingData = [
      { name: "Toronto Maple Leafs", image: "https://mlse.com/wp-content/uploads/2016/10/16_Leafs_w.png" },
      { name: "Toronto Raptors", image: "http://cc8.980.myftpupload.com/wp-content/uploads/2015/06/211.png" }
    ];
  }

  setViewData() {
    let viewData: Array<any> = [];
    this.rankingGO.api.forEachNodeAfterFilterAndSort((rowNode: RowNode) => {
      viewData.push(rowNode.data)
    });
    this.rankingData = viewData;
    this.rankingGO.api.setRowData(viewData);
  }

  setAuthenticated(value: boolean) {
    this.isAuthenticated = value;
  }

  logout() {
    this.isAuthenticated = false;
    this.router.navigate([""]);
  }

}

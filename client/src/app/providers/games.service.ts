import { Injectable } from '@angular/core';
import { GridOptions } from 'ag-grid';
import { IGame } from '../interfaces';
import { RestService } from './rest.service';
import { TeamsService } from './teams.service';
import { GridImageComponent } from '../gridElements/grid-image/grid-image.component';

@Injectable({
  providedIn: 'root'
})
export class GamesService {

  nhlGO: GridOptions;
  nhlGames: Array<IGame> = [];

  constructor(
    public restService: RestService,
    public teamsService: TeamsService
  ) {

    this.nhlGO = {
      onGridReady: (params) => {
        this.nhlGO.api = params.api;
        this.nhlGO.columnApi = params.columnApi;
        this.nhlGO.api.setRowData(this.nhlGames);
        this.nhlGO.api.sizeColumnsToFit();

      },
      suppressMovableColumns: true,
      rowDragManaged: true,
      rowHeight: 50,
      columnDefs: [
        {
          headerName: "Team",
          field: "team"
        },
        {
          headerName: "Logo",
          cellRendererFramework: GridImageComponent,
          cellRendererParams: {
            field: "logo"
          }
        }
      ]
    }

  }
}

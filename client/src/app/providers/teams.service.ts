import { Injectable } from '@angular/core';
import { RestService } from './rest.service';
import { Response } from '@angular/http';
import { ITeam } from '../interfaces';
import { GridOptions } from 'ag-grid';
import { GridImageComponent } from '../gridElements/grid-image/grid-image.component';

@Injectable({
  providedIn: 'root'
})
export class TeamsService {

  nhlGO: GridOptions;
  nhlTeams: Array<ITeam> = [];

  constructor(
    public restService: RestService
  ) {

    this.loadNHLTeams();

    this.nhlGO = {
      onGridReady: (params) => {
        this.nhlGO.api = params.api;
        this.nhlGO.columnApi = params.columnApi;
        this.nhlGO.rowData = this.nhlTeams;
        this.nhlGO.api.setRowData(this.nhlTeams);
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


  loadNHLTeams() {
    console.log("hi");
    this.restService.getNHLTeams().then((value: Response) => {
      this.nhlTeams = value.json();
    });
  }

  getNHLLogo(team: string) {
    this.nhlTeams.filter(value => value.team.toLowerCase() == team.toLowerCase());
  }





}

import { Component } from '@angular/core';
import { LocalDataSource } from 'ng2-smart-table';
import { NgForm } from '@angular/forms';
import { ITeam } from '../../../@theme/interfaces';
import { RestService } from '../../../@core/data/REST.service';
import { LogoComponent } from '../teams/logo.component';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'games',
  templateUrl: './games.component.html',
})
export class GamesComponent {

  team: any = {};
  date: Date = new Date();
  benefit: number;
  source: LocalDataSource = new LocalDataSource();
  searching: string = "";

  tempGames: Array<any> = [];
  nhlTeams: Array<ITeam> = [];

  constructor(
    public restService: RestService
  ) {
    this.restService.getNHLTeams().toPromise().then(teams => this.nhlTeams = teams);
  }

  settings = {
    actions: {
      add: false
    },
    pager: {
      perPage: 5
    },
    add: {
      addButtonContent: '<i class="nb-plus"></i>',
      createButtonContent: '<i class="nb-checkmark"></i>',
      cancelButtonContent: '<i class="nb-close"></i>',
    },
    edit: {
      editButtonContent: '<i class="nb-edit"></i>',
      saveButtonContent: '<i class="nb-checkmark"></i>',
      cancelButtonContent: '<i class="nb-close"></i>',
      confirmSave: true
    },
    delete: {
      deleteButtonContent: '<i class="nb-trash"></i>',
      confirmDelete: true,
    },
    columns: {
      image: {
        title: 'Logo',
        type: 'custom',
        renderComponent: LogoComponent,
        editable: false,
        filter: false
      },
      name: {
        title: 'Team',
        type: 'string',
        sort: true,
        sortDirection: 'asc'
      },
      benefit: {
        title: 'Taxable Benefit',
        type: 'number'
      },
      date: {
        title: 'Date',
        type: 'string'
      }
    },
  };

  displayTeam(t: ITeam) {
    if (t) return t.name;
  }

  addTempGame(form: NgForm) {
    let formData = form.value;
    let data = {
      name: formData.team.name,
      logo: formData.team.logo,
      date: new DatePipe("en-us").transform(formData.date, 'EEEE, MMM d, y'),
      benefit: formData.benefit
    }
    this.tempGames.push(data);
    this.source.load(this.tempGames);
    this.team = undefined;
    this.searching = "";
    this.benefit = undefined;
  }

  onDeleteConfirm(event): void {
    if (window.confirm('Are you sure you want to delete?')) {
      this.source.remove(event.data);
      this.source.getAll().then(data => this.tempGames = data);
      event.confirm.resolve();
    } else {
      event.confirm.reject();
    }
    
  }

  onEditConfirm(event) {
    event.confirm.resolve();
  }

}
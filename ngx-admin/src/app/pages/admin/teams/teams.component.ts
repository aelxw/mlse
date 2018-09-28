import { Component } from '@angular/core';
import { LocalDataSource } from 'ng2-smart-table';
import { RestService } from '../../../@core/data/REST.service';
import { LogoComponent } from './logo.component';

@Component({
    selector: 'teams',
    templateUrl: './teams.component.html',
    styles: [`
    nb-card {
        transform: translate3d(0, 0, 0);
    }
    `]
})
export class TeamsComponent {

    settings = {
        actions: {
        },
        pager: {
            perPage: 5
        },
        add: {
            addButtonContent: '<i class="nb-plus"></i>',
            createButtonContent: '<i class="nb-checkmark"></i>',
            cancelButtonContent: '<i class="nb-close"></i>',
            confirmCreate: true
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
            division: {
                title: 'Division',
                type: 'string'
            },
            logo: {
                title: 'Logo URL',
                type: 'string'
            },
        },
    };

    nhlSource: LocalDataSource = new LocalDataSource();
    nhlTeams: Array<any>;

    nbaSource: LocalDataSource = new LocalDataSource();
    nbaTeams: Array<any>;

    constructor(
        private restService: RestService
    ) {
        this.restService.getNHLTeams().toPromise().then(teams => this.nhlSource.load(teams));
        this.restService.getNBATeams().toPromise().then(teams => this.nbaSource.load(teams));
        
    }

    onCreateConfirm(event): void {
        event.newData.show = event.newData.show == 'true';
        this.restService.createTeam(event.newData).toPromise().then(res => {
            event.confirm.resolve();
        }, reason => {
            event.confirm.reject();
        });
    }

    onDeleteConfirm(event): void {
        if (window.confirm('Are you sure you want to delete?')) {
            this.restService.deleteTeam(event.data).toPromise().then(
                res => event.confirm.resolve(),
                reason => event.confirm.reject()
            );
        } else {
            event.confirm.reject();
        }
    }

    onEditConfirm(event): void {
        event.newData.show = event.newData.show == 'true';
        this.restService.updateTeam(event.newData).toPromise().then(res => {
            event.confirm.resolve();
        }, reason => {
            event.confirm.reject();
        });
    }

}

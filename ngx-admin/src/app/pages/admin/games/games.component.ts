import { Component } from '@angular/core';
import { LocalDataSource } from 'ng2-smart-table';
import { RestService } from '../../../@core/data/REST.service';
import { LogoComponent } from './logo.component';

@Component({
    selector: 'games',
    templateUrl: './games.component.html',
    styles: [`
    nb-card {
        transform: translate3d(0, 0, 0);
    }
    `]
})
export class GamesComponent {

    settings = {
        actions: {
        },
        pager: {
            perPage: 12
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
        rowClassFunction: (row) => {
            if (row.data.show) return 'showing'
        },
        columns: {
            show: {
                title: 'Show',
                type: 'html',
                editor: {
                    type: 'list',
                    config: {
                        list: [{ value: true, title: 'true' }, { value: false, title: 'false' }]
                    }
                },
                sort: true,
                sortDirection: 'desc'
            },
            image: {
                title: 'Image',
                type: 'custom',
                renderComponent: LogoComponent,
                editable: false,
                filter: false
            },
            name: {
                title: 'Opponent',
                type: 'string',
            },
            date: {
                title: 'YYYY-MM-DD',
                type: 'string'
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

    source: LocalDataSource = new LocalDataSource();
    allTeams: Array<any>;

    constructor(
        private restService: RestService
    ) {
        this.restService.getAllTeams().subscribe(res => {
            this.allTeams = res.json();
            this.source.load(res.json());
        });
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

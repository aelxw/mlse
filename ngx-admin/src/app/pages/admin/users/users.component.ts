import { Component } from '@angular/core';
import { LocalDataSource, } from 'ng2-smart-table';
import { RestService } from '../../../@core/data/REST.service';
import { map } from 'rxjs/operators';
import { IUser } from '../../../@theme/interfaces';
import { Response } from '@angular/http';

@Component({
  selector: 'users',
  templateUrl: './users.component.html',
  styles: [`
    nb-card {
      transform: translate3d(0, 0, 0);
    }
  `],
})
export class UsersComponent {

  settings = {
    actions: {
      add: false
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
      email: {
        title: 'E-mail',
        type: 'string',
        editable: false
      },
      fullname: {
        title: 'Full Name',
        type: 'string',
        editable: false
      },
      role: {
        title: 'Role',
        type: 'html',
        editor: {
            type: 'list',
            config: {
                list: [{value: 'user', title: 'user'}, {value: 'admin', title: 'admin'}]
            }
        },
    },
    },
  };

  source: LocalDataSource = new LocalDataSource();

  constructor(
    private restService: RestService
  ) {
    this.restService.getAllUsers().toPromise().then(users => this.source.load(users));
  }

  onDeleteConfirm(event): void {
    if (window.confirm('Are you sure you want to delete this user?')) {
      this.restService.deleteUser(event.data["email"]).toPromise().then(res => {
        event.confirm.resolve();
      });

    } else {
      event.confirm.reject();
    }
  }

  onEditConfirm(event): void {
    this.restService.updateRole(event.newData).toPromise().then(res => {
      event.confirm.resolve();
    }, reason => {
      event.confirm.reject();
    });

  }

}

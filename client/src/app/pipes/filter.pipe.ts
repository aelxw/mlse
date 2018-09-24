import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'filter'
})
export class FilterPipe implements PipeTransform {

  transform(objArr: Array<any>, field: string, filterValue: string): any {
    return objArr.filter(o => o[field].toLowerCase().includes(filterValue.toLowerCase()));
  }

}

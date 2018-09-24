import { Component, Inject, OnDestroy } from '@angular/core';
import { MatBottomSheetRef, MAT_BOTTOM_SHEET_DATA } from '@angular/material';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-add-nhl',
  templateUrl: './add-nhl.component.html',
  styleUrls: ['./add-nhl.component.css']
})
export class AddNhlComponent implements OnDestroy {

  backDropSubscription: Subscription;

  constructor(
    private bottomSheetRef: MatBottomSheetRef<AddNhlComponent>,
    @Inject(MAT_BOTTOM_SHEET_DATA) public data: any
  ) {

    this.backDropSubscription = this.bottomSheetRef.backdropClick().subscribe(()=>{
      
    });

  }

  ngOnDestroy() {
    this.backDropSubscription.unsubscribe();
  }

  close(){
    this.bottomSheetRef.dismiss();
  }

}

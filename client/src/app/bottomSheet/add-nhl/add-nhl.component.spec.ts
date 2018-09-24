import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AddNhlComponent } from './add-nhl.component';

describe('AddNhlComponent', () => {
  let component: AddNhlComponent;
  let fixture: ComponentFixture<AddNhlComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AddNhlComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AddNhlComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

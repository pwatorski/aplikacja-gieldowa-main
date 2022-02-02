import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NewDataComponent } from './new-data.component';

describe('NewDataComponent', () => {
  let component: NewDataComponent;
  let fixture: ComponentFixture<NewDataComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ NewDataComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(NewDataComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

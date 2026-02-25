import { ComponentFixture, TestBed } from '@angular/core/testing';

import { JobExecutionsComponent } from './job-executions.component';

describe('JobExecutionsComponent', () => {
  let component: JobExecutionsComponent;
  let fixture: ComponentFixture<JobExecutionsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JobExecutionsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(JobExecutionsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

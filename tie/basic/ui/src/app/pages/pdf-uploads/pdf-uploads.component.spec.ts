import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PdfUploadsComponent } from './pdf-uploads.component';

describe('PdfUploadsComponent', () => {
  let component: PdfUploadsComponent;
  let fixture: ComponentFixture<PdfUploadsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PdfUploadsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PdfUploadsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

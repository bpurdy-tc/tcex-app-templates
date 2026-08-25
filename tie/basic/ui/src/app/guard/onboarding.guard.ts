import { first, map } from 'rxjs/operators';

import { inject } from '@angular/core';
import { CanActivateFn, CanDeactivateFn, Router } from '@angular/router';

import { SettingsComponent } from '../pages/settings/settings.component';
import { OnboardingService } from '../service/onboarding-service/onboarding.service';

/**
 * Redirect to Settings until onboarding is complete.
 *
 * A guard rather than a boot-time redirect in AppComponent: the side nav is visible during
 * onboarding now, so a one-shot redirect would let the operator click away to Dashboard and
 * sit there. This re-asserts on every navigation.
 *
 * `settings` is deliberately NOT guarded — it is the destination.
 */
export const onboardingGuard: CanActivateFn = () => {
    const onboardingService = inject(OnboardingService);
    const router = inject(Router);
    return onboardingService.getStatus().pipe(
        // `getStatus()` is a ReplaySubject that never completes; a guard that does not take
        // exactly one value never resolves and the router hangs on a blank page.
        first(),
        map((status) => (status?.completed ? true : router.createUrlTree(['settings']))),
    );
};

/**
 * Confirm before in-app navigation discards an open stepper.
 *
 * `onboardingGuard` bounces every other route back to `settings`, and that navigation
 * destroys and recreates SettingsComponent — which resets `showStepper` and destroys
 * OnboardingComponent along with every value collected. An operator four steps in who
 * clicks "Dashboard" would otherwise land on the empty state with nothing entered and no
 * warning. The stepper used to be a full-page overlay with the nav HIDDEN precisely so this
 * could not happen; un-gating the nav is what creates the exposure.
 *
 * Deliberately scoped to in-app navigation only. No `beforeunload`: browser close and
 * refresh are out of scope, and nothing is persisted — this is a confirmation, not a draft.
 *
 * The component owns the prompt because the component owns the modal.
 */
export const discardStepperGuard: CanDeactivateFn<SettingsComponent> = (component) =>
    component.showStepper ? component.confirmDiscard() : true;

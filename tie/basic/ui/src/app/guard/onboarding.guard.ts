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
 * Block in-app navigation away from an open stepper, and say why.
 *
 * This is a hard block, NOT a confirmation, because there was never a real choice to
 * offer. `onboardingGuard` bounces every other route straight back to `settings`, so
 * "leave anyway" could not have taken the operator anywhere — the router would return
 * them to this same page. Presenting Discard/Keep-editing implied a decision that did not
 * exist, and picking Discard appeared to do nothing: Angular's default
 * `onSameUrlNavigation: 'ignore'` drops the settings->settings redirect, so the component
 * was never destroyed and the stepper stayed exactly as it was.
 *
 * So: always deny, and show an informational modal explaining that setup has to be
 * finished first. The operator can still abandon setup — that is what the stepper's own
 * controls are for; this only stops the side nav from looking like an exit that works.
 *
 * Deliberately scoped to in-app navigation only. No `beforeunload`: browser close and
 * refresh are out of scope, and nothing here is persisted.
 *
 * The component owns the message because the component owns the modal.
 */
export const discardStepperGuard: CanDeactivateFn<SettingsComponent> = (component) =>
    component.showStepper ? component.blockNavDuringSetup() : true;

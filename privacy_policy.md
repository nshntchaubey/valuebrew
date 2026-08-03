# ValueBrew Privacy Policy

_Last updated: 2026-08-03_

ValueBrew ("the app") is a beer recommendation and price-verification
app. This policy describes what data the app handles, in plain terms.

## Summary

ValueBrew does not require an account, does not collect personal
information, does not run analytics or advertising, and does not track
you. The only thing the app remembers on your device is a cached copy
of its own beer catalog, used purely to keep working offline.

## No accounts, no authentication

There is no sign-up, sign-in, or user account of any kind. The app has
no concept of "your" identity at all.

## Data stored locally on your device

The app uses local device storage (`shared_preferences`) for exactly
one thing:

- **Cached catalog data** — a copy of the beer catalog (beer names,
  prices, styles, value scores), used so the app still works if the
  remote catalog fetch below fails or you're offline.

Nothing else is stored. Your budget, your style preference, a charged
price you're checking, and any recommendation you receive exist only
for the duration of that one screen — closing or navigating away
discards them. None of this is written to your device, sent anywhere,
or retained in any form.

## Remote catalog fetch

On launch, the app attempts to download an updated version of its beer
catalog (prices, styles, and value scores) from a remote file hosted on
a CDN. This is a plain, anonymous file download — the app does not send
any personal information, device identifier, or usage data as part of
this request. If the request fails for any reason (no network, timeout,
or a bad response), the app silently falls back to the catalog already
bundled with or cached on your device — you will never see an error for
this.

As with any network request, the hosting infrastructure (the CDN) may
log standard, generic web-server access data (such as an IP address and
timestamp) as part of normal server operation. ValueBrew does not
access, receive, or process any of that data — it is outside the app's
control and no different from what happens when any device requests any
public file on the internet.

## No analytics, no advertising, no tracking

ValueBrew does not include any analytics SDK, crash-reporting service,
advertising SDK, or tracking library of any kind. There are no ads in
the app. Nothing about how you use the app is measured, recorded
remotely, or shared with any third party.

## Children's privacy

ValueBrew is a general-audience app about alcoholic beverages and is
not directed at children. It collects no personal information from
anyone, regardless of age.

## Changes to this policy

If ValueBrew's data handling ever changes (for example, if a future
version adds any feature that saves something between visits), this
policy will be updated before that change ships, and the "Last updated"
date above will reflect it.

## Contact

Questions about this policy or the app's data handling can be directed
to the app's maintainer via the project's GitHub repository.

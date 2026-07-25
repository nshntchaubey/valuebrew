import 'package:flutter/material.dart';

import 'package:valuebrew/core/constants/app_spacing.dart';

/// A friendly, full-space error message with an optional Retry action —
/// the shared error state for every async screen in the app.
///
/// [message] must already be human-readable; this widget never renders a
/// raw exception or stack trace, by design — a screen's `.when(error: ...)`
/// callback is where a raw error gets turned into a plain-language
/// [message] before it ever reaches this widget.
class ErrorStateView extends StatelessWidget {
  const ErrorStateView({super.key, required this.message, this.onRetry});

  final String message;

  /// Called when the user taps "Retry", or `null` to omit the button
  /// entirely (e.g. when there's nothing meaningful to retry).
  final VoidCallback? onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.error_outline,
              size: 40,
              color: Theme.of(context).colorScheme.error,
            ),
            const SizedBox(height: AppSpacing.sm),
            Text(
              message,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            if (onRetry != null) ...[
              const SizedBox(height: AppSpacing.md),
              FilledButton.tonalIcon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh),
                label: const Text('Retry'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

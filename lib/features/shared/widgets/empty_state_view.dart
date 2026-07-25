import 'package:flutter/material.dart';

import 'package:valuebrew/core/constants/app_spacing.dart';

/// A friendly, full-space "there's nothing here" message — the shared
/// empty state for every screen in the app (no favorites yet, no search
/// results, no beers matching the active filters, ...).
///
/// Every field but [icon] and [title] is optional, so a screen only pays
/// for the richness it actually needs — a search-empty state might be
/// just an icon and a title, while Favorites' first-run state adds a
/// [message] too.
class EmptyStateView extends StatelessWidget {
  const EmptyStateView({
    super.key,
    required this.icon,
    required this.title,
    this.message,
    this.action,
  });

  final IconData icon;
  final String title;
  final String? message;

  /// An optional call to action (e.g. a "Clear filters" button).
  final Widget? action;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 48, color: Theme.of(context).colorScheme.outline),
            const SizedBox(height: AppSpacing.md),
            Text(
              title,
              style: Theme.of(context).textTheme.titleMedium,
              textAlign: TextAlign.center,
            ),
            if (message != null) ...[
              const SizedBox(height: AppSpacing.xs),
              Text(
                message!,
                style: Theme.of(context).textTheme.bodyMedium,
                textAlign: TextAlign.center,
              ),
            ],
            if (action != null) ...[
              const SizedBox(height: AppSpacing.md),
              action!,
            ],
          ],
        ),
      ),
    );
  }
}

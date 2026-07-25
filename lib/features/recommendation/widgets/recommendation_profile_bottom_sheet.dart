import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:valuebrew/features/recommendation/policy/recommendation_profile.dart';
import 'package:valuebrew/features/recommendation/providers/recommendation_providers.dart';
import 'package:valuebrew/features/shared/widgets/bottom_sheet_header.dart';

/// Lets the user pick a [RecommendationProfile] — shown in a modal bottom
/// sheet from `BeerDetailScreen`'s AppBar action.
///
/// Selecting a profile writes to [recommendationProfileProvider]
/// immediately and closes the sheet; there is no separate "Apply" step,
/// matching the requirement that changing profiles updates recommendations
/// right away. This widget only *presents* the four built-in profiles;
/// it makes no recommendation decision itself.
class RecommendationProfileBottomSheet extends ConsumerWidget {
  const RecommendationProfileBottomSheet({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activeProfile = ref.watch(recommendationProfileProvider);

    return SafeArea(
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const BottomSheetHeader(title: 'Recommendation profile'),
            for (final profile in RecommendationProfile.values)
              ListTile(
                title: Text(profile.displayName),
                subtitle: Text(profile.description),
                trailing: profile == activeProfile ? const Icon(Icons.check) : null,
                onTap: () {
                  ref.read(recommendationProfileProvider.notifier).select(profile);
                  Navigator.pop(context);
                },
              ),
          ],
        ),
      ),
    );
  }
}

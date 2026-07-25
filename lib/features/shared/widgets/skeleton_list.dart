import 'package:flutter/material.dart';

import 'package:valuebrew/features/shared/widgets/skeleton_box.dart';

/// A placeholder row roughly matching `buildBeerListTile`'s shape (title
/// line, subtitle line, a small trailing circle standing in for the
/// favorite heart) — shown while [HomeScreen] or [FavoritesScreen] load,
/// instead of a generic spinner.
class BeerListTileSkeleton extends StatelessWidget {
  const BeerListTileSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return const ListTile(
      title: SkeletonBox(width: 160),
      subtitle: Padding(
        padding: EdgeInsets.only(top: 6),
        child: SkeletonBox(width: 100),
      ),
      trailing: SkeletonBox(width: 20, height: 20, borderRadius: 10),
    );
  }
}

/// A scrolling list of [count] [BeerListTileSkeleton] rows — the loading
/// state for any screen showing a beer list.
class BeerListSkeleton extends StatelessWidget {
  const BeerListSkeleton({super.key, this.count = 8});

  final int count;

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: count,
      itemBuilder: (context, index) => const BeerListTileSkeleton(),
    );
  }
}

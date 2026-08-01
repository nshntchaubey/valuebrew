import 'package:flutter/material.dart';

import 'package:valuebrew/core/utils/display_formatting.dart';
import 'package:valuebrew/shared_domain/beer.dart';
import 'package:valuebrew/shared_domain/sku.dart';
import 'package:valuebrew/features/beer_detail/screens/beer_detail_screen.dart';
import 'package:valuebrew/features/shared/catalog_lookups.dart';

/// Builds the shared beer row used by both `HomeScreen` and
/// `FavoritesScreen`: [beer]'s name, brewery, and best available value
/// score (via [bestSkuForBeer] over [skus]), plus a small trailing heart
/// indicating [isFavorite]. Tapping navigates to [BeerDetailScreen].
///
/// A plain function rather than a widget class, matching this codebase's
/// convention for small, single-purpose builders (see `buildBeerColumn` in
/// `compare_screen.dart`) — used by two screens, which is exactly the
/// "more than one call site" bar for sharing this rather than inlining it
/// in each.
///
/// The trailing heart is a plain, non-interactive [Icon] — this screen's
/// row isn't where favorite status is toggled (that's `BeerDetailScreen`'s
/// AppBar action); it only ever indicates status here. Wrapped in
/// [Semantics] so a screen reader announces favorite status even though
/// nothing here is independently tappable, and in [AnimatedSwitcher] so
/// toggling a favorite elsewhere gives this row's heart the same subtle
/// pop `BeerDetailScreen`'s favorite button has, rather than an instant,
/// jarring swap.
Widget buildBeerListTile(
  BuildContext context,
  Beer beer,
  List<Sku> skus, {
  required bool isFavorite,
}) {
  final bestSku = bestSkuForBeer(skus, beer.id);

  return ListTile(
    title: Text(beer.name),
    subtitle: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(beer.brewery),
        Text(
          bestSku == null
              ? 'No SKUs available'
              : 'Value score: ${bestSku.valueScore} '
                  '(${bestSku.valueVerdict.displayLabel})',
        ),
      ],
    ),
    trailing: Semantics(
      label: isFavorite ? 'Favorited' : 'Not favorited',
      child: AnimatedSwitcher(
        duration: const Duration(milliseconds: 200),
        transitionBuilder: (child, animation) =>
            ScaleTransition(scale: animation, child: child),
        child: Icon(
          isFavorite ? Icons.favorite : Icons.favorite_border,
          key: ValueKey(isFavorite),
          size: 20,
          color: isFavorite ? Colors.red : null,
        ),
      ),
    ),
    onTap: () {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (context) => BeerDetailScreen(beer: beer)),
      );
    },
  );
}

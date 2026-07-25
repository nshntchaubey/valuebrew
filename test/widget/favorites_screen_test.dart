import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:valuebrew/data/repositories/catalog_repository.dart';
import 'package:valuebrew/features/beer_detail/screens/beer_detail_screen.dart';
import 'package:valuebrew/features/favorites/screens/favorites_screen.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';

const _catalogJson = '''
{
  "catalog_version": 1,
  "generated_at": "2026-01-01T00:00:00Z",
  "styles": [
    { "id": "lager", "name": "Lager", "description": "Crisp, mild bitterness" }
  ],
  "beers": [
    { "id": "kf_premium", "name": "Kingfisher Premium", "brewery": "United Breweries", "style_id": "lager", "is_craft": false },
    { "id": "toit_porter", "name": "Toit Porter", "brewery": "Toit Brewpub", "style_id": "lager", "is_craft": true },
    { "id": "simba_strong", "name": "Simba Strong", "brewery": "Kals Brewing", "style_id": "lager", "is_craft": false }
  ],
  "skus": [
    {
      "id": "kf_premium_650",
      "beer_id": "kf_premium",
      "size_ml": 650,
      "package_type": "bottle",
      "abv": 4.8,
      "calories": 260,
      "price": 110,
      "price_last_checked": "2026-07-20",
      "price_source": "test",
      "cost_per_litre": 169.2,
      "cost_per_ml_alcohol": 3.52,
      "value_score": 78,
      "value_verdict": "great_value"
    },
    {
      "id": "toit_porter_330",
      "beer_id": "toit_porter",
      "size_ml": 330,
      "package_type": "can",
      "abv": 6.5,
      "calories": 220,
      "price": 250,
      "price_last_checked": "2026-07-18",
      "price_source": "test",
      "cost_per_litre": 757.6,
      "cost_per_ml_alcohol": 11.66,
      "value_score": 55,
      "value_verdict": "fair_value"
    }
  ],
  "benchmarks": []
}
''';

Widget _wrap(Widget child, {required CatalogRepository repository}) {
  return ProviderScope(
    overrides: [catalogRepositoryProvider.overrideWithValue(repository)],
    child: MaterialApp(home: child),
  );
}

void main() {
  final repository = CatalogRepository(
    loadAsset: (key) async => _catalogJson,
    assetKey: 'fake_key',
  );

  testWidgets('shows the empty-state message when nothing is favorited', (
    WidgetTester tester,
  ) async {
    SharedPreferences.setMockInitialValues({});

    await tester.pumpWidget(_wrap(const FavoritesScreen(), repository: repository));
    await tester.pumpAndSettle();

    expect(
      find.text('No favorite beers yet.\n\nTap the heart on any beer to save it.'),
      findsOneWidget,
    );
  });

  testWidgets('lists every favorited beer, and none that aren\'t favorited', (
    WidgetTester tester,
  ) async {
    SharedPreferences.setMockInitialValues({
      'favorite_beer_ids': ['kf_premium', 'toit_porter'],
    });

    await tester.pumpWidget(_wrap(const FavoritesScreen(), repository: repository));
    await tester.pumpAndSettle();

    expect(find.text('Kingfisher Premium'), findsOneWidget);
    expect(find.text('Toit Porter'), findsOneWidget);
    expect(find.text('Simba Strong'), findsNothing);
    expect(
      find.text('No favorite beers yet.\n\nTap the heart on any beer to save it.'),
      findsNothing,
    );
  });

  testWidgets('tapping a favorited beer opens its BeerDetailScreen', (
    WidgetTester tester,
  ) async {
    SharedPreferences.setMockInitialValues({
      'favorite_beer_ids': ['kf_premium'],
    });

    await tester.pumpWidget(_wrap(const FavoritesScreen(), repository: repository));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Kingfisher Premium'));
    await tester.pumpAndSettle();

    expect(find.byType(BeerDetailScreen), findsOneWidget);
    expect(find.widgetWithText(AppBar, 'Kingfisher Premium'), findsOneWidget);
  });

  testWidgets(
    'a favorited beer ID that no longer resolves to any beer in the catalog is skipped, '
    'not a crash',
    (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({
        'favorite_beer_ids': ['kf_premium', 'a_beer_that_was_removed_from_the_catalog'],
      });

      await tester.pumpWidget(_wrap(const FavoritesScreen(), repository: repository));
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
      // The still-resolvable favorite renders normally.
      expect(find.text('Kingfisher Premium'), findsOneWidget);
      // Only one row — the stale ID contributes nothing, not an error row.
      expect(find.byType(ListTile), findsOneWidget);
    },
  );

  testWidgets('shows a loading indicator before the catalog resolves', (
    WidgetTester tester,
  ) async {
    SharedPreferences.setMockInitialValues({});

    await tester.pumpWidget(_wrap(const FavoritesScreen(), repository: repository));

    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });
}

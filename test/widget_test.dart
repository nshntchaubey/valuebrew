import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:valuebrew/catalog/data/catalog_repository.dart';
import 'package:valuebrew/features/beer_detail/screens/beer_detail_screen.dart';
import 'package:valuebrew/features/home/screens/home_screen.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';
import 'package:valuebrew/features/shared/widgets/skeleton_box.dart';

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
  "skus": [],
  "benchmarks": []
}
''';

const _catalogJsonWithSkus = '''
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
      "id": "kf_premium_330",
      "beer_id": "kf_premium",
      "size_ml": 330,
      "package_type": "can",
      "abv": 4.8,
      "calories": 130,
      "price": 90,
      "price_last_checked": "2026-07-20",
      "price_source": "test",
      "cost_per_litre": 272.7,
      "cost_per_ml_alcohol": 5.68,
      "value_score": 40,
      "value_verdict": "overpriced"
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

const _catalogJsonForSorting = '''
{
  "catalog_version": 1,
  "generated_at": "2026-01-01T00:00:00Z",
  "styles": [
    { "id": "lager", "name": "Lager", "description": "Crisp, mild bitterness" }
  ],
  "beers": [
    { "id": "kf_premium", "name": "Kingfisher Premium", "brewery": "United Breweries", "style_id": "lager", "is_craft": false },
    { "id": "simba_strong", "name": "Simba Strong", "brewery": "Kals Brewing", "style_id": "lager", "is_craft": false },
    { "id": "toit_porter", "name": "Toit Porter", "brewery": "Toit Brewpub", "style_id": "lager", "is_craft": true },
    { "id": "mystery_beer", "name": "Mystery Beer", "brewery": "Secret Craft Ltd", "style_id": "lager", "is_craft": false }
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
      "id": "simba_strong_500",
      "beer_id": "simba_strong",
      "size_ml": 500,
      "package_type": "can",
      "abv": 8.0,
      "calories": 300,
      "price": 150,
      "price_last_checked": "2026-07-18",
      "price_source": "test",
      "cost_per_litre": 300.0,
      "cost_per_ml_alcohol": 3.75,
      "value_score": 55,
      "value_verdict": "fair_value"
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
      "value_score": 78,
      "value_verdict": "great_value"
    }
  ],
  "benchmarks": []
}
''';

const _catalogJsonForFiltering = '''
{
  "catalog_version": 1,
  "generated_at": "2026-01-01T00:00:00Z",
  "styles": [
    { "id": "lager", "name": "Lager", "description": "Crisp, mild bitterness" },
    { "id": "stout", "name": "Stout", "description": "Dark, roasted" }
  ],
  "beers": [
    { "id": "kf_premium", "name": "Kingfisher Premium", "brewery": "United Breweries", "style_id": "lager", "is_craft": false },
    { "id": "toit_porter", "name": "Toit Porter", "brewery": "Toit Brewpub", "style_id": "stout", "is_craft": true }
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

/// Opens the Sort bottom sheet from the AppBar and selects [label] — the
/// sheet closes itself on selection.
Future<void> _selectSortOption(WidgetTester tester, String label) async {
  await tester.tap(find.byIcon(Icons.sort));
  await tester.pumpAndSettle();
  await tester.tap(find.text(label));
  await tester.pumpAndSettle();
}

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  testWidgets('HomeScreen shows a loading indicator, then the loaded beers', (
    WidgetTester tester,
  ) async {
    final fakeRepository = CatalogRepository(
      loadAsset: (key) async => _catalogJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          catalogRepositoryProvider.overrideWithValue(fakeRepository),
        ],
        child: MaterialApp(home: const HomeScreen()),
      ),
    );

    expect(find.byType(SkeletonBox), findsWidgets);

    await tester.pumpAndSettle();

    expect(find.text('ValueBrew'), findsOneWidget);
    expect(find.text('Kingfisher Premium'), findsOneWidget);
    expect(find.text('United Breweries'), findsOneWidget);
    expect(find.text('Toit Porter'), findsOneWidget);
    expect(find.text('Toit Brewpub'), findsOneWidget);
  });

  testWidgets('HomeScreen shows an error message when the catalog fails to load', (
    WidgetTester tester,
  ) async {
    final failingRepository = CatalogRepository(
      loadAsset: (key) async => throw Exception('boom'),
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          catalogRepositoryProvider.overrideWithValue(failingRepository),
        ],
        child: MaterialApp(home: const HomeScreen()),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text("Couldn't load the beer catalog."), findsOneWidget);
    expect(find.text('Retry'), findsOneWidget);
  });

  testWidgets('tapping Retry after a load failure reloads the catalog successfully', (
    WidgetTester tester,
  ) async {
    var shouldFail = true;
    final repository = CatalogRepository(
      loadAsset: (key) async {
        if (shouldFail) throw Exception('boom');
        return _catalogJson;
      },
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [catalogRepositoryProvider.overrideWithValue(repository)],
        child: MaterialApp(home: const HomeScreen()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text("Couldn't load the beer catalog."), findsOneWidget);

    shouldFail = false;
    await tester.tap(find.text('Retry'));
    await tester.pumpAndSettle();

    expect(find.text("Couldn't load the beer catalog."), findsNothing);
    expect(find.text('Kingfisher Premium'), findsOneWidget);
  });

  testWidgets(
    'shows a "No beers found" empty state when search matches nothing and no filter is active',
    (WidgetTester tester) async {
      final fakeRepository = CatalogRepository(
        loadAsset: (key) async => _catalogJson,
        assetKey: 'fake_key',
      );

      await tester.pumpWidget(
        ProviderScope(
          overrides: [catalogRepositoryProvider.overrideWithValue(fakeRepository)],
          child: MaterialApp(home: const HomeScreen()),
        ),
      );
      await tester.pumpAndSettle();

      await tester.enterText(find.byType(TextField), 'no beer matches this query at all');
      await tester.pumpAndSettle();

      expect(find.text('No beers found'), findsOneWidget);
      expect(find.text('Try a different search term.'), findsOneWidget);
      // Distinct from the filter-driven empty state, since no filter is active.
      expect(find.text('No beers match your filters'), findsNothing);
    },
  );

  testWidgets('tapping a beer navigates to BeerDetailScreen showing its details', (
    WidgetTester tester,
  ) async {
    final fakeRepository = CatalogRepository(
      loadAsset: (key) async => _catalogJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          catalogRepositoryProvider.overrideWithValue(fakeRepository),
        ],
        child: MaterialApp(home: const HomeScreen()),
      ),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.text('Kingfisher Premium'));
    await tester.pumpAndSettle();

    final detailScreen = find.byType(BeerDetailScreen);
    expect(detailScreen, findsOneWidget);
    expect(
      find.descendant(of: detailScreen, matching: find.text('United Breweries')),
      findsOneWidget,
    );
    expect(
      find.descendant(of: detailScreen, matching: find.text('Lager')),
      findsOneWidget,
    );
  });

  testWidgets(
    'typing in the search field filters by name and brewery, clearing restores the full list',
    (WidgetTester tester) async {
      final fakeRepository = CatalogRepository(
        loadAsset: (key) async => _catalogJson,
        assetKey: 'fake_key',
      );

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            catalogRepositoryProvider.overrideWithValue(fakeRepository),
          ],
          child: MaterialApp(home: const HomeScreen()),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Kingfisher Premium'), findsOneWidget);
      expect(find.text('Toit Porter'), findsOneWidget);
      expect(find.text('Simba Strong'), findsOneWidget);

      // Filter by a name substring, case-insensitive and with whitespace.
      await tester.enterText(find.byType(TextField), '  KING  ');
      await tester.pumpAndSettle();

      expect(find.text('Kingfisher Premium'), findsOneWidget);
      expect(find.text('Toit Porter'), findsNothing);
      expect(find.text('Simba Strong'), findsNothing);

      // Filter by a brewery substring instead.
      await tester.enterText(find.byType(TextField), 'toit brewpub');
      await tester.pumpAndSettle();

      expect(find.text('Toit Porter'), findsOneWidget);
      expect(find.text('Kingfisher Premium'), findsNothing);

      // Clearing the search restores the complete list.
      await tester.enterText(find.byType(TextField), '');
      await tester.pumpAndSettle();

      expect(find.text('Kingfisher Premium'), findsOneWidget);
      expect(find.text('Toit Porter'), findsOneWidget);
      expect(find.text('Simba Strong'), findsOneWidget);
    },
  );

  testWidgets('navigation to BeerDetailScreen continues to work from filtered results', (
    WidgetTester tester,
  ) async {
    final fakeRepository = CatalogRepository(
      loadAsset: (key) async => _catalogJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          catalogRepositoryProvider.overrideWithValue(fakeRepository),
        ],
        child: MaterialApp(home: const HomeScreen()),
      ),
    );
    await tester.pumpAndSettle();

    await tester.enterText(find.byType(TextField), 'king');
    await tester.pumpAndSettle();

    expect(find.text('Kingfisher Premium'), findsOneWidget);
    expect(find.text('Toit Porter'), findsNothing);

    await tester.tap(find.text('Kingfisher Premium'));
    await tester.pumpAndSettle();

    final detailScreen = find.byType(BeerDetailScreen);
    expect(detailScreen, findsOneWidget);
    expect(
      find.descendant(of: detailScreen, matching: find.text('United Breweries')),
      findsOneWidget,
    );
  });

  testWidgets(
    'HomeScreen shows the highest-scoring SKU per beer, and a fallback for beers with none',
    (WidgetTester tester) async {
      final fakeRepository = CatalogRepository(
        loadAsset: (key) async => _catalogJsonWithSkus,
        assetKey: 'fake_key',
      );

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            catalogRepositoryProvider.overrideWithValue(fakeRepository),
          ],
          child: MaterialApp(home: const HomeScreen()),
        ),
      );
      await tester.pumpAndSettle();

      // Kingfisher Premium has two SKUs (78 great_value, 40 overpriced) —
      // the higher-scoring one must be shown, not the lower one.
      expect(find.text('Value score: 78 (Great value)'), findsOneWidget);
      expect(find.text('Value score: 40 (Overpriced for this ABV)'), findsNothing);

      // Toit Porter has a single SKU.
      expect(find.text('Value score: 55 (Fair value)'), findsOneWidget);

      // Simba Strong has no SKUs at all — must not crash, and shows the
      // fallback instead.
      expect(find.text('No SKUs available'), findsOneWidget);
    },
  );

  testWidgets(
    'navigation to BeerDetailScreen still works when rows show a value summary',
    (WidgetTester tester) async {
      final fakeRepository = CatalogRepository(
        loadAsset: (key) async => _catalogJsonWithSkus,
        assetKey: 'fake_key',
      );

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            catalogRepositoryProvider.overrideWithValue(fakeRepository),
          ],
          child: MaterialApp(home: const HomeScreen()),
        ),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.text('Kingfisher Premium'));
      await tester.pumpAndSettle();

      final detailScreen = find.byType(BeerDetailScreen);
      expect(detailScreen, findsOneWidget);
      expect(
        find.descendant(of: detailScreen, matching: find.text('United Breweries')),
        findsOneWidget,
      );
    },
  );

  testWidgets('HomeScreen shows beers in catalog order by default', (
    WidgetTester tester,
  ) async {
    final fakeRepository = CatalogRepository(
      loadAsset: (key) async => _catalogJsonForSorting,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          catalogRepositoryProvider.overrideWithValue(fakeRepository),
        ],
        child: MaterialApp(home: const HomeScreen()),
      ),
    );
    await tester.pumpAndSettle();

    // Catalog order: Kingfisher Premium, Simba Strong, Toit Porter, Mystery Beer.
    final kfY = tester.getTopLeft(find.text('Kingfisher Premium')).dy;
    final simbaY = tester.getTopLeft(find.text('Simba Strong')).dy;
    final toitY = tester.getTopLeft(find.text('Toit Porter')).dy;
    final mysteryY = tester.getTopLeft(find.text('Mystery Beer')).dy;

    expect(kfY, lessThan(simbaY));
    expect(simbaY, lessThan(toitY));
    expect(toitY, lessThan(mysteryY));
  });

  testWidgets(
    'selecting Best value sorts by highest valueScore descending, ties by catalog order, no-SKU beers last',
    (WidgetTester tester) async {
      final fakeRepository = CatalogRepository(
        loadAsset: (key) async => _catalogJsonForSorting,
        assetKey: 'fake_key',
      );

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            catalogRepositoryProvider.overrideWithValue(fakeRepository),
          ],
          child: MaterialApp(home: const HomeScreen()),
        ),
      );
      await tester.pumpAndSettle();

      await _selectSortOption(tester, 'Best Value');

      // kf_premium and toit_porter both score 78 — kf_premium comes first
      // in the catalog, so it must stay first despite simba_strong (55)
      // sitting between them in catalog order. simba_strong (55) comes
      // next, and mystery_beer (no SKUs) is always last.
      final kfY = tester.getTopLeft(find.text('Kingfisher Premium')).dy;
      final toitY = tester.getTopLeft(find.text('Toit Porter')).dy;
      final simbaY = tester.getTopLeft(find.text('Simba Strong')).dy;
      final mysteryY = tester.getTopLeft(find.text('Mystery Beer')).dy;

      expect(kfY, lessThan(toitY));
      expect(toitY, lessThan(simbaY));
      expect(simbaY, lessThan(mysteryY));
    },
  );

  testWidgets('switching back to Relevance restores the original (catalog) order', (
    WidgetTester tester,
  ) async {
    final fakeRepository = CatalogRepository(
      loadAsset: (key) async => _catalogJsonForSorting,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          catalogRepositoryProvider.overrideWithValue(fakeRepository),
        ],
        child: MaterialApp(home: const HomeScreen()),
      ),
    );
    await tester.pumpAndSettle();

    await _selectSortOption(tester, 'Best Value');
    await _selectSortOption(tester, 'Relevance');

    final kfY = tester.getTopLeft(find.text('Kingfisher Premium')).dy;
    final simbaY = tester.getTopLeft(find.text('Simba Strong')).dy;
    final toitY = tester.getTopLeft(find.text('Toit Porter')).dy;
    final mysteryY = tester.getTopLeft(find.text('Mystery Beer')).dy;

    expect(kfY, lessThan(simbaY));
    expect(simbaY, lessThan(toitY));
    expect(toitY, lessThan(mysteryY));
  });

  testWidgets(
    'search followed by Best value sorting applies only to the filtered subset',
    (WidgetTester tester) async {
      final fakeRepository = CatalogRepository(
        loadAsset: (key) async => _catalogJsonForSorting,
        assetKey: 'fake_key',
      );

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            catalogRepositoryProvider.overrideWithValue(fakeRepository),
          ],
          child: MaterialApp(home: const HomeScreen()),
        ),
      );
      await tester.pumpAndSettle();

      // "o" matches Toit Porter and Simba Strong by name, but not
      // Kingfisher Premium or Mystery Beer.
      await tester.enterText(find.byType(TextField), 'o');
      await tester.pumpAndSettle();

      expect(find.text('Toit Porter'), findsOneWidget);
      expect(find.text('Simba Strong'), findsOneWidget);
      expect(find.text('Kingfisher Premium'), findsNothing);
      expect(find.text('Mystery Beer'), findsNothing);

      await _selectSortOption(tester, 'Best Value');

      // Toit Porter (78) must outrank Simba Strong (55) within the
      // filtered subset — Kingfisher Premium, excluded by the search, must
      // not affect this ordering.
      final toitY = tester.getTopLeft(find.text('Toit Porter')).dy;
      final simbaY = tester.getTopLeft(find.text('Simba Strong')).dy;
      expect(toitY, lessThan(simbaY));
    },
  );

  testWidgets('navigation to BeerDetailScreen works after switching to Best value sort', (
    WidgetTester tester,
  ) async {
    final fakeRepository = CatalogRepository(
      loadAsset: (key) async => _catalogJsonForSorting,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          catalogRepositoryProvider.overrideWithValue(fakeRepository),
        ],
        child: MaterialApp(home: const HomeScreen()),
      ),
    );
    await tester.pumpAndSettle();

    await _selectSortOption(tester, 'Best Value');

    await tester.tap(find.text('Kingfisher Premium'));
    await tester.pumpAndSettle();

    final detailScreen = find.byType(BeerDetailScreen);
    expect(detailScreen, findsOneWidget);
    expect(
      find.descendant(of: detailScreen, matching: find.text('United Breweries')),
      findsOneWidget,
    );
  });

  testWidgets(
    'the active-sort indicator updates, and Name (A to Z) orders alphabetically',
    (WidgetTester tester) async {
      final fakeRepository = CatalogRepository(
        loadAsset: (key) async => _catalogJsonForSorting,
        assetKey: 'fake_key',
      );

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            catalogRepositoryProvider.overrideWithValue(fakeRepository),
          ],
          child: MaterialApp(home: const HomeScreen()),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Sorted by: Relevance'), findsOneWidget);

      await _selectSortOption(tester, 'Name (A to Z)');

      expect(find.text('Sorted by: Name (A to Z)'), findsOneWidget);
      expect(find.text('Sorted by: Relevance'), findsNothing);

      // Catalog order is Kingfisher Premium, Simba Strong, Toit Porter,
      // Mystery Beer — alphabetically it's Kingfisher, Mystery, Simba,
      // Toit.
      final kfY = tester.getTopLeft(find.text('Kingfisher Premium')).dy;
      final mysteryY = tester.getTopLeft(find.text('Mystery Beer')).dy;
      final simbaY = tester.getTopLeft(find.text('Simba Strong')).dy;
      final toitY = tester.getTopLeft(find.text('Toit Porter')).dy;

      expect(kfY, lessThan(mysteryY));
      expect(mysteryY, lessThan(simbaY));
      expect(simbaY, lessThan(toitY));
    },
  );

  testWidgets(
    'each beer row shows a filled heart if favorited, an outline heart otherwise',
    (WidgetTester tester) async {
      final semanticsHandle = tester.ensureSemantics();

      SharedPreferences.setMockInitialValues({
        'favorite_beer_ids': ['kf_premium'],
      });
      final fakeRepository = CatalogRepository(
        loadAsset: (key) async => _catalogJson,
        assetKey: 'fake_key',
      );

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            catalogRepositoryProvider.overrideWithValue(fakeRepository),
          ],
          child: MaterialApp(home: const HomeScreen()),
        ),
      );
      await tester.pumpAndSettle();

      final favoritedTile = find.widgetWithText(ListTile, 'Kingfisher Premium');
      final unfavoritedTile = find.widgetWithText(ListTile, 'Toit Porter');

      expect(
        find.descendant(of: favoritedTile, matching: find.byIcon(Icons.favorite)),
        findsOneWidget,
      );
      expect(
        find.descendant(of: unfavoritedTile, matching: find.byIcon(Icons.favorite_border)),
        findsOneWidget,
      );

      // A screen reader announces favorite status even though the heart
      // itself isn't independently tappable on this row. "Favorited"
      // (capital F) never matches "Not favorited" (lowercase f), so this
      // distinguishes the one favorited beer from the two that aren't,
      // in this fixture's three-beer catalog.
      expect(find.bySemanticsLabel(RegExp('Favorited')), findsOneWidget);
      expect(find.bySemanticsLabel(RegExp('Not favorited')), findsNWidgets(2));

      semanticsHandle.dispose();
    },
  );

  testWidgets('Favorites is reachable from HomeScreen via the AppBar action', (
    WidgetTester tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final fakeRepository = CatalogRepository(
      loadAsset: (key) async => _catalogJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          catalogRepositoryProvider.overrideWithValue(fakeRepository),
        ],
        child: MaterialApp(home: const HomeScreen()),
      ),
    );
    await tester.pumpAndSettle();

    await tester.tap(
      find.descendant(of: find.byType(AppBar), matching: find.byIcon(Icons.favorite)),
    );
    await tester.pumpAndSettle();

    expect(find.text('Favorites'), findsOneWidget);
  });

  testWidgets('selecting a style in the filter sheet narrows the visible beer list', (
    WidgetTester tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final fakeRepository = CatalogRepository(
      loadAsset: (key) async => _catalogJsonForFiltering,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [catalogRepositoryProvider.overrideWithValue(fakeRepository)],
        child: MaterialApp(home: const HomeScreen()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Kingfisher Premium'), findsOneWidget);
    expect(find.text('Toit Porter'), findsOneWidget);

    await tester.tap(find.byIcon(Icons.filter_list));
    await tester.pumpAndSettle();

    final styleDropdown = find.byType(DropdownButton<String?>).at(0);
    await tester.tap(styleDropdown);
    await tester.pumpAndSettle();
    await tester.tap(find.text('Stout').last);
    await tester.pumpAndSettle();

    expect(find.text('Toit Porter'), findsOneWidget);
    expect(find.text('Kingfisher Premium'), findsNothing);
    expect(find.text('1 filter active'), findsOneWidget);
  });

  testWidgets('the Clear action on the active-filters indicator restores the full list', (
    WidgetTester tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final fakeRepository = CatalogRepository(
      loadAsset: (key) async => _catalogJsonForFiltering,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [catalogRepositoryProvider.overrideWithValue(fakeRepository)],
        child: MaterialApp(home: const HomeScreen()),
      ),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.byIcon(Icons.filter_list));
    await tester.pumpAndSettle();
    final styleDropdown = find.byType(DropdownButton<String?>).at(0);
    await tester.tap(styleDropdown);
    await tester.pumpAndSettle();
    await tester.tap(find.text('Stout').last);
    await tester.pumpAndSettle();

    // Dismiss the modal bottom sheet (tapping its scrim) so the
    // underlying screen's own "Clear" action becomes tappable.
    await tester.tapAt(const Offset(10, 10));
    await tester.pumpAndSettle();

    expect(find.text('Kingfisher Premium'), findsNothing);

    await tester.tap(find.widgetWithText(TextButton, 'Clear'));
    await tester.pumpAndSettle();

    expect(find.text('Kingfisher Premium'), findsOneWidget);
    expect(find.text('Toit Porter'), findsOneWidget);
    expect(find.textContaining('filter active'), findsNothing);
  });

  testWidgets(
    'shows a friendly empty state when the active filters match no beer, with a working '
    'clear-filters action',
    (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({});
      final fakeRepository = CatalogRepository(
        loadAsset: (key) async => _catalogJsonForFiltering,
        assetKey: 'fake_key',
      );

      await tester.pumpWidget(
        ProviderScope(
          overrides: [catalogRepositoryProvider.overrideWithValue(fakeRepository)],
          child: MaterialApp(home: const HomeScreen()),
        ),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.byIcon(Icons.filter_list));
      await tester.pumpAndSettle();

      // A minimum value score of 100 clears every SKU-scored beer in this
      // fixture (78 and 55), leaving nothing.
      final slider = find.byType(Slider).last;
      await tester.drag(slider, const Offset(1000, 0));
      await tester.pumpAndSettle();

      // Dismiss the modal bottom sheet so the underlying empty state's own
      // "Clear filters" button is the only one, and is tappable.
      await tester.tapAt(const Offset(10, 10));
      await tester.pumpAndSettle();

      expect(find.text('No beers match your filters'), findsOneWidget);

      await tester.tap(find.widgetWithText(TextButton, 'Clear filters'));
      await tester.pumpAndSettle();

      expect(find.text('Kingfisher Premium'), findsOneWidget);
      expect(find.text('Toit Porter'), findsOneWidget);
    },
  );
}

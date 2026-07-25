import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:valuebrew/data/repositories/catalog_repository.dart';
import 'package:valuebrew/features/beer_detail/screens/beer_detail_screen.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';
import 'package:valuebrew/main.dart';

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

void main() {
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
        child: const ValueBrewApp(),
      ),
    );

    expect(find.byType(CircularProgressIndicator), findsOneWidget);

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
        child: const ValueBrewApp(),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.textContaining('Failed to load catalog'), findsOneWidget);
  });

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
        child: const ValueBrewApp(),
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
          child: const ValueBrewApp(),
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
        child: const ValueBrewApp(),
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
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:valuebrew/data/models/beer.dart';
import 'package:valuebrew/data/repositories/catalog_repository.dart';
import 'package:valuebrew/features/beer_detail/screens/beer_detail_screen.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';

const _catalogJson = '''
{
  "catalog_version": 1,
  "generated_at": "2026-01-01T00:00:00Z",
  "styles": [
    { "id": "lager", "name": "Lager", "description": "Crisp, mild bitterness" }
  ],
  "beers": [],
  "skus": [],
  "benchmarks": []
}
''';

const _kfPremium = Beer(
  id: 'kf_premium',
  name: 'Kingfisher Premium',
  brewery: 'United Breweries',
  styleId: 'lager',
  isCraft: false,
);

Widget _wrap(Widget child, {required CatalogRepository repository}) {
  return ProviderScope(
    overrides: [catalogRepositoryProvider.overrideWithValue(repository)],
    child: MaterialApp(home: child),
  );
}

void main() {
  testWidgets('shows a loading indicator before the catalog resolves', (
    WidgetTester tester,
  ) async {
    final repository = CatalogRepository(
      loadAsset: (key) async => _catalogJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      _wrap(const BeerDetailScreen(beer: _kfPremium), repository: repository),
    );

    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });

  testWidgets('shows beer name, brewery, and the resolved style name', (
    WidgetTester tester,
  ) async {
    final repository = CatalogRepository(
      loadAsset: (key) async => _catalogJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      _wrap(const BeerDetailScreen(beer: _kfPremium), repository: repository),
    );
    await tester.pumpAndSettle();

    expect(find.text('Kingfisher Premium'), findsWidgets);
    expect(find.text('United Breweries'), findsOneWidget);
    expect(find.text('Lager'), findsOneWidget);
  });

  testWidgets('falls back to "Unknown style" when the styleId cannot be resolved', (
    WidgetTester tester,
  ) async {
    final repository = CatalogRepository(
      loadAsset: (key) async => _catalogJson,
      assetKey: 'fake_key',
    );
    const orphanBeer = Beer(
      id: 'mystery_beer',
      name: 'Mystery Beer',
      brewery: 'Unknown Brewery',
      styleId: 'nonexistent_style',
      isCraft: false,
    );

    await tester.pumpWidget(
      _wrap(const BeerDetailScreen(beer: orphanBeer), repository: repository),
    );
    await tester.pumpAndSettle();

    expect(find.text('Unknown style'), findsOneWidget);
  });

  testWidgets('shows an error message when the catalog fails to load', (
    WidgetTester tester,
  ) async {
    final repository = CatalogRepository(
      loadAsset: (key) async => throw Exception('boom'),
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      _wrap(const BeerDetailScreen(beer: _kfPremium), repository: repository),
    );
    await tester.pumpAndSettle();

    expect(find.textContaining('Failed to load catalog'), findsOneWidget);
  });
}

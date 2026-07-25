import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:valuebrew/data/models/beer.dart';
import 'package:valuebrew/data/repositories/catalog_repository.dart';
import 'package:valuebrew/features/compare/screens/compare_screen.dart';
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

Future<void> _selectBeer(
  WidgetTester tester,
  Finder dropdownFinder,
  String beerName,
) async {
  await tester.tap(dropdownFinder);
  await tester.pumpAndSettle();
  await tester.tap(find.text(beerName).last);
  await tester.pumpAndSettle();
}

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  testWidgets('shows a loading indicator before the catalog resolves', (
    WidgetTester tester,
  ) async {
    final repository = CatalogRepository(
      loadAsset: (key) async => _catalogJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      _wrap(const CompareScreen(), repository: repository),
    );

    expect(find.byType(SkeletonBox), findsWidgets);
  });

  testWidgets('shows prompts to select both beers before any are chosen', (
    WidgetTester tester,
  ) async {
    final repository = CatalogRepository(
      loadAsset: (key) async => _catalogJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      _wrap(const CompareScreen(), repository: repository),
    );
    await tester.pumpAndSettle();

    expect(find.text('Select Beer A to compare.'), findsOneWidget);
    expect(find.text('Select Beer B to compare.'), findsOneWidget);
  });

  testWidgets('selecting two different beers shows both side by side', (
    WidgetTester tester,
  ) async {
    final repository = CatalogRepository(
      loadAsset: (key) async => _catalogJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      _wrap(const CompareScreen(), repository: repository),
    );
    await tester.pumpAndSettle();

    final dropdowns = find.byType(DropdownButton<Beer>);
    await _selectBeer(tester, dropdowns.at(0), 'Kingfisher Premium');
    await _selectBeer(tester, dropdowns.at(1), 'Toit Porter');

    expect(find.text('United Breweries'), findsOneWidget);
    expect(find.text('Toit Brewpub'), findsOneWidget);
    expect(find.text('Bottle · 650 mL'), findsOneWidget);
    expect(find.text('Can · 330 mL'), findsOneWidget);
    expect(find.text('MRP: ₹110'), findsOneWidget);
    expect(find.text('MRP: ₹250'), findsOneWidget);
    expect(find.text('Value score: 78 (Great value)'), findsOneWidget);
    expect(find.text('Value score: 55 (Fair value)'), findsOneWidget);
  });

  testWidgets('selecting the same beer for both A and B renders it twice, without crashing', (
    WidgetTester tester,
  ) async {
    final repository = CatalogRepository(
      loadAsset: (key) async => _catalogJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      _wrap(const CompareScreen(), repository: repository),
    );
    await tester.pumpAndSettle();

    final dropdowns = find.byType(DropdownButton<Beer>);
    await _selectBeer(tester, dropdowns.at(0), 'Kingfisher Premium');
    await _selectBeer(tester, dropdowns.at(1), 'Kingfisher Premium');

    expect(tester.takeException(), isNull);
    expect(find.text('United Breweries'), findsNWidgets(2));
    expect(find.text('Bottle · 650 mL'), findsNWidgets(2));
    expect(find.text('Value score: 78 (Great value)'), findsNWidgets(2));
  });

  testWidgets('a beer with no SKUs shows the fallback message in its column', (
    WidgetTester tester,
  ) async {
    final repository = CatalogRepository(
      loadAsset: (key) async => _catalogJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      _wrap(const CompareScreen(), repository: repository),
    );
    await tester.pumpAndSettle();

    final dropdowns = find.byType(DropdownButton<Beer>);
    await _selectBeer(tester, dropdowns.at(0), 'Kingfisher Premium');
    await _selectBeer(tester, dropdowns.at(1), 'Mystery Beer');

    expect(find.text('No SKUs available for this beer.'), findsOneWidget);
    // The beer with SKUs still renders correctly alongside it.
    expect(find.text('Value score: 78 (Great value)'), findsOneWidget);
  });

  testWidgets('shows an error message when the catalog fails to load', (
    WidgetTester tester,
  ) async {
    final repository = CatalogRepository(
      loadAsset: (key) async => throw Exception('boom'),
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      _wrap(const CompareScreen(), repository: repository),
    );
    await tester.pumpAndSettle();

    expect(find.text("Couldn't load the beer catalog."), findsOneWidget);
    expect(find.text('Retry'), findsOneWidget);
  });

  testWidgets('CompareScreen is reachable from HomeScreen via the AppBar action', (
    WidgetTester tester,
  ) async {
    final repository = CatalogRepository(
      loadAsset: (key) async => _catalogJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      _wrap(const HomeScreen(), repository: repository),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.byIcon(Icons.compare_arrows));
    await tester.pumpAndSettle();

    expect(find.byType(CompareScreen), findsOneWidget);
    expect(find.text('Compare Beers'), findsOneWidget);
  });
}

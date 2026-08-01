import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:valuebrew/catalog/data/catalog_repository.dart';
import 'package:valuebrew/features/discovery/presentation/home_screen.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';
import 'package:valuebrew/main.dart';

const _catalogJson = '''
{
  "catalog_version": 1,
  "generated_at": "2026-01-01T00:00:00Z",
  "styles": [],
  "beers": [],
  "skus": [],
  "benchmarks": []
}
''';

void main() {
  testWidgets('ValueBrewApp launches on the new canonical HomeScreen', (WidgetTester tester) async {
    final fakeRepository = CatalogRepository(
      loadAsset: (key) async => _catalogJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [catalogRepositoryProvider.overrideWithValue(fakeRepository)],
        child: const ValueBrewApp(),
      ),
    );

    expect(find.byType(HomeScreen), findsOneWidget);
    expect(find.text('Get a recommendation'), findsOneWidget);
  });
}

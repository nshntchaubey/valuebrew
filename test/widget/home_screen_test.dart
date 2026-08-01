import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:valuebrew/catalog/data/catalog_repository.dart';
import 'package:valuebrew/features/discovery/presentation/home_screen.dart';
import 'package:valuebrew/features/recommendation/presentation/recommendation_screen.dart';
import 'package:valuebrew/features/shared/providers/catalog_provider.dart';
import 'package:valuebrew/navigation/value_brew_navigator.dart';

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
  testWidgets('tapping "Get a recommendation" navigates to the real RecommendationScreen', (
    WidgetTester tester,
  ) async {
    final fakeRepository = CatalogRepository(
      loadAsset: (key) async => _catalogJson,
      assetKey: 'fake_key',
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [catalogRepositoryProvider.overrideWithValue(fakeRepository)],
        child: MaterialApp(
          navigatorKey: rootNavigatorKey,
          home: const HomeScreen(),
        ),
      ),
    );

    expect(find.byType(RecommendationScreen), findsNothing);

    await tester.tap(find.text('Get a recommendation'));
    await tester.pumpAndSettle();

    expect(find.byType(RecommendationScreen), findsOneWidget);
  });
}

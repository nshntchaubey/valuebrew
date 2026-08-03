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

const _planningCaveat =
    'This is a provisional recommendation for planning ahead — prices '
    'and availability may have changed by the time you actually buy.';

void main() {
  Future<void> pumpHomeScreen(WidgetTester tester) async {
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
  }

  testWidgets('tapping "Get a recommendation" navigates to the real RecommendationScreen', (
    WidgetTester tester,
  ) async {
    await pumpHomeScreen(tester);

    expect(find.byType(RecommendationScreen), findsNothing);

    await tester.tap(find.text('Get a recommendation'));
    await tester.pumpAndSettle();

    expect(find.byType(RecommendationScreen), findsOneWidget);
  });

  testWidgets('the default recommendation path opens Recommendation without the Planning banner', (
    WidgetTester tester,
  ) async {
    await pumpHomeScreen(tester);

    await tester.tap(find.text('Get a recommendation'));
    await tester.pumpAndSettle();

    final submitButton = find.descendant(
      of: find.byType(RecommendationScreen),
      matching: find.widgetWithText(ElevatedButton, 'Get a recommendation'),
    );
    await tester.enterText(find.byType(TextField), '150');
    await tester.tap(submitButton);
    await tester.pumpAndSettle();

    expect(find.text(_planningCaveat), findsNothing);
  });

  testWidgets('"I\'m planning ahead" opens Recommendation with the Planning banner visible', (
    WidgetTester tester,
  ) async {
    await pumpHomeScreen(tester);

    await tester.tap(find.text("I'm planning ahead"));
    await tester.pumpAndSettle();

    expect(find.byType(RecommendationScreen), findsOneWidget);

    final submitButton = find.descendant(
      of: find.byType(RecommendationScreen),
      matching: find.widgetWithText(ElevatedButton, 'Get a recommendation'),
    );
    await tester.enterText(find.byType(TextField), '150');
    await tester.tap(submitButton);
    await tester.pumpAndSettle();

    expect(find.text(_planningCaveat), findsOneWidget);
  });
}

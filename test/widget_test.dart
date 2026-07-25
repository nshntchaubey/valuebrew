import 'package:flutter_test/flutter_test.dart';

import 'package:valuebrew/main.dart';

void main() {
  testWidgets('HomeScreen shows the ValueBrew title and tagline', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const ValueBrewApp());

    expect(find.text('ValueBrew'), findsOneWidget);
    expect(find.textContaining('Find the best beer.'), findsOneWidget);
    expect(find.textContaining('One pint at a time.'), findsOneWidget);
  });
}

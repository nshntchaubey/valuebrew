import 'package:flutter_test/flutter_test.dart';
import 'package:valuebrew/data/models/sku.dart';
import 'package:valuebrew/features/recommendation/models/recommendation.dart';
import 'package:valuebrew/features/recommendation/models/recommendation_reason.dart';

Sku _sku({String id = 'a'}) {
  return Sku(
    id: id,
    beerId: 'kf',
    sizeMl: 650,
    packageType: PackageType.bottle,
    abv: 5.0,
    calories: 250,
    price: 100,
    priceLastChecked: DateTime(2026, 1, 1),
    priceSource: 'test',
    costPerLitre: 150,
    costPerMlAlcohol: 4.0,
    valueScore: 50,
    valueVerdict: ValueVerdict.fairValue,
  );
}

void main() {
  group('RecommendationReasonFormatting', () {
    test('every reason has a distinct, human-readable display label', () {
      final labels = RecommendationReason.values.map((r) => r.displayLabel).toSet();

      expect(labels.length, RecommendationReason.values.length);
      expect(RecommendationReason.sameStyle.displayLabel, 'Same style');
      expect(RecommendationReason.sameBrewery.displayLabel, 'Same brewery');
      expect(RecommendationReason.similarAbv.displayLabel, 'Similar ABV');
      expect(RecommendationReason.similarPrice.displayLabel, 'Similar price');
      expect(RecommendationReason.samePackage.displayLabel, 'Same package');
      expect(RecommendationReason.betterValue.displayLabel, 'Better value');
    });
  });

  group('Recommendation.reasonSummary', () {
    test('joins multiple reasons with a bullet separator, in list order', () {
      final recommendation = Recommendation(
        sku: _sku(),
        overallScore: 0.9,
        matchedReasons: const [RecommendationReason.sameStyle, RecommendationReason.similarAbv],
        type: RecommendationType.similar,
      );

      expect(recommendation.reasonSummary, 'Same style • Similar ABV');
    });

    test('a single reason has no separator', () {
      final recommendation = Recommendation(
        sku: _sku(),
        overallScore: 0.9,
        matchedReasons: const [RecommendationReason.betterValue],
        type: RecommendationType.betterValue,
      );

      expect(recommendation.reasonSummary, 'Better value');
    });

    test('is null when there are no matched reasons', () {
      final recommendation = Recommendation(
        sku: _sku(),
        overallScore: 0.0,
        matchedReasons: const [],
        type: RecommendationType.similar,
      );

      expect(recommendation.reasonSummary, isNull);
    });
  });

  group('Recommendation equality', () {
    test('two Recommendations with identical field values are equal', () {
      final a = Recommendation(
        sku: _sku(),
        overallScore: 0.9,
        matchedReasons: const [RecommendationReason.sameStyle],
        type: RecommendationType.similar,
      );
      final b = Recommendation(
        sku: _sku(),
        overallScore: 0.9,
        matchedReasons: const [RecommendationReason.sameStyle],
        type: RecommendationType.similar,
      );

      expect(a, b);
      expect(a.hashCode, b.hashCode);
    });

    test('Recommendations differing by matchedReasons are not equal', () {
      final a = Recommendation(
        sku: _sku(),
        overallScore: 0.9,
        matchedReasons: const [RecommendationReason.sameStyle],
        type: RecommendationType.similar,
      );
      final b = Recommendation(
        sku: _sku(),
        overallScore: 0.9,
        matchedReasons: const [RecommendationReason.sameBrewery],
        type: RecommendationType.similar,
      );

      expect(a, isNot(b));
    });

    test('Recommendations differing by type are not equal', () {
      final a = Recommendation(
        sku: _sku(),
        overallScore: 0.9,
        matchedReasons: const [],
        type: RecommendationType.similar,
      );
      final b = Recommendation(
        sku: _sku(),
        overallScore: 0.9,
        matchedReasons: const [],
        type: RecommendationType.betterValue,
      );

      expect(a, isNot(b));
    });
  });
}

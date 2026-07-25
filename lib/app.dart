import 'package:flutter/material.dart';

import 'package:valuebrew/features/home/screens/home_screen.dart';

/// The app's shared [ThemeData] — a single, amber-seeded Material 3 color
/// scheme (evoking beer, rather than Flutter's stock indigo default) plus
/// a handful of component themes chosen for consistency, not for a new
/// design language: every widget in the app still renders as standard
/// Material widgets, just themed from one place instead of picking
/// incidental defaults per screen.
final ThemeData _appTheme = ThemeData(
  useMaterial3: true,
  colorScheme: ColorScheme.fromSeed(seedColor: Colors.amber.shade800),
  appBarTheme: const AppBarTheme(centerTitle: true),
  dividerTheme: const DividerThemeData(space: 24, thickness: 1),
  listTileTheme: const ListTileThemeData(
    contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
  ),
  cardTheme: const CardThemeData(
    margin: EdgeInsets.symmetric(vertical: 4),
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.all(Radius.circular(12))),
  ),
  bottomSheetTheme: const BottomSheetThemeData(
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
    ),
  ),
  snackBarTheme: const SnackBarThemeData(behavior: SnackBarBehavior.floating),
);

class ValueBrewApp extends StatelessWidget {
  const ValueBrewApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ValueBrew',
      debugShowCheckedModeBanner: false,
      theme: _appTheme,
      home: const HomeScreen(),
    );
  }
}

import 'package:flutter/material.dart';

import 'package:valuebrew/features/home/screens/home_screen.dart';

class ValueBrewApp extends StatelessWidget {
  const ValueBrewApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ValueBrew',
      debugShowCheckedModeBanner: false,
      home: const HomeScreen(),
    );
  }
}

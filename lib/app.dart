import 'package:flutter/material.dart';

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

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('ValueBrew'),
        centerTitle: true,
      ),
      body: const Center(
        child: Text(
          'Find the best beer.\nOne pint at a time.',
          textAlign: TextAlign.center,
          style: TextStyle(
            fontSize: 24,
          ),
        ),
      ),
    );
  }
}

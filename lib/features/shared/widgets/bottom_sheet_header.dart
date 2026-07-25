import 'package:flutter/material.dart';

/// The shared header every modal bottom sheet in the app starts with: a
/// small drag handle (the standard Material affordance signalling "this
/// can be dragged down to dismiss") followed by a title.
///
/// Used by the Filter, Sort, and Recommendation Profile sheets so all
/// three look and feel like the same family of UI rather than three
/// independently-styled ones — the one thing that's meant to differ
/// between them is [title] and whatever comes after this widget.
class BottomSheetHeader extends StatelessWidget {
  const BottomSheetHeader({super.key, required this.title});

  final String title;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Center(
          child: Container(
            margin: const EdgeInsets.only(top: 8),
            width: 32,
            height: 4,
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.outlineVariant,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
          child: Text(title, style: Theme.of(context).textTheme.titleMedium),
        ),
      ],
    );
  }
}

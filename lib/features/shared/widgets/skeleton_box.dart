import 'package:flutter/material.dart';

/// A single placeholder block that gently pulses in place of real content
/// while it loads.
///
/// This is the app's entire "skeleton loading" mechanism — no shimmer or
/// animation package, just an [AnimationController] driving a slow opacity
/// pulse (`0.4` to `0.8`) between two repaints, which is what "avoid
/// excessive animation" means in practice here: a subtle, continuous
/// breathing effect, not a moving gradient sweep.
class SkeletonBox extends StatefulWidget {
  const SkeletonBox({super.key, this.width, this.height = 14, this.borderRadius = 4});

  /// Fixed width, or `null` to fill whatever space is available.
  final double? width;

  final double height;
  final double borderRadius;

  @override
  State<SkeletonBox> createState() => _SkeletonBoxState();
}

class _SkeletonBoxState extends State<SkeletonBox> with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 900),
  )..repeat(reverse: true);

  late final Animation<double> _opacity = Tween<double>(begin: 0.4, end: 0.8).animate(
    CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
  );

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final baseColor = Theme.of(context).colorScheme.onSurface;

    return AnimatedBuilder(
      animation: _opacity,
      builder: (context, child) {
        return Container(
          width: widget.width,
          height: widget.height,
          decoration: BoxDecoration(
            color: baseColor.withValues(alpha: _opacity.value * 0.12),
            borderRadius: BorderRadius.circular(widget.borderRadius),
          ),
        );
      },
    );
  }
}

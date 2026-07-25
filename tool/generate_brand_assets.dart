// Regenerates ValueBrew's Android launcher icon (legacy + adaptive +
// Android 13+ monochrome) and splash foreground assets from one vector
// definition drawn in code, so the brand mark is a single source of truth
// instead of a set of hand-exported PNGs.
//
// Deliberately NOT a package dependency (no flutter_launcher_icons /
// flutter_native_splash): this draws directly with dart:ui, which is
// already part of the Flutter SDK, run through flutter_test's binding
// purely to get engine access for image encoding — nothing here is an
// actual test and this file is not picked up by a plain `flutter test`
// (it lives under tool/, outside the test/ directory flutter test scans).
//
// Re-run after changing the mark:
//   flutter test tool/generate_brand_assets.dart
import 'dart:io';
import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

/// Matches the app's theme seed color (`Colors.amber.shade800` in
/// lib/app.dart) — the adaptive icon background and splash background both
/// use this exact value so the launcher icon, splash, and in-app theme read
/// as one brand, not three approximations of it.
const Color _brandAmber800 = Color(0xFFFF8F00);
const Color _glassCream = Color(0xFFFFF8E1);
const Color _bubbleAmber = Color(0xFFFFC107);

/// The pint-glass mark, drawn as fractions of a square canvas so it can be
/// rendered at any pixel size. Bounding box is kept inside a circle of
/// diameter ~0.6 of the canvas, centered — Android's adaptive icon safe
/// zone (content must survive a circular, squircle, or rounded-square mask
/// applied by the launcher).
void _paintMark(Canvas canvas, Size size, {required Color glassColor, Color? bubbleColor}) {
  final w = size.width;
  final h = size.height;
  final glassPath = Path()
    ..moveTo(w * 0.32, h * 0.26)
    ..lineTo(w * 0.68, h * 0.26)
    ..quadraticBezierTo(w * 0.685, h * 0.30, w * 0.66, h * 0.34)
    ..lineTo(w * 0.63, h * 0.74)
    ..quadraticBezierTo(w * 0.5, h * 0.79, w * 0.37, h * 0.74)
    ..lineTo(w * 0.34, h * 0.34)
    ..quadraticBezierTo(w * 0.315, h * 0.30, w * 0.32, h * 0.26)
    ..close();
  canvas.drawPath(glassPath, Paint()..color = glassColor);

  if (bubbleColor != null) {
    final bubblePaint = Paint()..color = bubbleColor;
    canvas.drawCircle(Offset(w * 0.44, h * 0.38), w * 0.028, bubblePaint);
    canvas.drawCircle(Offset(w * 0.565, h * 0.47), w * 0.022, bubblePaint);
    canvas.drawCircle(Offset(w * 0.48, h * 0.58), w * 0.02, bubblePaint);
  }
}

Future<Uint8List> _renderPng(
  int sizePx,
  void Function(Canvas canvas, Size size) paint,
) async {
  final recorder = ui.PictureRecorder();
  final canvas = Canvas(recorder);
  paint(canvas, Size(sizePx.toDouble(), sizePx.toDouble()));
  final picture = recorder.endRecording();
  final image = await picture.toImage(sizePx, sizePx);
  final byteData = await image.toByteData(format: ui.ImageByteFormat.png);
  return byteData!.buffer.asUint8List();
}

Future<void> _write(String path, Uint8List bytes) async {
  final file = File(path);
  await file.parent.create(recursive: true);
  await file.writeAsBytes(bytes);
  // ignore: avoid_print
  print('Wrote $path (${bytes.length} bytes)');
}

const _androidRes = 'android/app/src/main/res';

/// mipmap density -> legacy launcher icon size (48dp base).
const _legacySizes = {'mdpi': 48, 'hdpi': 72, 'xhdpi': 96, 'xxhdpi': 144, 'xxxhdpi': 192};

/// mipmap density -> adaptive icon layer size (108dp base).
const _adaptiveSizes = {'mdpi': 108, 'hdpi': 162, 'xhdpi': 216, 'xxhdpi': 324, 'xxxhdpi': 432};

Future<void> main() async {
  TestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('regenerate brand assets', (tester) async {
    // picture.toImage()/File I/O are genuinely async engine/OS work, which
    // never resolves inside testWidgets' default FakeAsync zone — runAsync
    // escapes to the real event loop so these futures actually complete.
    await tester.runAsync(() async {
      // Legacy launcher icon (pre-Android-8 devices, and the fallback the
      // <application android:icon> attribute still points at): background +
      // mark flattened onto one square, since there is no separate layer to
      // mask on these OS versions.
      for (final entry in _legacySizes.entries) {
        final bytes = await _renderPng(entry.value, (canvas, size) {
          canvas.drawRect(Offset.zero & size, Paint()..color = _brandAmber800);
          _paintMark(canvas, size, glassColor: _glassCream, bubbleColor: _bubbleAmber);
        });
        await _write('$_androidRes/mipmap-${entry.key}/ic_launcher.png', bytes);
      }

      // Adaptive icon foreground layer: mark only, transparent background —
      // the background color comes from the separate
      // `ic_launcher_background` layer so the OS can animate/mask them
      // independently.
      for (final entry in _adaptiveSizes.entries) {
        final bytes = await _renderPng(entry.value, (canvas, size) {
          _paintMark(canvas, size, glassColor: _glassCream, bubbleColor: _bubbleAmber);
        });
        await _write(
          '$_androidRes/mipmap-${entry.key}/ic_launcher_foreground.png',
          bytes,
        );
      }

      // Android 13+ monochrome layer: same mark, single opaque color — the
      // OS applies its own tint, so color choice here doesn't matter beyond
      // being fully opaque where the mark should be visible.
      for (final entry in _adaptiveSizes.entries) {
        final bytes = await _renderPng(entry.value, (canvas, size) {
          _paintMark(canvas, size, glassColor: Colors.white);
        });
        await _write(
          '$_androidRes/mipmap-${entry.key}/ic_launcher_monochrome.png',
          bytes,
        );
      }
    });
  });
}

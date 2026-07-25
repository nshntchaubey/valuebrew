# Third-Party Notices

ValueBrew is built with the Flutter SDK and the following open-source
packages. All of them use permissive licenses (BSD-3-Clause or MIT) that
impose no copyleft or source-disclosure obligations — the only shared
requirement is retaining each package's copyright notice, which this file
does.

| Package | Version | License | Purpose |
|---|---|---|---|
| [Flutter SDK](https://github.com/flutter/flutter) | 3.44.8 | BSD-3-Clause | Application framework |
| [flutter_riverpod](https://pub.dev/packages/flutter_riverpod) | ^2.6.1 | MIT | State management |
| [http](https://pub.dev/packages/http) | ^1.2.2 | BSD-3-Clause | Remote catalog fetch |
| [shared_preferences](https://pub.dev/packages/shared_preferences) | ^2.3.3 | BSD-3-Clause | Local persistence (favorites, cached catalog) |
| [path_provider](https://pub.dev/packages/path_provider) | ^2.1.5 | BSD-3-Clause | Filesystem path access |
| [cupertino_icons](https://pub.dev/packages/cupertino_icons) | ^1.0.8 | MIT | iOS-style icon font |
| [flutter_lints](https://pub.dev/packages/flutter_lints) | ^6.0.0 (dev) | BSD-3-Clause | Static analysis rules |

## License texts

### BSD-3-Clause (Flutter SDK, http, shared_preferences, path_provider, flutter_lints)

```
Copyright 2013 The Flutter Authors / 2014 the Dart project authors. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above
      copyright notice, this list of conditions and the following
      disclaimer in the documentation and/or other materials provided
      with the distribution.
    * Neither the name of Google LLC nor the names of its
      contributors may be used to endorse or promote products derived
      from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
```

### MIT (flutter_riverpod, cupertino_icons)

```
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
```

## In-app attribution

Flutter apps expose every bundled package's full license text at runtime
via `showLicensePage`/`LicenseRegistry`, which `MaterialApp` wires up
automatically (Settings → About, or any screen that calls
`showAboutDialog`) — no extra code is required for this. This file exists
for anyone auditing the repository itself, not as a substitute for that
in-app page.

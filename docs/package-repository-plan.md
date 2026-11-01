# Custom compile, normal Debian packaging

This is a custom PPC/SPE rebuild based on Debian sources and packaging, not an
official Debian powerpcspe release. Preserve normal Debian runtime and package
behavior while applying attributable compatibility patches at source level.
Retain upstream version/source provenance and distinguish our revisions, for
example a reviewed +tabor1 suffix. Do not rename all packages into bundles or
reuse incompatible generic PowerPC binaries.

## Compact browser

NetSurf GTK is the initial candidate, not a proven SPE build. Its own engine
avoids making a modern heavyweight engine the first browser milestone. Upstream
reports limited/incomplete JavaScript support, so its intended use is local
build documentation and basic browsing, not modern web apps or noVNC assurance.
Pin the Debian source and dependencies first; test actual target text, images,
scrolling and HTTPS certificate verification before including it in an image.
GTK and all other mandatory libraries remain ordinary package dependencies.
Do not disable TLS verification to get a browser acceptance result.

Sources: https://www.netsurf-browser.org/about/ and
https://www.netsurf-browser.org/documentation/progress.html .

## Repository

Start with reprepro-managed static APT metadata and an ordinary lab HTTP server.
Gitea can retain source/patch history and build artifacts; target installation
should use apt with a proper repository rather than downloading release assets
as a package resolver. No Gitea capability or new service is assumed deployed.

Proposed archive: suite tabor-trixie, component main, architecture powerpcspe,
with Architecture: all packages built from the selected source where valid.
Keep QEMU and A1222 packages in one ABI archive; select machine-specific kernels,
firmware and configuration through separate packages/profiles. Do not multiply
the common userspace into two incompatible repositories.

Retain .deb, .dsc, source tar/diff, .buildinfo, .changes, source/patch/toolchain
hashes and build/test receipts. Import each complete accepted package build,
export Packages/Sources/Release plus signed InRelease (or Release.gpg), and
publish a consistent snapshot atomically. Use our own archive signing key and
a dedicated keyring referenced by Signed-By in the target's deb822 source file.
Do not turn off APT authentication or use trusted=yes. Signing establishes
archive provenance, not ABI or runtime correctness.

Bootstrap apt, its target dependency closure and its signature verifier normally.
The present diagnostic root has dpkg but is not an accepted apt-enabled Debian
root. Build/archive tools and HTTP serving run on lab servers, not the laptop.
Keep unsigned or failed build candidates outside the accepted archive, with
fresh iteration directories and immutable source caches as before.

First publication acceptance: target apt update verifies our signature; apt
resolves and installs a package with a real dependency and maintainer script;
upgrade/configuration/trigger state survives image assembly; both machine
configurations use the same accepted userspace. Publish only redistributable
sources/binaries; AmigaOS ISOs, Enhancer media and credentials do not belong in
the archive. This plan does not create DNS, servers, signing keys or accounts.

References:
https://manpages.debian.org/trixie/reprepro/reprepro.1.en.html
https://wiki.debian.org/DebianRepository/SetupWithReprepro
https://manpages.debian.org/trixie/apt/apt-secure.8.en.html

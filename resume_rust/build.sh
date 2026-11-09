#!/bin/sh
# Build the release binary and copy it to the tracked `bin/` directory so it
# can be committed and deployed to hosts without a Rust toolchain.
set -eu

cd "$(dirname "$0")"

cargo build --release

mkdir -p bin
cp target/release/resume bin/resume
echo "wrote $(pwd)/bin/resume"

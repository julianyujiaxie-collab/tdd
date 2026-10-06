#!/usr/bin/env bash

test_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd) || exit 1
project_dir=$(cd "$test_dir/../.." && pwd) || exit 1

if [ ! -f "$test_dir/ssshtest" ]; then
    curl --fail --location --silent --show-error \
        https://raw.githubusercontent.com/ryanlayer/ssshtest/master/ssshtest \
        --output "$test_dir/ssshtest" || exit 1
fi

work_dir=$(mktemp -d "${TMPDIR:-/tmp}/scatter-test.XXXXXX") || exit 1
. "$test_dir/ssshtest"
STOP_ON_FAIL=1

tear_down() {
    rm -rf "$work_dir"
}

data_file="$work_dir/points.txt"
file_name="$work_dir/scatter.png"
cat > "$data_file" <<'EOF'
1 2
2 4
3 5
EOF

run test_scatter_creates_image \
    env MPLCONFIGDIR="$work_dir/matplotlib" "${PYTHON:-python3}" \
    "$project_dir/src/scatter.py" "$data_file" "$file_name" \
    "Test scatter plot" "X" "Y"
assert_exit_code 0
if [ "${test_scatter_creates_image:-}" = 1 ]; then
    assert_equal "$file_name" "$( ls "$file_name" )"
fi

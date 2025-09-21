# tests/test_interactive.py

import os

from tests.conftest import KEY_DOWN, KEY_ENTER


def test_interactive_menu(cli_runner):
    # Create a dummy interactive app for testing
    app_code = r"""
import sys

menu_items = ["Menu Item 1", "Menu Item 2", "Menu Item 3"]
selected_item = 0

def print_menu():
    for i, item in enumerate(menu_items):
        if i == selected_item:
            sys.stdout.write('> {}\n'.format(item))
        else:
            sys.stdout.write('  {}\n'.format(item))
    sys.stdout.flush()

print_menu()

while True:
    key = sys.stdin.read(1)
    if key == '\x1b':  # ANSI escape sequence
        key += sys.stdin.read(2)

    if key == '\n':  # Enter key
        sys.stdout.write(
            'You selected {}\n'.format(menu_items[selected_item])
        )
        sys.stdout.flush()
        break
    elif key == '\x1b[A':  # Up arrow
        selected_item = (selected_item - 1) % len(menu_items)
    elif key == '\x1b[B':  # Down arrow
        selected_item = (selected_item + 1) % len(menu_items)

    # Clear previous menu and print new one
    sys.stdout.write('\033[F' * (len(menu_items) + 1)) # Move cursor up
    sys.stdout.write('\033[J') # Clear from cursor to end of screen
    print_menu()
"""

    # Write the dummy app to a temporary file
    with open("my_interactive_app.py", "w") as f:
        f.write(app_code)

    session = cli_runner.run_interactive_command(
        ["python", "my_interactive_app.py"]
    )

    assert session.expect("> Menu Item 1")
    session.send_key(KEY_DOWN)
    assert session.expect("Menu Item 2")
    session.send_key(KEY_ENTER)
    assert session.expect("You selected Menu Item 2")

    session.close()

    # Clean up the dummy app
    os.remove("my_interactive_app.py")

# MC-Tools

### Python only
### 5.0b11 or above

### `close()`
- Close the currently open screen without sending a packet to the server.
- Ie, using this to close a screen will make the server think you still have it opened.

### `packet_close()`
- Close the currently open screen on the server side.
- Ie, using this to close a screen, will make the server think you closed it, but its still open on your client side.

### `save_screen() -> screen object`
-  Save a screen, to restore later with `restore_screen`
### `restore_screen()`
- Restore a static screen on the client, using a saved screen from `save_screen`

### `packet_use(x,y,z,direction="up",hand="main")`
- Do a right click on a block on the server side
- x, y, z all floats / integers
- direction: up/down or NESW as string (example: "north") (OPTIONAL, DEFAULTS TO "up")
- hand: "main" for main hand, "off" for off hand (OPTIONAL, DEFAULTS TO "main")

### `packet_mine(x,y,z,direction="up",hand="main")`
- Mine a block on the server side (not instant!)
- x, y, z all floats / integers
- direction: up/down or NESW as string (example: "north") (OPTIONAL, DEFAULTS TO "up")
- hand: "main" for main hand, "off" for off hand (OPTIONAL, DEFAULTS TO "main")

### `flip_esp()`
- WIP DO NOT USE

### `crash()`
- Performs a graceful crash (saves game before crashing)

### `terminate()`
- Kills the JVM instantly
- Doesnt save anything
- Here be dragons! Can corrupt worlds

### `disconnect()`
- Gracefully disconnects you
- Same as if you were to exit using the pause menu
- Works in single player

### `terminate_connection()`
- Severs the TCP connection to the server
- Only leaves on the server (will be timed out)
- Client never gets kicked

### `hide_chat()`
- Hide the chat
- Excludes the input bar

### `show_chat()`
- Show chat
- Excludes the input bar

### `buffer(func, arg)`
- Buffer up a lot of function calls
- `func` a callable
- `args` all arguments as a tuple (or other iterable)

### `flush_buffer()`
- Execute all function calls buffered up

### `clear_buffer()`
- Deletes all buffered function calls

### `get_tick_time() -> float`
- Returns a really good estimate on the servers tick time (the time between 2 tick)

### `get_tps() -> float`
- Returns a really good estimate of the servers TPS (ticks per second)

### `start_tick_monitor_and_wait()`
- Starts the tick monitor, and waits for values to flow in. Ususally this isnt needed, since starting up this script also starts the monitor.
- In case you accidentally killed the monitor, this is the function to restart it. Otherwise it should never be used

Usage:
```py
from ui_utils import *
# * wont cause any name missmatch
```
Note: You can run a function, without having to make a burner script, by appending the function name, and argument when starting the script

Example:
```
\mc_tools packet_mine 0 0 0
# Executes:
# packet_mine(0,0,0)
```

## MORE TO COME IN THE FUTURE
last updated on 09/03/2026

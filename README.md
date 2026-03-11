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

### `restore_screen(screen)`
- Restore a static screen on the client, using a saved screen from `save_screen`

### `packet_use(x,y,z,direction="up",hand="main")`
- Do a right click on a block on the server side
- `x, y, z`: all floats / integers
- `direction`: up/down or NESW as string (example: "north") (OPTIONAL, DEFAULTS TO "up")
- `hand`: "main" for main hand, "off" for off hand (OPTIONAL, DEFAULTS TO "main")

### `packet_mine(x,y,z,direction="up",hand="main")`
- Mine a block on the server side (not instant!)
- `x, y, z`: all floats / integers
- `direction`: up/down or NESW as string (example: "north") (OPTIONAL, DEFAULTS TO "up")
- `hand`: "main" for main hand, "off" for off hand (OPTIONAL, DEFAULTS TO "main")

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
- `func`: a callable
- `args`: all arguments as a tuple (or other iterable)

### `flush_buffer(leave=False)`
- Execute all function calls buffered up
- `Leave`: if true, disconnect after flush

### `flush_buffer_in_pyjinn(imports=(),leave=False)`
- Execute all function calls buffered up
- Runs in pyjinn, usually finishes in the same tick
- `Leave`: if true, disconnect after flush
- `imports`: An iterable, of imports (`"import minescript"`). Needed if the functions in the buffer are not declared in pyjinn already

### `clear_buffer()`
- Deletes all buffered function calls

### `get_tick_time() -> float`
- Returns a really good estimate on the servers tick time (the time between two ticks)

### `get_tps() -> float`
- Returns a really good estimate of the servers TPS (ticks per second)

### `time_since_last_tick()`
- The estimated time since the last server update
- Normal times are ~1 second, at 20 tps

### `start_tick_monitor_and_wait()`
- Starts the tick monitor, and waits for values to flow in. Ususally this isnt needed, since starting up this script also starts the monitor.
- In case you accidentally killed the monitor, this is the function to restart it. Otherwise it should never be used

### `delay(func,args,by,threaded=True,server=True)`
- Delays a function call
- `func`: a callable
- `args`: all arguments as a tuple (or other iterable)
- `by`: the delay in server ticks
- `threaded`: If True, the delay will happen on a new thread
- `server`: If true, delay ticks will be in line with the servers ticks

### `swap_to_hotbar(inv_slot,hotbar_slot)`
- Reimplements the functionality of `player_inventory_slot_to_hotbar()`
- `inv_slot`: 9-35
- `hotbar_slot`: 0-8

### `execute_and_leave(command)`
- Executes a command, and leaves in the same tick
- `command`: the executed command

## Usage:
```py
from mc_tools import *
```
Note: You can run a function, without having to make a burner script, by appending the function name, and argument when starting the script

Example:
```
\mc_tools packet_mine(0,0,0)
# Executes:
# packet_mine(0,0,0)
# mc_tools is auto imported (*)
```

## MORE TO COME IN THE FUTURE
last updated on 11/03/2026

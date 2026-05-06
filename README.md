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

### `packet_use(x:int, y:int, z:int, direction:str="up", hand:str="main")`
- Do a right click on a block on the server side
- `x, y, z`: all integers
- `direction`: up/down or NESW as string (example: "north") (OPTIONAL, DEFAULTS TO "up")
- `hand`: "main" for main hand, "off" for off hand (OPTIONAL, DEFAULTS TO "main")

### `packet_mine(x:int, y:int, z:int, direction:str="up", hand:str="main")`
- Mine a block on the server side (not instant!)
- `x, y, z`: all integers
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

### `buffer(func:callable, args:tuple)`
- Buffer up a lot of function calls
- `func`: a callable
- `args`: all arguments as a tuple (or other iterable)

### `flush_buffer(leave:bool=False)`
- Execute all function calls buffered up
- `Leave`: if true, disconnect after flush

### `flush_buffer_in_pyjinn(imports:tuple=(), leave:bool=False)`
- Execute all function calls buffered up
- Runs in pyjinn, usually finishes on the same frame
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

### `delay(func:callable, args:tuple, by:int, threaded:bool=True, server:bool=True)`
- Delays a function call
- `func`: a callable
- `args`: all arguments as a tuple (or other iterable)
- `by`: the delay in server ticks
- `threaded`: If True, the delay will happen on a new thread
- `server`: If true, delay ticks will be in line with the servers ticks

### `swap_to_hotbar(inv_slot:int, hotbar_slot:int)`
- Reimplements the functionality of `player_inventory_slot_to_hotbar()`
- `inv_slot`: 9-35
- `hotbar_slot`: 0-8

### `execute_and_leave(command:str)`
- Executes a command, and leaves in the same tick
- `command`: the executed command

### `remove_server_rescource_pack()`
- Removes forced server rescource packs

### `steal(filter:str=None)`
- Steal all items from the currently open container
- Can be filtered for namespaced:id-s (None for no filter)

### `dump(filter:str=None)`
- Dump all items from your inventory, to the currently open container
- Can be filtered for namespaced:id-s (None for no filter)

### `unlock_mouse()`
- Unlock the mouse, allowing it to be moved freely
- Note: this will close the currently open gui on the client side

### `lock_mouse()`
- Lock the mouse, allowing the camera to be rotated (Other guis may still unlock the mouse)
- Note: this will close any open guis, if it was called while the mouse was unlocked

### `get_minescript_version_index()`
- Returns the version index of minescript

### `set_global_variable(key:str,dat:any)`
- Set a global variable
- Global variables can be accessed by any process (even pyjinn), and persist until a restart of the game

### `get_global_variable(key:str)`
- Get a global variable
- Global variables can be accessed by any process (even pyjinn), and persist until a restart of the game

## Usage:
```py
import mc_tools as mt
```
Note: You can run a function, without having to make a burner script, by appending the function name, and argument when starting the script

Example:
```
\mc_tools packet_use(0,0,0)\ndump()
# Executes:
packet_use(0,0,0)
dump()
# mc_tools is auto imported (*)
```
To use quotes (`"` and `'`) use `/$` and `\$` (respectively)

## MORE TO COME IN THE FUTURE
last updated on 06/05/2026

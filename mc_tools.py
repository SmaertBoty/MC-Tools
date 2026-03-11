import sys
if "Pyjinn" in sys.version: sys.exit("Not pyjinnable")

from system.lib.minescript import execute, job_info, version_info, log, tick_loop

version = version_info().minescript
ver = ""
for char in version:
    try: ver += str(int(char))
    except: pass

if int(ver) < 5011: sys.exit("Please update to 5.0b11")

from system.lib.java import JavaClass
from time import perf_counter, sleep
from pathlib import Path
from threading import Thread, Lock

Minecraft = JavaClass("net.minecraft.client.Minecraft")
mc = Minecraft.getInstance()

chat_scale = mc.options.chatScale().get()
chat_scale = 1.0 if chat_scale == 0 else chat_scale
buffer_list = []
tick_time = -1
session = 0
_time_since_last_tick = 0
lock = Lock()

path = Path(__file__).parent.resolve() / "tick_time.txt"

def _log(s):
    log(f"[MCT] {s}")

def exec(code):
    if not code.startswith("\n"):
        code = "\n" + code
    if not code.endswith("\n"):
        code += "\n"
    code = code.replace("    ","").replace("\n","' '")[2:-2]
    execute(fr"\eval {code}")

def close():
    """
    Close the currently open screen without sending a packet to the server.
    Ie, using this to close a screen will make the server think you still have it opened.
    """
    mc.setScreen(None)

def packet_close():
    """
    Close the currently open screen on the server side.
    Ie, using this to close a screen, will make the server think you closed it, but its still open on your client side.
    """
    exec(r"""
    Minecraft = JavaClass("net.minecraft.client.Minecraft")
    mc = Minecraft.getInstance()
    ServerboundContainerClosePacket = JavaClass("net.minecraft.network.protocol.game.ServerboundContainerClosePacket")
    mc.getConnection().send(ServerboundContainerClosePacket(mc.player.containerMenu.containerId))
    """)

def save_screen():
    """
    Save a screen, to restore later.
    """
    return mc.screen

def restore_screen(screen):
    """
    Restore a screen on the client, using a saved screen.
    """
    mc.setScreen(screen)


def packet_use(x,y,z,direction="up",hand="main"):
    """"
    Do a right click on a block on the server side.
    """
    exec(fr"""
    BlockPos = JavaClass("net.minecraft.core.BlockPos")
    Minecraft = JavaClass("net.minecraft.client.Minecraft")
    mc = Minecraft.getInstance()
    ServerboundPlayerActionPacket = JavaClass("net.minecraft.network.protocol.game.ServerboundPlayerActionPacket")
    dir = JavaClass("net.minecraft.core.Direction")
    InteractionHand = JavaClass("net.minecraft.world.InteractionHand")
    x = {x}
    y = {y}
    z = {z}
    direction = "{direction}"
    hand = "{hand}"
    pos = BlockPos(x,y,z)
    if direction.lower().strip() == "up": direction = dir.UP
    elif direction.lower().strip() == "down": direction = dir.DOWN
    elif direction.lower().strip() == "north": direction = dir.NORTH
    elif direction.lower().strip() == "east": direction = dir.EAST
    elif direction.lower().strip() == "south": direction = dir.SOUTH
    elif direction.lower().strip() == "west": direction = dir.WEST
    if hand.lower().strip() == "main": hand = InteractionHand.MAIN_HAND
    elif hand.lower().strip() == "off": hand = InteractionHand.SECONDARY_HAND
    hit = HitResult(Vec3(pos.getX(), pos.getY(), pos.getZ()), direction, pos, False)
    mc.getConnection().send(ServerboundUseItemOnPacket(hand, hit, 0))
    """)

def packet_mine(x,y,z,direction="up",hand="main"):
    """"
    Mine a block, on the server side.
    """
    exec(fr"""
    BlockPos = JavaClass("net.minecraft.core.BlockPos")
    Minecraft = JavaClass("net.minecraft.client.Minecraft")
    mc = Minecraft.getInstance()
    ServerboundPlayerActionPacket = JavaClass("net.minecraft.network.protocol.game.ServerboundPlayerActionPacket")
    ServerboundSwingPacket = JavaClass("net.minecraft.network.protocol.game.ServerboundSwingPacket")
    dir = JavaClass("net.minecraft.core.Direction")
    InteractionHand = JavaClass("net.minecraft.world.InteractionHand")
    x = {x}
    y = {y}
    z = {z}
    direction = "{direction}"
    hand = "{hand}"
    pos = BlockPos(x,y,z)
    if direction.lower().strip() == "up": direction = dir.UP
    elif direction.lower().strip() == "down": direction = dir.DOWN
    elif direction.lower().strip() == "north": direction = dir.NORTH
    elif direction.lower().strip() == "east": direction = dir.EAST
    elif direction.lower().strip() == "south": direction = dir.SOUTH
    elif direction.lower().strip() == "west": direction = dir.WEST
    if hand.lower().strip() == "main": hand = InteractionHand.MAIN_HAND
    elif hand.lower().strip() == "off": hand = InteractionHand.SECONDARY_HAND
    mc.getConnection().send(ServerboundPlayerActionPacket(ServerboundPlayerActionPacket.Action.START_DESTROY_BLOCK, pos, direction))
    mc.getConnection().send(ServerboundSwingPacket(hand))
    mc.getConnection().send(ServerboundPlayerActionPacket(ServerboundPlayerActionPacket.Action.STOP_DESTROY_BLOCK, pos, direction))
    """)

def flip_esp():
    global esp
    if esp:
        esp = False
        for job in job_info():
            if len(job.command) > 1:
                if job.command[1] == "#ESPRENDERER":
                    execute(fr"\killjob {job.job_id}")
    else:
        esp = True
        exec(fr"""
        #ESPRENDERER
        Minecraft = JavaClass("net.minecraft.client.Minecraft")
        BlockPos = JavaClass("net.minecraft.core.BlockPos")
        Gizmos = JavaClass("net.minecraft.gizmos.Gizmos")
        GizmoStyle = JavaClass("net.minecraft.gizmos.GizmoStyle")
        TextGizmo_Style = JavaClass("net.minecraft.gizmos.TextGizmo$Style")
        Vec3 = JavaClass("net.minecraft.world.phys.Vec3")
        ARGB = JavaClass("net.minecraft.util.ARGB")

        def _on_render(event):
         block_pos = BlockPos(0,-60,0)
         color = ARGB.color(255,255,10,100)
         Gizmos.cuboid(block_pos, GizmoStyle.stroke(color)).setAlwaysOnTop()

        add_event_listener("render", _on_render)
        """)

def terminate():
    """
    Shut down the entire JVM in an instant.
    Here be dragons! Can corrupt worlds.
    """
    exec(r"""
    Runtime = JavaClass("java.lang.Runtime")
    Runtime.getRuntime().halt(1)
    """)

def crash():
    """
    Same as if you were to normally crash, or by holding down F3+C
    """
    exec(r"""
    System = JavaClass("java.lang.System")
    System.exit(1)
    """)

def disconnect():
    """
    "Gracefully" disconnect from the server. Same as exiting from the pause menu
    """
    exec(r"""
    Minecraft = JavaClass("net.minecraft.client.Minecraft")
    mc = Minecraft.getInstance()
    Component = JavaClass("net.minecraft.network.chat.Component")
    mc.player.connection.getConnection().disconnect(Component.translatable("multiplayer.disconnect.generic"))
    """)

def terminate_connection():
    """
    Leave only on the server side, by crashing the TCP channel.
    """
    mc.getConnection().close()

def hide_chat():
    """
    Hide the chat
    """
    mc.options.chatScale().set(0.0)

def show_chat():
    """
    Show the chat
    """
    mc.options.chatScale().set(chat_scale)

def buffer(func,args:tuple):
    """
    Buffer up function calls
    """
    global buffer_list
    buffer_list.append((func,args))

def flush_buffer():
    """
    Send all function calls in the buffer, all at once
    """
    for func, args in buffer_list:
        func(*args)

def clear_buffer():
    """
    Clears out all buffered function calls
    """
    global buffer_list
    buffer_list.clear()

def _monitor_tps():
    for job in job_info():
        if len(job.command) > 1:
            if job.command[1] == "#TICKTIMESCRIPT":
                _log("Joining already existing tick monitor...")
                return True
    exec(fr"""
    #TICKTIMESCRIPT
    # An MC-Tools script. DO NOT KILL
    ClientboundSetTimePacket = JavaClass("net.minecraft.network.protocol.game.ClientboundSetTimePacket")
    System = JavaClass("java.lang.System")
    Math = JavaClass("java.lang.Math")
    prev = System.currentTimeMillis()
    BufferedWriter = JavaClass("java.io.BufferedWriter")
    FileWriter = JavaClass("java.io.FileWriter")
    path = System.getProperty("user.dir") + "\\minescript\\tick_time.txt"
    chain = 0

    def save(data):
     global chain
     chain = chain % 9
     chain += 1
     writer = BufferedWriter(FileWriter(path, False))
     writer.write(str(chain) + str(data))
     writer.flush()
     writer.close()

    def on_clientbound_packet(event):
     global prev
     if isinstance(event.packet, ClientboundSetTimePacket):
      now = System.currentTimeMillis()
      tick_time = (now - prev) / 20000
      try: save(tick_time)
      except: pass
      prev = now


    add_event_listener("clientbound_packet", on_clientbound_packet)
    """)
    def monitor():
        global tick_time
        global session
        global _time_since_last_tick
        last_session = session
        last_session_time = perf_counter()
        while True:
            with lock:
                with open(path,"r") as f:
                    try: 
                        extracted = str(f.read())
                        tick_time = float(extracted[1:])
                        session = int(extracted[0])
                    except: pass
                if session != last_session:
                    last_session = session
                    last_session_time = perf_counter()
                _time_since_last_tick = perf_counter() - last_session_time
    Thread(target=monitor,daemon=True).start()
_monitor_tps()

def get_tick_time():
    """
    A really strong estimate on the tick time
    """
    return tick_time

def get_tps():
    """
    A really strong estimate on the tps
    """
    return 1/tick_time

def time_since_last_tick():
    """
    The estimated time since the last tick
    """
    return _time_since_last_tick

def start_tick_monitor_and_wait():
    """
    Starts the tick monitor, and waits for values to flow in. Ususally this isnt needed, since starting up this script also starts the monitor.
    In case you accidentally killed the monitor, this is the function to restart it.
    """
    if _monitor_tps():
        sleep(1)

def delay(func,args:tuple,by:int,threaded:bool=True):
    """
    Delay a function call by a given amount of server ticks
    """
    def _delay():
        index = 0
        while True:
            if index >= by:
                func(*args)
            index += 1
            sleep(get_tick_time())
    if threaded:
        Thread(target=_delay,daemon=True).start()
    else:
        _delay()

def swap_to_hotbar(inv_slot:int=0,hotbar_slot:int=0):
    """
    Reimplements the functionality of player_inventory_slot_to_hotbar
    """
    exec(fr"""
    ClickType = JavaClass("net.minecraft.world.inventory.ClickType")
    BlockPos = JavaClass("net.minecraft.core.BlockPos")
    Minecraft = JavaClass("net.minecraft.client.Minecraft")
    mc = Minecraft.getInstance()
    mc.gameMode.handleInventoryMouseClick(mc.player.containerMenu.containerId, {hotbar_slot}, {inv_slot}, ClickType.SWAP, mc.player)
    mc.gameMode.handleInventoryMouseClick(mc.player.containerMenu.containerId, {inv_slot}, {hotbar_slot}, ClickType.SWAP, mc.player)
    """)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        globals().get(args[0])(*args[1:])
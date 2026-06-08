import sys
if "Pyjinn" in sys.version: sys.exit("Not pyjinnable")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        args = " ".join(sys.argv[1:]).replace(r"\n","\n").replace(r"\$","'").replace("/$",'"')
        exec(f"""from minescript import EventQueue\nEventQueue().register_world_listener()\nfrom mc_tools import *\n{args}""")
        sys.exit(1)

from system.lib.minescript import execute, job_info, version_info, log

version = version_info().minescript
ver = ""
for char in version:
    try: ver += str(int(char))
    except: pass

if int(ver) < 5011: sys.exit("Please update to 5.0b11")

from system.lib.java import eval_pyjinn_script as _eps, JavaClass
from time import perf_counter, sleep
from pathlib import Path
from threading import Thread, Lock
import os
from typing import Any

mc = JavaClass("net.minecraft.client.Minecraft").getInstance()

chat_scale = mc.options.chatScale().get()
chat_scale = 1.0 if chat_scale == 0 else chat_scale
buffer_list = []
tick_time = -1
session = 0
_time_since_last_tick = 0
lock = Lock()
cmd_history = Path(os.getcwd()).resolve() / "command_history.txt"

path = Path(__file__).parent.resolve() / "tick_time.txt"

def _log(s):
    log(f"[MCT] {s}")

def _raise(type,msg):
    raise eval(type)(msg)

script = _eps(
r"""
if "mc_tools" not in __script__.vars["game"]:
    __script__.vars["game"]["mc_tools"] = {}

def sgv(key,dat):
    __script__.vars["game"]["mc_tools"][key] = dat

def ggv(key):
    return __script__.vars["game"]["mc_tools"][key]
""")

sgv = script.get("sgv")
ggv = script.get("ggv")

def get_minescript_version_index() -> int:
    """
    Returns the version index of minescript
    """
    return int(ver)

def set_global_variable(key:str,dat:Any):
    """
    Set a global variable
    Global variables can be accessed by any process, and persist until a restart
    """
    sgv(key,dat)

def get_global_variable(key:str) -> Any:
    """
    Get a global variable
    Global variables can be accessed by any process, and persist until a restart
    """
    return ggv(key)

def eps(code:str):
    """
    Executes some pyjinn code
    Non blocking and very fast, but you cannot have returns
    Also code cannot contain >'< (single quote)
    """
    if not code.startswith("\n"):
        code = "\n" + code
    if not code.endswith("\n"):
        code += "\n"
    code = code.replace("\n","' '")[2:-2]
    execute(fr"\eval {code}")

def close():
    """
    Close the currently open screen without sending a packet to the server.
    Ie, using this to close a screen will make the server think you still have it opened.
    """
    eps(
r"""
mc = JavaClass("net.minecraft.client.Minecraft").getInstance()
mc.setScreen(None)
""")

def packet_close():
    """
    Close the currently open screen on the server side.
    Ie, using this to close a screen, will make the server think you closed it, but its still open on your client side.
    """
    eps(
r"""
mc = JavaClass("net.minecraft.client.Minecraft").getInstance()
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
    eps(
fr"""
BlockPos = JavaClass("net.minecraft.core.BlockPos")
mc = JavaClass("net.minecraft.client.Minecraft").getInstance()
ServerboundUseItemOnPacket = JavaClass("net.minecraft.network.protocol.game.ServerboundUseItemOnPacket")
ServerboundSwingPacket = JavaClass("net.minecraft.network.protocol.game.ServerboundSwingPacket")
dir = JavaClass("net.minecraft.core.Direction")
InteractionHand = JavaClass("net.minecraft.world.InteractionHand")
HitResult = JavaClass("net.minecraft.world.phys.BlockHitResult")
Vec3 = JavaClass("net.minecraft.world.phys.Vec3")
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
mc.getConnection().send(ServerboundSwingPacket(hand))
""")

def packet_mine(x,y,z,direction="up",hand="main"):
    """"
    Mine a block, on the server side.
    """
    eps(
fr"""
BlockPos = JavaClass("net.minecraft.core.BlockPos")
mc = JavaClass("net.minecraft.client.Minecraft").getInstance()
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

def terminate():
    """
    Shut down the entire JVM in an instant.
    Here be dragons! Can corrupt worlds.
    """
    eps(
r"""
Runtime = JavaClass("java.lang.Runtime")
Runtime.getRuntime().halt(1)
""")

def crash(reason:str="Intentional crash"):
    """
    Same as if you were to normally crash, or by holding down F3+C
    """
    eps(
fr"""
mc = JavaClass("net.minecraft.client.Minecraft").getInstance()
Throwable = JavaClass("java.lang.Throwable")
CrashReport = JavaClass("net.minecraft.CrashReport")
def crash():
    mc.delayCrash(CrashReport("Controlled crash from MC-Tools",Throwable("{reason}")))
    mc.handleDelayedCrash()
mc.execute(ManagedCallback(crash))
""")

def disconnect():
    """
    "Gracefully" disconnect from the server. Same as exiting from the pause menu
    """
    eps(
r"""
mc = JavaClass("net.minecraft.client.Minecraft").getInstance()
Component = JavaClass("net.minecraft.network.chat.Component")
mc.player.connection.getConnection().disconnect(Component.translatable("multiplayer.disconnect.generic"))
""")

def terminate_connection():
    """
    Leave only on the server side, by crashing the TCP channel.
    """
    eps(
r"""
mc = JavaClass("net.minecraft.client.Minecraft").getInstance()
mc.getConnection().close()
""")

def hide_chat():
    """
    Hide the chat
    """
    eps(
r"""
mc = JavaClass("net.minecraft.client.Minecraft").getInstance()
mc.options.chatScale().set(0.0)
""")

def show_chat(scale=None):
    """
    Show the chat
    """
    eps(
fr"""
mc = JavaClass("net.minecraft.client.Minecraft").getInstance()
mc.options.chatScale().set({chat_scale} if not {scale} else {scale})
""")

def buffer(func,args:tuple):
    """
    Buffer up function calls
    """
    buffer_list.append((func,args))

def flush_buffer(leave:bool=False) -> list:
    """
    Send all function calls in the buffer, all at once
    """
    out = [func(*args) for func, args in buffer_list]
    if leave: disconnect()
    return out

def flush_buffer_in_pyjinn(imports:tuple=(),leave:bool=False):
    """
    Send all function calls in the buffer, all at once (ran in pyjinn, finishes in the same frame)
    """
    code = "\n".join(imports) + "\n" + """mc = JavaClass("net.minecraft.client.Minecraft").getInstance()\nComponent = JavaClass("net.minecraft.network.chat.Component")\nmc.getConnection().close()\n""" if leave else ""
    for func, args in buffer_list:
        try: func_name = func.__name__
        except: func_name = func.name
        out = []
        for arg in args:
            if isinstance(arg,str):
                out.append(f'"{arg}"')
            else:
                out.append(arg)
        args = out
        code += f"{func_name}({", ".join(args)})\n"
    code += """mc.player.connection.getConnection().disconnect(Component.translatable("multiplayer.disconnect.generic"))""" if leave else ""
    eps(fr"""
    {code}
    """)

def clear_buffer():
    """
    Clears out all buffered function calls
    """
    buffer_list.clear()

def _monitor_tps():
    def monitor():
        global tick_time
        global session
        global _time_since_last_tick
        last_session = session
        last_session_time = perf_counter()
        while True:
            with lock:
                try:
                    extracted = get_global_variable("ticktimedata")
                    if extracted:
                        tick_time = float(extracted[1:])
                        session = int(extracted[0])
                    if session != last_session:
                        last_session = session
                        last_session_time = perf_counter()
                    _time_since_last_tick = perf_counter() - last_session_time
                except: pass
    
    Thread(target=monitor,daemon=True).start()
    for job in job_info():
        if len(job.command) > 1:
            if job.command[1] == "#TICKTIMESCRIPT":
                _log("Joining already existing tick monitor...")
                return True
    eps(
    fr"""
#TICKTIMESCRIPT
# An MC-Tools script. DO NOT KILL
ClientboundSetTimePacket = JavaClass("net.minecraft.network.protocol.game.ClientboundSetTimePacket")
System = JavaClass("java.lang.System")
Math = JavaClass("java.lang.Math")
prev = System.currentTimeMillis()
path = System.getProperty("user.dir") + "\\minescript\\tick_time.txt"
chain = 0
if "mc_tools" not in __script__.vars["game"]:
    __script__.vars["game"]["mc_tools"] = {"{"}{"}"}
def save(data):
    global chain
    chain = chain % 9
    chain += 1
    __script__.vars["game"]["mc_tools"]["ticktimedata"] = str(chain) + str(data)
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
_monitor_tps()

def get_tick_time() -> float:
    """
    A really strong estimate on the tick time
    """
    return tick_time

def get_tps() -> float:
    """
    A really strong estimate on the tps
    """
    return 1/tick_time

def time_since_last_tick() -> float:
    """
    The estimated time since the last tick
    """
    return _time_since_last_tick

def delay(func,args:tuple,by:int,threaded:bool=True,server:bool=True) -> Any:
    """
    Delay a function call by a given amount of ticks
    """
    def _delay():
        index = 0
        while True:
            if index >= by:
                return func(*args)
            index += 1
            sleep(get_tick_time() if server and get_tick_time() > 0 else 0.05)
    if threaded:
        Thread(target=_delay,daemon=True).start()
    else:
        _delay()

def swap_to_hotbar(inv_slot:int,hotbar_slot:int):
    """
    Reimplements the functionality of player_inventory_slot_to_hotbar
    """
    eps(
fr"""
ClickType = JavaClass("net.minecraft.world.inventory.ClickType")
mc = JavaClass("net.minecraft.client.Minecraft").getInstance()
mc.gameMode.handleInventoryMouseClick(mc.player.containerMenu.containerId, {hotbar_slot}, {inv_slot}, ClickType.SWAP, mc.player)
mc.gameMode.handleInventoryMouseClick(mc.player.containerMenu.containerId, {inv_slot}, {hotbar_slot}, ClickType.SWAP, mc.player)
""")

def execute_and_leave(command:str):
    """
    execute a command, and leave, on the same tick. 
    Simply using execute() then disconnect() may end up epsuting both of them 1 server tick apart
    """
    eps(
fr"""
mc = JavaClass("net.minecraft.client.Minecraft").getInstance()
Component = JavaClass("net.minecraft.network.chat.Component")
execute("{command}")
mc.player.connection.getConnection().disconnect(Component.translatable("multiplayer.disconnect.generic"))
""")

def remove_server_resource_pack():
    """
    Removes the server resource pack
    """
    eps(
r"""
mc = JavaClass("net.minecraft.client.Minecraft").getInstance()
mc.clearDownloadedResourcePacks()
""")

def steal(filter:str=None):
    """
    Steal all items from the currently open container.
    Can be filtered for namespaced:id-s
    """
    eps(
fr"""
mc = JavaClass("net.minecraft.client.Minecraft").getInstance()
ClickType = JavaClass("net.minecraft.world.inventory.ClickType")
for item in container_get_items():
    if item.item == "{filter}" or "{filter}" == "None":
        mc.gameMode.handleInventoryMouseClick(mc.player.containerMenu.containerId, item.slot, 1, ClickType.QUICK_MOVE, mc.player)
""")

def dump(filter:str=None):
    """
    Dump all items from your inventory, the currently open container.
    Can be filtered for namespaced:id-s
    """
    eps(
fr"""
mc = JavaClass("net.minecraft.client.Minecraft").getInstance()
ClickType = JavaClass("net.minecraft.world.inventory.ClickType")
size = mc.screen.getMenu().getItems().size()
extra = mc.screen.getMenu().getItems().size() - 36
for slot in range(extra, size):
    item = None
    for _item in container_get_items(): 
        if _item.slot == slot: 
            item = _item
    if item is None: continue
    if item.item == "{filter}" or "{filter}" == "None":
        mc.gameMode.handleInventoryMouseClick(mc.player.containerMenu.containerId, slot, 1, ClickType.QUICK_MOVE, mc.player)
""")

def _mouse_unlocker():
    for job in job_info():
        if len(job.command) > 1:
            if job.command[1] == "#MOUSEUNLOCKSCRIPT":
                _log("Joining already existing mouse unlocker...")
                return True
    eps(fr"""
#MOUSEUNLOCKSCRIPT
# An MC-Tools script. DO NOT KILL
mc = JavaClass("net.minecraft.client.Minecraft").getInstance()
HudRenderCallback = JavaClass("net.fabricmc.fabric.api.client.rendering.v1.HudRenderCallback")
ARGB = JavaClass("net.minecraft.util.ARGB")
Component = JavaClass("net.minecraft.network.chat.Component")
ContainerScreen = JavaClass("net.minecraft.client.gui.screens.inventory.ContainerScreen")
ChestMenu = JavaClass("net.minecraft.world.inventory.ChestMenu")
Inventory = JavaClass("net.minecraft.world.entity.player.Inventory")
EntityEquipment = JavaClass("net.minecraft.world.entity.EntityEquipment")
if "mc_tools" not in __script__.vars["game"]:
    __script__.vars["game"]["mc_tools"] = {"{"}{"}"}
__script__.vars["game"]["mc_tools"]["unlock_mouse"] = False
inv = Inventory(mc.player, EntityEquipment())
CustomScreen = ContainerScreen(ChestMenu.oneRow(0, inv), inv, Component.literal("Mouse Unlocked"))
first = False
def handle_render(ctx,delta):
    global first
    matrices = ctx.pose()
    if __script__.vars["game"]["mc_tools"]["unlock_mouse"]:
        if __script__.vars["game"]["mc_tools"]["unlock_mouse"] == "Block":
            mc.setScreen(CustomScreen)
            delta = delta.getRealtimeDeltaTicks()
            matrices.pushMatrix()
            matrices.translate(10000,10000)
        elif __script__.vars["game"]["mc_tools"]["unlock_mouse"] == "Non":
            mc.mouseHandler.releaseMouse()
        first = True
    else:
        if first:
            mc.player.closeContainer()
            mc.mouseHandler.grabMouse()
            first = False
        matrices.pushMatrix()
        matrices.translate(0,0)
HudRenderCallback.EVENT.register(HudRenderCallback(ManagedCallback(handle_render)))
""")
_mouse_unlocker()

def unlock_mouse(blocking:bool=True):
    """
    Unlock the mouse, allowing it to be moved freely
    If blocking is True, it will attempt to block interaction with the game
    """
    eps(
fr"""
x=0
__script__.vars["game"]["mc_tools"]["unlock_mouse"] = "{"Non" if not blocking else "Block"}"
""")

def lock_mouse():
    """
    Lock the mouse, allowing the camera to be rotated
    """
    eps(
r"""
x=0
__script__.vars["game"]["mc_tools"]["unlock_mouse"] = False
""")

def join_server(ip:str,delay:float=0.0):
    """
    Automatically exits the current server, and joins another
    Note: a positive delay will result in the game freezing for that long. Do not worry, it will not crash
    """
    eps(
fr"""
import sys
mc = JavaClass("net.minecraft.client.Minecraft").getInstance()
ServerAddress = JavaClass("net.minecraft.client.multiplayer.resolver.ServerAddress")
ServerData = JavaClass("net.minecraft.client.multiplayer.ServerData")
ConnectScreen = JavaClass("net.minecraft.client.gui.screens.ConnectScreen")
Component = JavaClass("net.minecraft.network.chat.Component")
TitleScreen = JavaClass("net.minecraft.client.gui.screens.TitleScreen")
JoinMultiplayerScreen = JavaClass("net.minecraft.client.gui.screens.multiplayer.JoinMultiplayerScreen")
Thread = JavaClass("java.lang.Thread")
def connect():
    if {delay} > 0:
        Thread.sleep(int({delay}*1000))
    ConnectScreen.startConnecting(
    JoinMultiplayerScreen(TitleScreen()),
    mc,
    ServerAddress.parseString("{ip}"),
    ServerData("Minecraft Server", "{ip}", ServerData.Type.OTHER),
    False,
    None)
    sys.exit(1)
def world(event):
    if event.connected: return
    mc.execute(ManagedCallback(connect))
add_event_listener("world",world)
mc.player.connection.getConnection().disconnect(Component.translatable("multiplayer.disconnect.generic"))
""")

def get_tablist() -> list:
    eps(
fr"""
mc = JavaClass("net.minecraft.client.Minecraft").getInstance()
plyrs = mc.getConnection().getListedOnlinePlayers()
out = []
for playerdat in plyrs:
    out.append([
        playerdat.getTabListDisplayName().getString(),
        playerdat.getLatency()
        ])
__script__.vars["game"]["mc_tools"]["tablist"] = out
""")
    sleep(0.01)
    return get_global_variable("tablist")

def freeze(_for:float):
    """
    Freezes the game for a set amount of time
    Same as R-clicikng the window border
    Note: Will pause any and all pyjinn processes for the duration of the freeze
    """
    eps(
fr"""
Thread = JavaClass("java.lang.Thread")
Thread.sleep({_for}*1000)
""")

def _block_packet_script():
    for job in job_info():
        if len(job.command) > 1:
            if job.command[1] == "#BLOCKPACKETSCRIPT":
                _log("Joining already existing packet blocker...")
                return True
    eps(
fr"""
#BLOCKPACKETSCRIPT
# An MC-Tools script. DO NOT KILL
mappings = JavaClass("net.minescript.common.Minescript").mappingsLoader.get()
if "blocked_packets" not in __script__.vars["game"]["mc_tools"]:
    __script__.vars["game"]["mc_tools"]["blocked_packets"] = []
def c2s(event):
    _class = str(event.packet.getClass())
    p = mappings.getPrettyClassName(_class.split(" ")[-1]).split(".")[-1]
    if p in __script__.vars["game"]["mc_tools"]["blocked_packets"]:
        event.cancel()
add_event_listener("serverbound_packet",c2s)
""")
_block_packet_script()

def block_packet(packet:str):
    """
    Intercepts a packet, so that it never reaches the server
    """
    eps(
fr"""
if "blocked_packets" not in __script__.vars["game"]["mc_tools"]:
    __script__.vars["game"]["mc_tools"]["blocked_packets"] = []
__script__.vars["game"]["mc_tools"]["blocked_packets"].append("{packet}")
""")

def unblock_packet(packet:str):
    """
    Stops intercepting a specific packet
    """
    eps(
fr"""
if "blocked_packets" not in __script__.vars["game"]["mc_tools"]:
    __script__.vars["game"]["mc_tools"]["blocked_packets"] = []
[__script__.vars["game"]["mc_tools"]["blocked_packets"].pop(i) for i in range(len(__script__.vars["game"]["mc_tools"]["blocked_packets"])) if __script__.vars["game"]["mc_tools"]["blocked_packets"][i] == "{packet}"]
""")

def get_fps() -> int:
    """
    Returns the current fps of the game
    """
    return mc.getFps()

def show_toast(title:str,message:str):
    """
    Display a toast!
    """
    eps(
fr"""
mc = JavaClass("net.minecraft.client.Minecraft").getInstance()
Component = JavaClass("net.minecraft.network.chat.Component")
ToastManager = JavaClass("net.minecraft.client.gui.components.toasts.ToastManager")
SystemToast = JavaClass("net.minecraft.client.gui.components.toasts.SystemToast")
mc.getToastManager().addToast(SystemToast.multiline(mc, SystemToast.SystemToastId.PERIODIC_NOTIFICATION, Component.literal("{title}"), Component.literal("{message}")))
""")

def batch_java_calls(*code:str):
    """
    Batch up many java calls into one
    """
    raise NotImplementedError("batch_java_calls")
    pass

import re
from typing import List, Union


def custom_log_parser(customs, log: str) -> Union[List[str], None]:
    LIST: List[str] = []
    for k in customs:
        if customs[k] in log:
            LIST.append(k)
    if LIST:
        return LIST
    return None


def multimc_in_program_files(log: str) -> Union[str, None]:
    TRIGGER: str = "Minecraft folder is:\nC:/Program Files"
    if TRIGGER in log:
        return "‼ Your MultiMC installation is in Program Files, where MultiMC doesn't have permission to write.\nYou should move it somewhere else, like your Desktop."
    return None


def server_java(log: str) -> Union[str, None]:
    TRIGGER: str = "-Bit Server VM warning"
    if TRIGGER in log:
        return "‼ You're using the server version of Java. [See here for help installing the correct version.](https://github.com/MultiMC/MultiMC5/wiki/Using-the-right-Java)"
    return None


def id_range_exceeded(log: str) -> Union[str, None]:
    TRIGGER: str = "java.lang.RuntimeException: Invalid id 4096 - maximum id range exceeded."
    if TRIGGER in log:
        return "‼ You've exceeded the hardcoded ID Limit. Remove some mods, or install [this one](https://www.curseforge.com/minecraft/mc-mods/notenoughids)"
    return None


def out_of_memory_error(log: str) -> Union[str, None]:
    TRIGGER: str = "java.lang.OutOfMemoryError"
    if TRIGGER in log:
        return "‼ You've run out of memory. You should allocate more, although the exact value depends on how many mods you have installed."
    return None


def shadermod_optifine_conflict(log: str) -> Union[str, None]:
    TRIGGER: str = "java.lang.RuntimeException: Shaders Mod detected. Please remove it, OptiFine has built-in support for shaders."
    if TRIGGER in log:
        return "‼ You've installed Shaders Mod alongside OptiFine. OptiFine has built-in shader support, so you should remove Shaders Mod"
    return None


def fabric_api_missing(log: str) -> Union[str, None]:
    EXEPTION: str = (
        "net.fabricmc.loader.discovery.ModResolutionException: Could not find required mod:"
    )
    FABRIC: str = "requires {fabric @"
    if EXEPTION in log and FABRIC in log:
        return "‼ You are missing Fabric API, which is required by a mod.\n[Download the needed version here](https://www.curseforge.com/minecraft/mc-mods/fabric-api)"
    return None


def multimc_in_onedrive_managed_folder(log: str) -> Union[str, None]:
    REGEX = re.compile(r"Minecraft folder is:\nC:/.+/.+/OneDrive")
    if REGEX.search(log):
        return "❗ MultiMC is located in a folder managed by OneDrive. OneDrive messes with Minecraft folders while the game is running, and this often leads to crashes.\nYou should move the MultiMC folder to a different folder."
    return None


def major_java_version_change(log: str) -> Union[str, None]:
    REGEX = re.compile(r"Java is version (1.)??(?P<ver>[6-9]|[1-9][0-9])+\..+,")
    if found := re.findall(REGEX, log):
        if int(list(found[0])[1]) == 8:
            return None
        return "❗ You're using Java {}. Versions other than Java 8 are not designed to be used with Minecraft and may cause issues. [See here for help installing the correct version.](https://github.com/MultiMC/MultiMC5/wiki/Using-the-right-Java)".format(
            list(found[0])[1]
        )
    return None


def pixel_format_not_accelerated_win10(log: str) -> Union[str, None]:
    LWJGL_EXCEPTION: str = "org.lwjgl.LWJGLException: Pixel format not accelerated"
    WIN10: str = "Operating System: Windows 10"
    if LWJGL_EXCEPTION in log and WIN10 in log:
        return "❗ You seem to be using an Intel GPU that is not supported on Windows 10.\nYou will need to install an older version of Java, [see here for help](https://github.com/MultiMC/MultiMC5/wiki/Unsupported-Intel-GPUs)"
    return None


def java_architecture(log: str) -> Union[str, None]:
    TRIGGER: str = "Your Java architecture is not matching your system architecture."
    if TRIGGER in log:
        return "❗ You're using 32-bit Java. [See here for help installing the correct version.](https://github.com/MultiMC/MultiMC5/wiki/Using-the-right-Java)"
    return None


def ram_amount(log: str) -> Union[str, None]:
    REGEX = re.compile(r"-Xmx(?P<amount>[0-9]+)m[,\]]")
    if found := re.findall(REGEX, log):
        amount = int(found[0]) / 1000.0
        if amount > 10.0:
            return "⚠ You have allocated {}GB of RAM to Minecraft. [This is too much and can cause lagspikes.](https://vazkii.net/#blog/ram-explanation)".format(
                amount
            )
        return None
    return None


PARSERS = [
    multimc_in_program_files,
    server_java,
    id_range_exceeded,
    out_of_memory_error,
    shadermod_optifine_conflict,
    fabric_api_missing,
    multimc_in_onedrive_managed_folder,
    major_java_version_change,
    pixel_format_not_accelerated_win10,
    java_architecture,
    ram_amount,
]


def parse_all(log: str) -> Union[List[str], None]:
    result: List[str] = []
    for parser in PARSERS:
        if msg := parser(log):
            result.append(msg)
    if result:
        return result
    return []

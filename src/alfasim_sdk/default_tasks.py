import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any
from typing import Union
from zipfile import ZipFile

from colorama import Fore
from colorama import Style
from hookman.hookman_generator import HookManGenerator
from invoke import Collection
from invoke import Exit
from invoke import Task
from invoke import task
from strictyaml.ruamel import YAML

sdk_ns = Collection()


def sdk_task(*args: object, **kwargs: object) -> Any:
    """
    Similar to the native @task decorator, but also registers
    the task in the global ``sdk`` namespace.
    """
    if len(args) == 1 and not kwargs:
        # Direct decoration:
        # @task
        # def cog(...)
        fn = args[0]
        assert callable(fn)
        t = task(fn)
        # error: Argument 1 to "add_task" of "Collection" has incompatible type "Callable[..., Any]"; expected "Task[Any]"  [arg-type]
        sdk_ns.add_task(t)  # type:ignore[arg-type]
        return t
    else:
        # Indirect decoration:
        # @ns_task(help="...")
        # def codegen(...):
        def inner(fn) -> Task:
            assert callable(fn)
            t = task(*args, **kwargs)(fn)
            sdk_ns.add_task(t)
            return t

        return inner


def print_message(
    message: str,
    color: Union[str, None] = None,
    bright: bool = True,
    endline: str = "\n",
) -> None:
    """
    Print a message to the standard output.

    :param message: The message to print.
    :param color: The ANSI color used to colorize the message (see `colorama.Fore`).
        When `None` the message is printed as is. Default to `None`.
    :param bright: Control if the output message is bright or dim. This value is ignored if
        `color is None`. Default to `True`.
    :param endline: The character printed after `message`. Default to "new line character".
    """
    if color is not None:
        style = Style.BRIGHT if bright else Style.DIM
        message = "{color}{style}{msg}{reset}".format(
            color=color, style=style, reset=Style.RESET_ALL, msg=message
        )

    # The subprocesses are going to write directly to stdout/stderr, so we need to flush to make
    # sure the output does not get out of order
    sys.stdout.flush()
    sys.stderr.flush()
    print(message, end=endline)
    sys.stdout.flush()
    sys.stderr.flush()


def get_msvc_cmake_generator(msvc_compiler: str) -> str:
    """
    Gets the correct MSVC compiler version and return the corresponding
    cmake generator.
    """
    cmake_generators = {
        "2022": "Visual Studio 17 2022",
        "2019": "Visual Studio 16 2019",
        "2017": "Visual Studio 15 2017 Win64",
    }
    return cmake_generators[msvc_compiler]


# =============================================================
# =========================  Tasks  ===========================
# =============================================================
@sdk_task(
    help={
        "cmake_extra_args": "Extra arguments that will be passed to cmake",
        "debug": "Compile in debug mode",
        "clean": "Remove previous build directory",
    }
)
def compile(ctx, cmake_extra_args="", debug=False, clean=False):
    """
    Compile the plugin and generate shared lib.

    The option ``cmake_extra_args`` gives you the ability to pass a
    list of parameters to the cmake command. The list must be a space
    separeted list, for example, "-DARIABLE1=TEST -DVARIABLE2=TEST2"
    Remember to use quotes to wrap the content being passed to this option.

    If the ``--debug`` flag is present, the build configuration will be
    changed from ``Release`` to ``Debug``. Also, if this flag is active,
    more information about the compilation process will be printed to
    the console

    If the ``--clean`` flag is present, the previous generated ``build`` folder
    is removed. This is useful because in the absence of the task, the compilation
    will use cmake's cache to speed up the compilation time.
    """

    # Set to the plugin root, where the tasks.py is located in the plugin structure
    plugin_dir = Path(ctx.config._project_prefix)

    artifacts_dir = plugin_dir / "artifacts"
    assets_dir = plugin_dir / "assets"
    build_dir = plugin_dir / "build"
    package_dir = plugin_dir / "package"

    plugin_id = plugin_dir.name

    cmake_args = []
    if sys.platform == "win32":
        shared_lib_name = f"{plugin_id}.dll"
        if sys.maxsize == 2**63 - 1:
            cmake_args += ["-A", "x64"]
    else:
        shared_lib_name = f"lib{plugin_id}.so"

    shared_lib_path = artifacts_dir / shared_lib_name

    if clean and build_dir.exists():
        shutil.rmtree(build_dir)

    if artifacts_dir.exists():
        shutil.rmtree(artifacts_dir)

    import alfasim_sdk

    sdk_include_dir = alfasim_sdk.get_alfasim_sdk_api_path()

    build_configuration = "Debug" if debug else "Release"
    print_message(
        f"Build configuration: {build_configuration}", color=Fore.YELLOW, bright=True
    )

    binary_directory_path = f"-B{str(build_dir)}"
    home_directory_path = f"-H{plugin_dir}"
    sdk_include_arg = f"-DSDK_INCLUDE_DIR={sdk_include_dir}"
    build_config_arg = f"-DCMAKE_BUILD_TYPE={build_configuration}"
    cmake_args += [
        binary_directory_path,
        home_directory_path,
        sdk_include_arg,
        build_config_arg,
    ]

    if cmake_extra_args:
        cmake_args += cmake_extra_args.split(sep=" ")

    if debug:
        print_message(f"cmake args = {cmake_args}", color=Fore.YELLOW, bright=True)

    cmake_cmd = shutil.which("cmake")
    subprocess.check_call([f"{cmake_cmd}"] + cmake_args)
    subprocess.check_call(
        [
            f"{cmake_cmd}",
            "--build",
            str(build_dir),
            "--config",
            build_configuration,
            "--target",
            "install",
        ],
    )

    assert (
        shared_lib_path.exists()
    ), "Compilation task failed, shared lib was not created"

    if package_dir.exists():
        shutil.rmtree(package_dir)

    shutil.copytree(src=assets_dir, dst=package_dir)
    shutil.copy2(src=shared_lib_path, dst=package_dir)


def _get_hook_specs_file_path() -> Path:
    import alfasim_sdk._internal.hook_specs

    return Path(alfasim_sdk._internal.hook_specs.__file__)


@sdk_task(
    help={
        "package-name": "Name of the package. If empty, the package-name will be assumed to be the pluginid",
        "dst": "A path to where the output package should be created.",
    }
)
def package_only(ctx, package_name="", dst=os.getcwd()):
    """
    Generate a `<package_name>.hmplugin` file with all the content from the directory
    assets and artifacts.

    By default, the package will be created inside the folder plugin_dir, however, it's possible
    to give another path filling the --dst argument.
    """

    # Set to the plugin root, where the tasks.py is located in the plugin structure
    plugin_dir = Path(ctx.config._project_prefix)
    dst = Path(dst)
    hook_specs_file_path = _get_hook_specs_file_path()
    hm = HookManGenerator(hook_spec_file_path=hook_specs_file_path)
    from alfasim_sdk._internal.constants import EXTRAS_REQUIRED_VERSION_KEY
    from alfasim_sdk._internal.alfasim_sdk_utils import (
        get_current_version,
        get_extras_default_required_version,
    )

    plugin_id = str(plugin_dir.name)
    if not package_name:
        package_name = plugin_id
    package_name_suffix = f"sdk-{get_current_version()}"
    extras_defaults = {
        EXTRAS_REQUIRED_VERSION_KEY: get_extras_default_required_version()
    }
    hm.generate_plugin_package(
        package_name,
        plugin_dir,
        dst,
        extras_defaults=extras_defaults,
        package_name_suffix=package_name_suffix,
    )


@sdk_task(
    help={
        "package-name": "Name of the package. If empty, the package-name will be assumed to be the plugin_id",
        "dst": "A path to where the output package should be created.",
        "debug": "Compile in debug mode",
        "clean": "Remove previous build directory",
        "cmake_extra_args": "Extra arguments that will be passed to cmake",
    }
)
def package(
    ctx, package_name="", dst=os.getcwd(), debug=False, clean=False, cmake_extra_args=""
):
    """
    Create a new `<package-name>.hmplugin` file containing all the necessary files.

    This command will first call `invoke compile` command to generate the shared library, and after that, the plugin
    package will be generated with all the content available from the directory assets and artifacts.

    The `package` command will assume that the plugin project is the directory that
    contains the ``tasks.py`` file and the generated file will be placed also in the current directory.
    """
    compile(ctx, debug=debug, clean=clean, cmake_extra_args=cmake_extra_args)
    package_only(ctx, package_name=package_name, dst=dst)


@sdk_task()
def update(ctx):
    """
    Update plugin files automatically generated by ALFAsim-SDK.

    It is important to update the automatically generated files from each plugin when
    a new version of ALFAsim-SDK is released. Otherwise compilation problems can occur.

    The files updated are: |br|
    - ´<plugin_folder>/src/hook_specs.h´ |br|
    """
    hook_specs_file_path = _get_hook_specs_file_path()
    hm = HookManGenerator(hook_spec_file_path=hook_specs_file_path)

    # Set to the plugin root, where the tasks.py is located in the plugin structure
    plugin_folder = Path(ctx.config._project_prefix)
    plugin_id = plugin_folder.name
    plugin_location = plugin_folder.parent

    # Delete previously generated file, if present
    generated_hook_file = plugin_folder / "src" / "hook_specs.h"
    if generated_hook_file.is_file():
        generated_hook_file.unlink()

    # Generate updated hook specs file
    hm.generate_hook_specs_header(plugin_id, plugin_location)
    if generated_hook_file.is_file():
        print_message(
            "Successfully updated alfasim-sdk's files", color=Fore.GREEN, bright=True
        )
    else:  # pragma: no cover (not reachable using mock)
        print_message(
            "Failed to update alfasim-sdk's files", color=Fore.RED, bright=True
        )
        raise Exit(message=None, code=1)  # `code != 0`


@sdk_task()
def install_plugin(ctx, install_dir=None):
    r"""
    Install a plugin to ``install_dir`` folder.

    If absent, the ``install_dir`` will be assumed to be ``$HOME/.alfasim_plugins`` on linux
    or ``USERPROFILE\.alfasim_plugins`` on windows.

    Note: remember to always set ``ALFASIM_PLUGINS_DIR` to ``install_dir`` if you are using
    a different path than the default.

    """
    from pathlib import Path

    # Set to the plugin root, where the tasks.py is located in the plugin structure
    plugin_folder = Path(ctx.config._project_prefix)
    plugin_id = plugin_folder.name

    try:
        hm_plugin_path = next(plugin_folder.glob("*.hmplugin"))
    except StopIteration:
        print_message(
            f"Could not find any '*.hmplugin' in {plugin_folder}.",
            color=Fore.RED,
            bright=True,
        )
        raise Exit(code=1)

    if not hm_plugin_path.is_file():
        print_message(
            f" Output file '{hm_plugin_path}' is not valid",
            color=Fore.RED,
            bright=True,
        )
        raise Exit(code=1)

    if install_dir is None:
        install_dir = Path("~/.alfasim_plugins").expanduser()
    else:
        install_dir = Path(install_dir)
    install_dir.mkdir(exist_ok=True, parents=True)

    # Unpacking hmplugin file
    print_message(
        f"Installing plugin {plugin_id} into {install_dir}",
        color=Fore.YELLOW,
        bright=True,
    )
    with ZipFile(hm_plugin_path) as plugin_file_zip:
        plugin_file_zip.extractall(os.path.join(install_dir, plugin_id))

    print_message(
        f"Successfully installed plugin {plugin_id} into {install_dir}",
        color=Fore.GREEN,
        bright=True,
    )


@sdk_task()
def uninstall_plugin(ctx, install_dir=None):
    r"""
    Remove plugin from install folder.

    If absent, the ``install_dir`` will be assumed to be ``$HOME/.alfasim_plugins`` on linux
    or ``USERPROFILE\.alfasim_plugins`` on windows.
    """

    # Set to the plugin root, where the tasks.py is located in the plugin structure
    plugin_folder = Path(ctx.config._project_prefix)
    plugin_id = plugin_folder.name

    if install_dir is None:
        install_dir = Path("~/.alfasim_plugins").expanduser()
    else:
        install_dir = Path(install_dir)
    assert install_dir.is_dir(), f"{install_dir} is not a valid installation directory"

    print_message(
        f"Removing installed plugin(s) from {install_dir}",
        color=Fore.YELLOW,
        bright=True,
    )
    plugins_dirs = [install_dir / plugin_id]

    for dir in plugins_dirs:
        if dir.name != ".trash" and dir.exists():
            print_message(f"Removing plugin {dir.name}", color=Fore.YELLOW, bright=True)
            shutil.rmtree(dir)

    print_message(
        f"Successfully removed plugin(s) from {install_dir}",
        color=Fore.GREEN,
        bright=True,
    )


@sdk_task()
def reinstall_plugin(ctx, package_name, install_dir=None):
    r"""
    Remove, package and install an specified plugin to install_dir

    If absent, the ``install_dir`` will be assumed to be ``$HOME/.alfasim_plugins`` on linux
    or ``USERPROFILE\.alfasim_plugins`` on windows.

    It does the following steps:
        1) Remove the specified plugin from $HOME/.alfasim_plugins
        2) Compile the specified plugin and generate package
        3) Install the specified plugin to $HOME/.alfasim_plugins
    """
    uninstall_plugin(ctx, install_dir=install_dir)
    package(ctx, package_name=package_name)
    install_plugin(ctx, install_dir=install_dir)


@sdk_task
def clean(ctx):
    """Remove all build folders and .hmplugin files from plugin root and children folders"""

    plugin_folder = Path(ctx.config._project_prefix)
    _remove_build_folders(plugin_folder)
    _remove_hmplugin_files(plugin_folder)


@sdk_task
def msvc(ctx):
    """Create a MSVC solution file for the plugin."""
    if sys.platform != "win32":
        print_message(
            "msvc task only available on windows environment",
            color=Fore.RED,
            bright=True,
        )
        exit(0)

    # Set to the plugin root, where the tasks.py is located in the plugin structure
    plugin_folder = Path(ctx.config._project_prefix)
    plugin_id = plugin_folder.name
    print_message(
        f"Generating Visual Studio solution for {plugin_id}...",
        color=Fore.BLUE,
        bright=True,
    )

    spec_file = plugin_folder / f"{plugin_id}.spec.yml"
    yaml = YAML(typ="safe")
    specs = yaml.load(spec_file)
    build_generator = get_msvc_cmake_generator(specs["msvc_compiler"])
    print_message(f"Build generator: {build_generator}", color=Fore.YELLOW, bright=True)

    artifacts_dir = plugin_folder / "artifacts"
    if artifacts_dir.exists():
        shutil.rmtree(artifacts_dir)

    msvc_dir = plugin_folder / "msvc"
    if not msvc_dir.exists():
        msvc_dir.mkdir()

    print_message(f"msvc dir: {msvc_dir}", color=Fore.YELLOW, bright=True)

    import alfasim_sdk

    sdk_include_dir = alfasim_sdk.get_alfasim_sdk_api_path()

    subprocess.check_call(
        [
            "cmake",
            f"-DSDK_INCLUDE_DIR={sdk_include_dir}",
            f"-B{str(msvc_dir)}",
            f"-H{plugin_folder}",
            "-G",
            build_generator,
        ]
    )


def _remove_hmplugin_files(plugin_folder):
    """Removes hmplugin files inside alfasim_plugins/[plugin_id] given a list of plugin_ids."""
    print_message(
        f'Removing ".hmplugin" files from {plugin_folder}',
        color=Fore.YELLOW,
        bright=True,
    )

    for item in os.listdir(plugin_folder):
        if item.endswith(".hmplugin"):
            file = plugin_folder / item
            print_message(f"Removing {file}", color=Fore.YELLOW, bright=True)
            os.remove(file)

    print_message(
        f'Successfully removed ".hmplugin" files from {plugin_folder}',
        color=Fore.GREEN,
        bright=True,
    )


def _remove_build_folders(plugin_folder):
    print_message(
        f'Removing all "build" folders from {plugin_folder}',
        color=Fore.YELLOW,
        bright=True,
    )

    build_dirs = []

    def find_all_dirs_in_path(path):
        return [e for e in path.iterdir() if e.is_dir()]

    base_dirs = find_all_dirs_in_path(plugin_folder)

    for base_dir in base_dirs:
        if str(base_dir.stem) == "build":
            build_dirs.append(base_dir)

        child_dirs = find_all_dirs_in_path(base_dir)

        for child_dir in child_dirs:
            if str(child_dir.stem) == "build":
                build_dirs.append(child_dir)

    for build_dir in build_dirs:
        shutil.rmtree(build_dir)

    print_message(
        f'Successfully removed all "build" folders from {plugin_folder}',
        color=Fore.GREEN,
        bright=True,
    )

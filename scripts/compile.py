import os
import shutil
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from Cython.Build import cythonize
from setuptools import Extension, setup


@contextmanager
def change_directory(path: Path) -> Generator[None, None, None]:
    """
    Context manager to temporarily change the working directory.
    """
    original_directory = Path().resolve()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original_directory)


class PythonBuildManager:
    """
    Manages the build and cleanup process for a Python project.
    """

    def __init__(
            self, directory: str, *, build: bool = True, build_folder: str = "build",
            delete_py: bool = False, delete_c: bool = False, delete_pyc: bool = False,
            exclude_files: list[str] | None = None, exclude_folders: list[str] | None = None,
    ):
        """
        Initializes the PythonBuildManager with build and delete options.

        Args:
            directory (str): The directory to manage.
            build (bool): Flag to control if Cython extensions should be built.
            build_folder (str): Directory where the build files will be placed.
            delete_py (bool): Flag to control if `.py` files should be deleted.
            delete_c (bool): Flag to control if `.c` files should be deleted.
            delete_pyc (bool): Flag to control if `.pyc` files should be deleted.
            exclude_files (list | None): List of filenames to exclude from operations.
            exclude_folders (list | None): List of folders to exclude from operations.
        """
        self.directory = Path(directory).resolve()
        self.build_flag = build
        self.build_folder = build_folder
        self.delete_py_flag = delete_py
        self.delete_c_flag = delete_c
        self.delete_pyc_flag = delete_pyc
        self.exclude_files = exclude_files or []
        self.exclude_folders = exclude_folders or []
        self.exclude_folders = [Path(exclude_folder).resolve() for exclude_folder in self.exclude_folders]
        self.extensions = []
        self.python_files = list(self.directory.glob("**/*.py"))

    def build_extensions(self) -> None:
        """
        Builds Cython extensions from Python files in the specified directory,
        in-place, excluding files and folders specified in `exclude_files` and `exclude_folders`.
        """
        for file in self.python_files:
            filename = file.resolve().stem
            if file.stat().st_size != 0 and filename not in self.exclude_files:
                relpath = os.path.relpath(os.path.dirname(file.absolute().as_posix()), self.directory)
                if Path(relpath).resolve() not in self.exclude_folders:
                    package_name = (
                        relpath.replace("/", ".").replace("\\", ".") + "." + filename
                        if relpath != "." else filename
                    )
                    print(f"Module {package_name}")
                    # Append the Cython extension
                    self.extensions.append(Extension(package_name, [str(file)]))

        # Temporarily change to the `app` directory to allow in-place compilation
        with change_directory(self.directory):
            # Build all extensions with a custom build folder0
            setup(
                ext_modules=cythonize(
                    self.extensions,
                    compiler_directives={
                        "always_allow_keywords": True,
                        "c_string_type": "str",
                        "c_string_encoding": "utf8",
                        "language_level": 3
                    }
                ),
                script_args=["build_ext", "--inplace"],
                options={"build": {"build_base": self.build_folder}}
            )

        # Delete the build folder after in-place compilation
        self.delete_build_folder()

    def delete_build_folder(self) -> None:
        """
        Deletes the 'build' directory created during the compilation process, if it exists.
        """
        build_dir = Path(self.build_folder)
        if build_dir.exists() and build_dir.is_dir():
            shutil.rmtree(build_dir)
            print("Deleted 'build' folder.")

    def delete_files(self, pattern: str, extension_flag: bool) -> None:
        """
        Deletes files matching a specific pattern if the corresponding flag is set.

        Args:
            pattern (str): The file extension pattern to delete (e.g., ".py", ".c", ".pyc").
            extension_flag (bool): Flag indicating whether to proceed with deletion.
        """
        if extension_flag:
            files = self.directory.glob(f"**/*{pattern}")
            for file in files:
                filename = file.resolve().stem
                relpath = os.path.relpath(os.path.dirname(file.absolute().as_posix()), self.directory)
                # Delete only if the file or folder is not in the exclude list
                if Path(relpath).resolve() not in self.exclude_folders and filename not in self.exclude_files:
                    print(f"Deleting {file}")
                    file.unlink()

    def execute(self) -> None:
        """
        Executes the build and cleanup process based on the initialized flags.
        """
        try:
            if self.build_flag:
                self.build_extensions()
        finally:
            self.delete_files(".py", self.delete_py_flag)
            self.delete_files(".c", self.delete_c_flag)
            self.delete_files(".pyc", self.delete_pyc_flag)


if __name__ == "__main__":
    manager = PythonBuildManager(
        directory="app",
        build=True,
        build_folder="build",
        delete_py=True,
        delete_c=True,
        delete_pyc=True,
        exclude_files=["compile"],
        exclude_folders=["alembic", "alembic/versions", "logs"]
    )
    manager.execute()

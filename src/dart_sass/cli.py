"""
Command-line interface for sass-embedded.
"""

import sys
import subprocess
from pathlib import Path
from .compiler_path import get_compiler_command


def main() -> None:
    """
    Main entry point for the sass CLI command.
    
    This is a thin wrapper that passes arguments directly to the Dart Sass
    executable, similar to the Node.js implementation.
    """
    try:
        # Get the compiler command
        compiler_command = get_compiler_command()
        
        # Pass through all command-line arguments except the script name
        args = compiler_command + sys.argv[1:]
        
        # Determine if we need to use shell on Windows
        use_shell = False
        if sys.platform == 'win32' and compiler_command:
            executable_path = Path(compiler_command[0])
            if executable_path.suffix.lower() in ['.bat', '.cmd']:
                use_shell = True
        
        # Execute the compiler with the provided arguments
        result = subprocess.run(
            args,
            shell=use_shell,
            # Inherit stdio so output goes directly to the terminal
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        
        # Exit with the same code as the compiler
        sys.exit(result.returncode)
        
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

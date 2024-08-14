import os
import cmd
import header
import server as socketServer
import requests


def stopServer(server: socketServer.Server):
    """Stop the server and ensure it's properly shut down."""
    server.stop()
    try:
        # Make a request to the server to ensure it stops
        requests.get(f"http://localhost:{server.port}")
    except requests.RequestException as e:
        print(f"Failed to stop server with requests: {e}")


class Term(cmd.Cmd):
    def __init__(self):
        super().__init__()
        header.init()
        self.prompt = "> "
        self.server = socketServer.Server()

    def emptyline(self):
        """Handle empty lines."""
        return False

    def do_exit(self, arg):
        """Exit the command loop."""
        print("Shutting down z-core...")
        return True

    def do_status(self, arg):
        """Print the status of the server."""
        print(self.server.getStatus())

    def do_start(self, arg):
        """Start the server."""
        self.server.start()

    def do_configure(self, arg):
        """Configure the server."""
        self.server.config()

    def do_clear(self, arg):
        """Clear the screen."""
        os.system("clear")

    def do_ls(self, arg):
        """List directory contents."""
        if os.system("command -v exa > /dev/null") == 0:
            if arg:
                os.system("exa -l " + arg)
            else:
                os.system("exa -l")

        else:
            print("Error: Command 'exa' not found")

    def do_stop(self, arg):
        """Stop the server."""
        stopServer(self.server)

    def default(self, line):
        """Handle unknown commands."""
        print(f"Error: unknown command: {line}")

    def complete_ls(self, text, line, begidx, endidx):
        """Provide tab completion for the ls command."""
        # Completion for `ls` command - if you need specific file completions, implement here
        return [file for file in os.listdir(".") if file.startswith(text)]

    def complete_status(self, text, line, begidx, endidx):
        """Provide tab completion for the status command."""
        return []  # No completions for status

    def complete_clear(self, text, line, begidx, endidx):
        """Provide tab completion for the clear command."""
        return []  # No completions for clear


if __name__ == "__main__":
    term = Term()
    term.cmdloop()

import os
import requests
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Tree, Input, Button, TextArea, Static, Header, Footer, TextLog, Label

API_URL = "http://localhost:8020"


class LoginScreen(Screen):
    """Simple login screen."""

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="login", classes="center"):
            yield Input(placeholder="Username", id="username")
            yield Input(placeholder="Password", password=True, id="password")
            yield Button("Login", id="login_btn")
            yield Label("", id="message")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login_btn":
            username = self.query_one("#username", Input).value
            password = self.query_one("#password", Input).value
            resp = requests.post(f"{API_URL}/api/login", json={"username": username, "password": password})
            if resp.ok:
                self.app.token = resp.json().get("token")
                self.app.push_screen(MainScreen())
            else:
                self.query_one("#message", Label).update("Login failed")


class DownloadScreen(Screen):
    """Prompt for download path."""

    def compose(self) -> ComposeResult:
        with Vertical(id="download", classes="center"):
            yield Label("Save ZIP as:")
            yield Input(placeholder="project.zip", id="path")
            yield Button("Download", id="do_download")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "do_download":
            path = self.query_one("#path", Input).value or "project.zip"
            resp = requests.get(f"{API_URL}/api/download")
            if resp.ok:
                with open(path, "wb") as f:
                    f.write(resp.content)
                self.app.pop_screen()
                main = self.app.get_screen("main")
                if main:
                    main.notify(f"Downloaded to {path}")


class MainScreen(Screen):
    """Main application screen with tree and editor."""

    BINDINGS = [("ctrl+s", "save", "Save")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Tree("Files", id="tree")
            with Vertical(id="right"):
                yield TextArea(id="editor")
                with Horizontal(id="buttons"):
                    yield Button("Save", id="save")
                    yield Button("Diff", id="diff")
                    yield Button("AI", id="ai")
                    yield Button("Download", id="download")
                yield TextLog(id="diff_panel", highlight=True)
                yield TextLog(id="ai_panel")
        yield Footer()

    def on_mount(self) -> None:
        self.current_path: str | None = None
        self.original_content: str = ""
        tree = self.query_one("#tree", Tree)
        resp = requests.get(f"{API_URL}/api/tree")
        if resp.ok:
            for file_path in resp.json():
                tree.root.add_leaf(file_path, data=file_path)
            tree.root.expand()

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        path = event.node.data
        if path:
            resp = requests.get(f"{API_URL}/api/file", params={"path": path})
            if resp.ok:
                content = resp.json().get("content", "")
                self.current_path = path
                self.original_content = content
                self.query_one("#editor", TextArea).value = content

    def action_save(self) -> None:
        self.save_file()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self.save_file()
        elif event.button.id == "diff":
            self.show_diff()
        elif event.button.id == "ai":
            self.call_ai()
        elif event.button.id == "download":
            self.app.push_screen(DownloadScreen())

    def save_file(self) -> None:
        if not self.current_path:
            return
        content = self.query_one("#editor", TextArea).value
        requests.post(f"{API_URL}/api/file", params={"path": self.current_path}, json={"content": content})
        self.original_content = content

    def show_diff(self) -> None:
        content = self.query_one("#editor", TextArea).value
        resp = requests.post(f"{API_URL}/api/diff", json={"old": self.original_content, "new": content})
        if resp.ok:
            diff_text = resp.json().get("diff", "")
            panel = self.query_one("#diff_panel", TextLog)
            panel.clear()
            panel.write(diff_text)

    def call_ai(self) -> None:
        content = self.query_one("#editor", TextArea).value
        resp = requests.post(f"{API_URL}/api/ai", json={"message": content})
        panel = self.query_one("#ai_panel", TextLog)
        panel.clear()
        if resp.ok:
            panel.write(str(resp.json()))
        else:
            panel.write("Error")

    def notify(self, message: str) -> None:
        panel = self.query_one("#ai_panel", TextLog)
        panel.write(message)


class DevLabApp(App):
    CSS = """
    #login, #download { align: center middle; height: 100%; }
    #right { width: 1fr; }
    #editor { height: 10; }
    #diff_panel, #ai_panel { height: 10; }
    """

    def on_mount(self) -> None:
        self.token: str | None = None
        self.push_screen(LoginScreen())


if __name__ == "__main__":
    DevLabApp().run()

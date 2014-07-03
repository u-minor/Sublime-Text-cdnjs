import sublime
import sublime_plugin


class CdnjsLibraryPickerCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        self.packages = args["packages"]
        self.onlyURL = args["onlyURL"]
        self.wholeFile = args["wholeFile"]
        sublime.set_timeout(self.show_quickpanel, 10)

    def get_list(self):
        return [[x['name'], x.get('description', '')] for x in self.packages]

    def show_quickpanel(self):
        self.view.window().show_quick_panel(self.get_list(), self.callback)

    def callback(self, index):
        if index == -1:
            return

        pkg = self.packages[index]
        self.view.run_command('cdnjs_version_picker', {
            "package": pkg,
            "onlyURL": self.onlyURL,
            "wholeFile":self.wholeFile
        })


class CdnjsVersionPickerCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        self.package = args["package"]
        self.onlyURL = args["onlyURL"]
        self.wholeFile = args["wholeFile"]
        sublime.set_timeout(self.show_quickpanel, 10)

    def get_list(self):
        return sorted(self.package['assets'], reverse=True)

    def show_quickpanel(self):
        self.view.window().show_quick_panel(self.get_list(), self.callback)

    def callback(self, index):
        if index == -1:
            return

        version = sorted(self.package["assets"], reverse=True)[index]
        files = self.package["assets"][version]
        self.view.run_command('cdnjs_file_picker', {
            "package": self.package,
            "onlyURL": self.onlyURL,
            "wholeFile": self.wholeFile,
            "version": version,
            "files": files
        })


class CdnjsFilePickerCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        self.package = args.get("package", {})
        self.version = args.get("version", '')
        self.files = args.get("files", [])
        self.onlyURL = args.get("onlyURL", False)
        self.wholeFile = args.get("wholeFile", False)
        sublime.set_timeout(self.show_quickpanel, 10)

    def get_list(self):
        return sorted(self.files)

    def show_quickpanel(self):
        self.view.window().show_quick_panel(self.get_list(), self.callback)

    def callback(self, index):
        if index == -1:
            return

        self.view.run_command('cdnjs_tag_builder', {
            "package": self.package,
            "version": self.version,
            "file": self.files[index],
            "onlyURL": self.onlyURL,
            "wholeFile": self.wholeFile
        })

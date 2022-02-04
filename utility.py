import sublime, sublime_plugin
import os
from os.path import dirname
from os import path

# opens settings/keymap/sublime-commnads file in split view
class ParserEditSettingsCommand(sublime_plugin.TextCommand):
    
    def run(self, edit, base_file, user_file, default):
        
        # root_dir = dirname(__file__)
        platform = '{os}'.format(
            os={ 'windows': 'Windows', 'linux': 'Linux', 'osx': 'OSX' }[sublime.platform().lower()]
        )
        
        print("base_file:", base_file)
        print("user_file:", user_file)
        base_file.replace('$platform', platform)
        user_file.replace('$platform', platform)
        print("base_file:", base_file)
        print("user_file:", user_file)
        
        # if action == 'open_settings':
        self.view.window().run_command('new_window')
        sublime.active_window().set_sidebar_visible(False)
        
        # sublime.active_window().open_file(path.join(root_dir, default_settings_file))
        sublime.active_window().open_file(base_file)
        sublime.active_window().set_layout({'cols': [0, 0.5, 1], 'rows': [0, 1], 'cells': [[0, 0, 1, 1], [1, 0, 2, 1]]})
        
        # user_settings_file = path.join(sublime.packages_path(), 'User', 'CompetitiveProgrammingParser.sublime-settings')
        # if not path.exists(user_settings_file):
        if not path.exists(user_file):
            with open(user_file, 'w') as f:
                f.write(default)

        user_file_view = sublime.active_window().open_file(user_file)
        sublime.active_window().set_view_index(user_file_view, 1, 0)
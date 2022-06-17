import sublime, sublime_plugin
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, _thread, threading
import platform, os, sys, time

TESTS_FILE_SUFFIX = ''
totalProblems, problems_parsed, successful_problems = 1, 0, 0
settings, user_settings = None, None
contest_name, contest_dir, working_dir, error, parse_in_view_file, view_file_name, sep = None, None, None, False, False, None, False
problems = []

def reset():
    global totalProblems, problems_parsed, successful_problems, contest_name, contest_dir, working_dir, error, parse_in_view_file, view_file_name, sep, problems
    totalProblems, problems_parsed, successful_problems = 1, 0, 0
    contest_name, contest_dir, working_dir, error, parse_in_view_file, view_file_name, sep = None, None, None, False, False, None, False
    problems = []

def plugin_loaded():
    update_settings()
    settings.add_on_change('extensions_path', update_settings)
    
def show_msg(msg):
    global sep
    if not sep:
        sep = True
        print(5 * '\n' + '------------------------------START------------------------------')
    sublime.active_window().run_command('show_panel', {"panel": "console"})
    print(msg)
    
def close_panel():
    if not error:
        show_msg('closing console...')
        time.sleep(5)
        sublime.active_window().run_command('hide_panel')
        print('closed console')
    print('------------------------------END------------------------------')
    
def GetSettings(key):
    global settings, user_settings
    if user_settings.get(key) != None:
        return user_settings.get(key)
    return settings.get(key)
    

def update_settings():
    global settings, user_settings, TESTS_FILE_SUFFIX
    settings = sublime.load_settings('CompetitiveProgrammingParser ({os}).sublime-settings'.format(
        os={ 'windows': 'Windows', 'linux': 'Linux', 'osx': 'OSX' }[sublime.platform().lower()])
    )
    user_settings = sublime.load_settings('CompetitiveProgrammingParser.sublime-settings')
    if GetSettings('TESTS_FILE_SUFFIX') != None:
        TESTS_FILE_SUFFIX = GetSettings('TESTS_FILE_SUFFIX')
    else:
        raise Exception('TESTS_FILE_SUFFIX not found in settings file')
    print("CompetitiveProgrammingParser Settings loaded successfully")
        
# fetch current and working directories
def fetch_directory(oj, action):
    global contest_name, contest_dir, working_dir, error
    if contest_dir == None: # implies that command wasn't invoked from the sidebar
        key = 'default' if GetSettings('use_default_directory') else oj
        if key not in GetSettings('directory').keys() or GetSettings('directory')[key] == '':
            contest_dir = os.path.dirname(__file__)
        else:
            contest_dir = GetSettings('directory')[key]
    if not os.path.exists(contest_dir):
        os.mkdir(contest_dir)
    working_dir = contest_dir
    if action == 'contest':
        working_dir = os.path.join(working_dir, contest_name)
        try:
            if not os.path.exists(working_dir):
                os.mkdir(working_dir)
        except Exception as e:
            error = True
            raise Exception(str(e) + '\nPlease update your CompetitiveProgrammingParser settings.')
    
    if GetSettings('open_in_new_window') and action == 'contest':
        os.system('subl -n \"' + working_dir + '\"')
    else:
        os.system('subl -a \"' + working_dir + '\"')

# create file and testcases
def parse_testcases(tests, problem, action):
    filename = problem + GetSettings('lang_extension')
    if parse_in_view_file:
        filename = view_file_name
    filename = os.path.join(working_dir, filename)
    if not os.path.exists(filename):
        file = open(filename, 'w')
        file.close()

    testcases = []
    tests = tests["tests"]
    for test in tests:
        testcase = {
            "test": test["input"],
            "correct_answers": [test["output"].strip()]
        }
        testcases.append(testcase)
    
    with open(filename + TESTS_FILE_SUFFIX, "w") as f:
        f.write(json.dumps(testcases))
    global successful_problems
    successful_problems += 1
    
def check_page_correctness(action):
    global error
    if totalProblems > 1 and action != 'contest':
        error = True
        raise Exception('It seems that you are trying to parse a contest page. Please open a problem page!')
        
def get_problem_name(tests, oj):
    global contest_name
    problem = tests["name"]
    if contest_name == None:
        contest_name = tests["group"].split('-', 1)[-1].strip()
        show_msg('Contest: ' + contest_name)
    if oj == "CodeChef":
        problem = tests["url"].split('/')[-1]
    elif oj == "Codeforces" or oj == "Yandex":
        problem = tests["name"].split('.')[0]
    elif oj == "AtCoder":
        problem = tests["name"].split(' ')[0]
    problem = problem.replace(" ", "_")
    return problem

def handle(tests, action):
    global totalProblems, problems_parsed, error
    problems_parsed += 1
    totalProblems = tests["batch"]['size']
    
    try:
        check_page_correctness(action)        
    except Exception as e:
        raise Exception(e)
    
    oj = tests["group"].split('-')[0].strip()
    
    problem = get_problem_name(tests, oj)
    
    cnt = problems.count(problem)
    if cnt == 5:
        error = True
        show_msg('❌ Aborting the process. Please check your internet connection and try again')
        return
    elif cnt > 0:
        problems.append(problem)
        show_msg('❌ Could not parse the next problem.(possibly due to slow internet connection).\nTrying again(' + str(cnt) + ')...')
        problems_parsed -= 1
        return
    else:
        problems.append(problem)
        
    if problems_parsed == 1 and action != 'testcase':
        try:
            fetch_directory(oj, action)
        except Exception as e:
            raise Exception(e)
        show_msg('parsing ' + action + "...")
    
    try:
        parse_testcases(tests, problem, action)
        show_msg("✔️ Problem " + problem + " (" + str(problems_parsed) + "/" + str(totalProblems) + ")" + " success")
    except Exception as e:
        show_msg("❌ Problem " + problem + " (" + str(problems_parsed) + "/" + str(totalProblems) + ")" + " fail")

def MakeHandlerClass(action):
    class HandleRequests(BaseHTTPRequestHandler):
        def do_POST(self):
            try:
                handle(json.loads(self.rfile.read(int(self.headers['Content-Length'])).decode('utf8')), action)
            except Exception as e:
                show_msg("❌ error: " + str(e))
            threading.Thread(target=self.server.shutdown, daemon=True).start()
    return HandleRequests

class CompetitiveCompanionServer:
    def startServer(action):
        try:
            httpd = HTTPServer(('localhost', 12345), MakeHandlerClass(action))
            while problems_parsed < totalProblems and not error:
                httpd.serve_forever()
            if action == 'contest' and successful_problems > 0:
                x = "All" if successful_problems == totalProblems else "Only"
                show_msg(x + " (" + str(successful_problems) + "/" + str(totalProblems) + ") Problems of \'" + str(contest_name) + "\'" + ' were parsed successfully')
            close_panel()
        except Exception as e:
            pass

class CompetitiveProgrammingParserFileCommand(sublime_plugin.TextCommand):
    def run(self, edit, action):
        global error
        reset()
        try:
            if action == 'testcase' and self.view.file_name() == None:
                error = True
                raise Exception("Can't parse testcases for an untitled file.")
                                
            if action == 'testcase':
                global parse_in_view_file, view_file_name
                parse_in_view_file = True
                view_file_name = self.view.file_name()
                
            if GetSettings('lang_extension') == None:
                error = True
                raise Exception('Language not set. Update your CompetitiveProgrammingParser settings.')
            
            _thread.start_new_thread(CompetitiveCompanionServer.startServer, (action,))
        
        except Exception as e:
            show_msg("❌ error: " + str(e))
            close_panel()
    
class CompetitiveProgrammingParserSidebarCommand(sublime_plugin.WindowCommand):
    def run(self, dirs, action, **kwargs):
        reset()
        global contest_dir, error
        contest_dir = dirs[0]
        try:
            if GetSettings('lang_extension') == None:
                error = True
                raise Exception('language extension not set. Update your CompetitiveProgrammingParser settings.')
            _thread.start_new_thread(CompetitiveCompanionServer.startServer, (action,))
        except Exception as e:
            show_msg("❌ error: " + str(e))
            close_panel()

    def is_enabled(self, dirs, action):
        return len(dirs) == 1

    def is_visible(self, dirs, action):
        return len(dirs) == 1
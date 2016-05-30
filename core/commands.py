import os
import re
import getopt
import dropbox

from core.out import *
from core.colors import bold, cyan, white
from core.session import __session__


class Commands(object):

    def __init__(self):
        # Map commands to their related functions.
        self.commands = dict(
            token=dict(obj=self.cmd_token,
                       description="Set access token"),
            userinfo=dict(obj=self.cmd_userinfo,
                          description="Show information of user"),
            lcd=dict(obj=self.cmd_lcd,
                     description="Change local directory"),
            lls=dict(obj=self.cmd_lls,
                     description="List local files in current directory"),
            cd=dict(obj=self.cmd_cd,
                    description="Change remote directory"),
            ls=dict(obj=self.cmd_ls,
                    description="List files in current remote directory"),
            mkdir=dict(obj=self.cmd_mkdir,
                       description="Make a new directory on remote"),
            put=dict(obj=self.cmd_put,
                     description="Upload local file to remote"),
            get=dict(obj=self.cmd_get,
                     description="Download remote file to local"),
            delete=dict(obj=self.cmd_delete,
                        description="Delete file on remote"),
            clear=dict(obj=self.cmd_clear,
                       description="Clear the console"),
            help=dict(obj=self.cmd_help,
                      description="Show this help message"),
            close=dict(obj=self.cmd_close,
                       description="Close the current session"),
        )

    def cmd_clear(self, *args):

        os.system('clear')

    def cmd_help(self, *args):

        print(bold("Commands:"))

        rows = []
        for command_name, command_item in self.commands.items():
            rows.append([command_name, command_item['description']])

        print(table(['Command', 'Description'], rows))

    def cmd_close(self, *args):

        __session__.clear()

    def cmd_token(self, *args):

        def usage():
            print("usage: token TOKEN")

        try:
            opts, argv = getopt.getopt(args, '')
        except getopt.GetoptError as e:
            print(e)
            usage()
            return

        if len(argv) == 0:
            usage()
            return
        else:
            token = argv[0]

        # Filter of quotes
        if re.search('\'', token):
            token = token.strip('\'')
        elif re.search('\"', token):
            token = token.strip('\"')

        __session__.set_token(token)
        self.cmd_userinfo()

    def cmd_userinfo(self, *args):
        if __session__.is_set():
            info = __session__.dbx.users_get_current_account()
            print(table(
                ['Key', 'Value'],
                [
                    ('Name', info.name.display_name),
                    ('E-mail', info.email)
                ]
            ))

    def cmd_lls(self, *args):
        opts, argv = getopt.getopt(args, '')
        if (len(argv) >= 1):
            dirname = argv[0].strip()
        else:
            dirname = __session__.ldir

        index = 1
        row = []
        for filename in os.listdir(dirname):
            if os.path.isdir(dirname+"/"+filename):
                filetype = "Directory"
            else:
                filetype = "File"
            row.append([index, filename, filetype])
            index += 1
        try:
            print table(['index', 'File name', 'File type'], row)
        except OSError:
            print "No such file or directory: {0}".format(dirname+"/"+filename)

    def cmd_lcd(self, *args):
        opts, argv = getopt.getopt(args, '')
        if (len(argv) >= 1):
            dirname = argv[0].strip()
        else:
            dirname = os.getenv("HOME")

        if re.match('^\/', dirname):
            __session__.ldir = dirname
        else:
            __session__.ldir = os.path.abspath(__session__.ldir+"/"+dirname)

        print_info("Local Directory set as: {0}".format(__session__.ldir))

    def cmd_cd(self, *args):
        opts, argv = getopt.getopt(args, '')
        if (len(argv) >= 1):
            dirname = argv[0].strip()
            __session__.rdir += "/"+dirname
        else:
            __session__.rdir = ''

        print_info("Remote Directory set as: {0}".format(__session__.rdir))

    def cmd_ls(self, *args):
        opts, argv = getopt.getopt(args, '')
        if (len(argv) >= 1):
            dirname = __session__.rdir+"/"+argv[0].strip()
        else:
            dirname = __session__.rdir

        result = __session__.dbx.files_list_folder(dirname)

        index = 1
        row = []
        for f in result.entries:
            if isinstance(f, dropbox.files.FolderMetadata):
                filetype = 'Directory'
            else:
                filetype = 'File'

            row.append([index, f.name, filetype])
            index += 1

        print table(['index', 'File name', 'File type'], row)

    def cmd_mkdir(self, *args):
        pass

    def cmd_put(self, *args):

        def usage():
            print("usage: put FILE")

        opts, argv = getopt.getopt(args, '')
        if (len(argv) >= 1):
            filename = argv[0]
        else:
            usage()

        if not re.search('/', filename):
            filename = __session__.ldir+'/'+filename

        try:
            file_data = open(filename, 'rb').read()
        except IOError:
            print_warn("No such file!")

        finally:
            result = __session__.dbx.files_upload(file_data, '/test/README.md')

            if result.id:
                print_info("Upload file {} successfully.".format(filename))

        """
        result = __session__.dbx.files_list_folder(dirname)

        index = 1
        row = []
        for f in result.entries:
            if isinstance(f, dropbox.files.FolderMetadata):
                filetype = 'Directory'
            else:
                filetype = 'File'

            row.append([index, f.name, filetype])
            index += 1

        print table(['index', 'File name', 'File type'], row)
        """
    def cmd_get(self, *args):
        pass
    def cmd_delete(self, *args):
        pass
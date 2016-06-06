import os
import re
import getopt
import dropbox

from ConfigParser import SafeConfigParser

from core.out import *
from core.colors import bold
from core.session import __session__


class Commands(object):

    def __init__(self):
        # Map commands to their related functions.
        self.commands = dict(
            cd=dict(obj=self.cmd_cd,
                    description="Change remote directory"),
            clear=dict(obj=self.cmd_clear,
                       description="Clear the console"),
            close=dict(obj=self.cmd_close,
                       description="Close the current session"),
            delete=dict(obj=self.cmd_delete,
                        description="Delete file on remote (not implement)"),
            get=dict(obj=self.cmd_get,
                     description="Download remote file to local"),
            help=dict(obj=self.cmd_help,
                      description="Show this help message"),
            lcd=dict(obj=self.cmd_lcd,
                     description="Change local directory"),
            lls=dict(obj=self.cmd_lls,
                     description="List local files in current directory"),
            ls=dict(obj=self.cmd_ls,
                    description="List files in current remote directory"),
            mkdir=dict(obj=self.cmd_mkdir,
                       description="Make a new directory on remote (not implement)"),
            put=dict(obj=self.cmd_put,
                     description="Upload local file to remote"),
            token=dict(obj=self.cmd_token,
                       description="Set access token"),
            userinfo=dict(obj=self.cmd_userinfo,
                          description="Show information of user"),
        )

    def _input_check(func):

        def func_wrapper(calling_obj, *args, **kwargs):
            need_usage = ['cmd_token', 'cmd_mkdir', 'cmd_put', 'cmd_get']
            try:
                opts, argv = getopt.getopt(args, '')
            except getopt.GetoptError as e:
                print(e)
                print(func.__doc__)
                return

            if len(argv) >= 1:
                new_argv = []
                for element in argv:
                    element = element.strip()
                    if re.search('\'', element):
                        element = element.strip('\'')
                    elif re.search('\"', element):
                        element = element.strip('\"')
                    new_argv.append(element)
                argv = tuple(new_argv)

            else:
                if func.__name__ in need_usage:
                    print(func.__doc__)
                    return

            return func(calling_obj, opts, argv)

        return func_wrapper

    def cmd_clear(self):

        os.system('clear')

    def cmd_help(self):

        print(bold("Commands:"))

        rows = []
        for command_name, command_item in sorted(self.commands.items()):
            rows.append([command_name, command_item['description']])

        print(table(['Command', 'Description'], rows))

    def cmd_close(self):

        __session__.clear()
        sys.exit(0)

    @_input_check
    def cmd_token(self, opts, argv):
        """ Set access token

        Example:
            > token TOKEN
        """
        token = argv[0]
        config = SafeConfigParser()
        config.read('conf/dropbox.conf')
        config.remove_section('Credentials')
        config.add_section('Credentials')
        config.set('Credentials', 'AccessToken', token)
        with open('conf/dropbox.conf', 'w') as f:
            config.write(f)

        __session__.set_token(token)

    def cmd_userinfo(self):
        if __session__.is_set():
            info = __session__.dbx.users_get_current_account()
            print(table(
                ['Key', 'Value'],
                [
                    ('Name', info.name.display_name),
                    ('E-mail', info.email)
                ]
            ))

    @_input_check
    def cmd_lls(self, opts, argv):
        if (len(argv) >= 1):
            dirname = argv[0]
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

    @_input_check
    def cmd_lcd(self, opts, argv):
        if (len(argv) >= 1):
            dirname = argv[0]
        else:
            dirname = os.getenv("HOME")

        if re.match('^\/', dirname):
            __session__.ldir = dirname
        else:
            __session__.ldir = os.path.abspath(__session__.ldir+"/"+dirname)

        print_info("Local Directory set as: {0}".format(__session__.ldir))

    @_input_check
    def cmd_cd(self,  opts, argv):
        if (len(argv) >= 1):
            dirname = argv[0]
            __session__.rdir += "/"+dirname
        else:
            __session__.rdir = ''

        print_info("Remote Directory set as: {0}".format(__session__.rdir))

    @_input_check
    def cmd_ls(self, opts, argv):
        if (len(argv) >= 1):
            dirname = __session__.rdir+"/"+argv[0]
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

    @_input_check
    def cmd_mkdir(self, opts, argv):
        """Create directory

        Example:
            > mkdir foldername
        """

        foldername = argv[0]
        if not re.search('/', foldername):
            foldername = __session__.rdir+'/'+foldername

        try:
            __session__.dbx.files_create_folder(foldername)
            print_info("Create folder {} successfully.".format(foldername))
        except:
            print_warn("Folder Create FAILED!")

    @_input_check
    def cmd_put(self, opts, argv):
        """Upload file to Dropbox directory

        Example:
            > put FILE
        """

        filename = argv[0]
        if not re.search('/', filename):
            local_file = __session__.ldir+'/'+filename
            remote_file = __session__.rdir+'/'+filename
        else:
            remote_file = __session__.rdir+'/'+filename.split('/').pop()

        try:
            file_data = open(local_file, 'rb').read()
        except IOError:
            print_warn("No such file!")

        finally:
            result = __session__.dbx.files_upload(file_data, remote_file)

            if result.id:
                print_info("Upload file {} successfully.".format(local_file))

    @_input_check
    def cmd_get(self, opts, argv):
        """Download file from Dropbox directory

        Example:
            > get FILE
        """

        filename = argv[0]
        if not re.search('/', filename):
            filename = __session__.rdir+'/'+filename

        try:
            file_meta, result = __session__.dbx.files_download(filename)
        except IOError:
            print_warn("No such file!")

        if result.ok:
            local_name = filename.split('/').pop()
            with open(__session__.ldir+'/'+local_name, 'wb') as f:
                for block in result.iter_content(1024):
                    f.write(block)
            print_info("Download file {} successfully.".format(local_name))

    def cmd_delete(self, *args):
        pass

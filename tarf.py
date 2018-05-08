import argparse
import os
import platform
import subprocess
import shutil
import shlex
import glob
import re
import tarfile
import zipfile
from email.utils import formatdate
from datetime import tzinfo
import time
import multiprocessing
import fileinput
import stat
import json

def box_draw(msg):
    spaces_no = 80 - len(msg) - 4
    spacer = ' ' * spaces_no

    if OS == 'Linux':
        print('''
┌──────────────────────────────────────────────────────────────────────────────┐
│ %s%s │
└──────────────────────────────────────────────────────────────────────────────┘''' % (msg, spacer))
    else:
        print('''
+-----------------------------------------------------------------------------+
| %s%s|
+-----------------------------------------------------------------------------+''' % (msg, spacer))

def tarball():
    box_draw("Compress binaries into a bzip2 tarball")
    tar = tarfile.open(prefix + '.tar.bz2', 'w:bz2')
    print('Creating archive: ' + os.path.basename(prefix) + '.tar.bz2')
    tar.add(prefix, arcname=os.path.basename(prefix))
    tar.close()

def tarball_deb():
    box_draw("Compress compiled binaries into a bzip2 tarball")
    tar = tarfile.open(os.path.join(workdir + '.orig.tar.bz2'), 'w:bz2')
    tar.add(prefix, arcname=os.path.basename(prefix))
    tar.close()

def fetch_llvm(llvm_revision):
    print('Current working directory is: ' + workdir + '\n')

    if "github.com" in LLVM_GIT_URL and args['create_dev_env'] is None and args['use_wget']:
        _, _, _, user, repo = LLVM_GIT_URL.split('/')
        print('Fetching LLVM ...')
        wget(url='https://github.com/%s/%s' % (user, repo.replace('.git', '')) +
                 '/archive/cling-patches-r%s.tar.gz' % llvm_revision,
             out_dir=workdir)

        print('Extracting: ' + os.path.join(workdir, 'cling-patches-r%s.tar.gz' % llvm_revision))
        tar = tarfile.open(os.path.join(workdir, 'cling-patches-r%s.tar.gz' % llvm_revision))
        tar.extractall(path=workdir)
        tar.close()

        os.rename(os.path.join(workdir, 'llvm-cling-patches-r%s' % llvm_revision), srcdir)

        if os.path.isfile(os.path.join(workdir, 'cling-patches-r%s.tar.gz' % llvm_revision)):
            print("Remove file: " + os.path.join(workdir, 'cling-patches-r%s.tar.gz' % llvm_revision))
            os.remove(os.path.join(workdir, 'cling-patches-r%s.tar.gz' % llvm_revision))

        print()
        return

    def checkout():
        if LLVM_BRANCH:
            exec_subprocess_call('git checkout %s' % LLVM_BRANCH, srcdir)
        else:
            exec_subprocess_call('git checkout cling-patches-r%s' % llvm_revision, srcdir)

    def get_fresh_llvm():
        if LLVM_BRANCH:
            exec_subprocess_call('git clone --depth=10 --branch %s %s %s'
                                 % (LLVM_BRANCH, LLVM_GIT_URL, srcdir), workdir)
        else:
            exec_subprocess_call('git clone %s %s' % (LLVM_GIT_URL, srcdir), workdir)

        checkout()

    def update_old_llvm():
        exec_subprocess_call('git stash', srcdir)

        # exec_subprocess_call('git clean -f -x -d', srcdir)

        checkout()

        if LLVM_BRANCH:
            exec_subprocess_call('git pull origin %s' % LLVM_BRANCH, srcdir)
        else:
            exec_subprocess_call('git fetch --tags', srcdir)
            exec_subprocess_call('git pull origin refs/tags/cling-patches-r%s'
                                 % llvm_revision, srcdir)

    if os.path.isdir(srcdir):
        update_old_llvm()
    else:
        get_fresh_llvm()



def fetch_clang(llvm_revision):
    if "github.com" in CLANG_GIT_URL and args['create_dev_env'] is None and args['use_wget']:
        _, _, _, user, repo = CLANG_GIT_URL.split('/')
        print('Fetching Clang ...')
        wget(url='https://github.com/%s/%s' % (user, repo.replace('.git', '')) +
                 '/archive/cling-patches-r%s.tar.gz' % llvm_revision,
             out_dir=workdir)

        print('Extracting: ' + os.path.join(workdir, 'cling-patches-r%s.tar.gz' % llvm_revision))
        tar = tarfile.open(os.path.join(workdir, 'cling-patches-r%s.tar.gz' % llvm_revision))
        tar.extractall(path=os.path.join(srcdir, 'tools'))
        tar.close()

        os.rename(os.path.join(srcdir, 'tools', 'clang-cling-patches-r%s' % llvm_revision),
                  os.path.join(srcdir, 'tools', 'clang'))

        if os.path.isfile(os.path.join(workdir, 'cling-patches-r%s.tar.gz' % llvm_revision)):
            print("Remove file: " + os.path.join(workdir, 'cling-patches-r%s.tar.gz' % llvm_revision))
            os.remove(os.path.join(workdir, 'cling-patches-r%s.tar.gz' % llvm_revision))

        print()
        return

    toolsdir = os.path.join(srcdir, 'tools')
    clangdir = os.path.join(toolsdir, 'clang')
    def checkout():
       if CLANG_BRANCH:
           exec_subprocess_call('git checkout %s' % CLANG_BRANCH, clangdir)
       else:
           exec_subprocess_call('git checkout cling-patches-r%s' % llvm_revision, clangdir)

    def get_fresh_clang():
        if CLANG_BRANCH:
            exec_subprocess_call('git clone --depth=10 --branch %s %s'
                                 % (CLANG_BRANCH, CLANG_GIT_URL), toolsdir)
        else:
            exec_subprocess_call('git clone %s' % CLANG_GIT_URL, toolsdir)

        checkout()

    def update_old_clang():
        exec_subprocess_call('git stash', clangdir)

        # exec_subprocess_call('git clean -f -x -d', clangdir)

        exec_subprocess_call('git fetch --tags', clangdir)

        checkout()
        if CLANG_BRANCH:
            exec_subprocess_call('git pull origin %s' % CLANG_BRANCH, clangdir)
        else:
            exec_subprocess_call('git fetch --tags', clangdir)
            exec_subprocess_call('git pull origin refs/tags/cling-patches-r%s' % llvm_revision,
                                  clangdir)

    if os.path.isdir(clangdir):
        update_old_clang()
    else:
        get_fresh_clang()


parser = argparse.ArgumentParser(description='Cling Packaging Tool')
parser.add_argument('-c', '--check-requirements', help='Check if packages required by the script are installed',
                    action='store_true')
parser.add_argument('--current-dev',
                    help=('--current-dev:<tar | deb | nsis | rpm | dmg | pkg> will package the latest development snapshot in the given format'
                          + '\n--current-dev:branch:<branch> will build <branch> on llvm, clang, and cling'
                          + '\n--current-dev:branches:<a,b,c> will build branch <a> on llvm, <b> on clang, and <c> on cling'))
parser.add_argument('--last-stable',
                    help='Package the last stable snapshot in one of these formats: tar | deb | nsis | rpm | dmg | pkg')
parser.add_argument('--tarball-tag', help='Package the snapshot of a given tag in a tarball (.tar.bz2)')
parser.add_argument('--deb-tag', help='Package the snapshot of a given tag in a Debian package (.deb)')
parser.add_argument('--rpm-tag', help='Package the snapshot of a given tag in an RPM package (.rpm)')
parser.add_argument('--nsis-tag', help='Package the snapshot of a given tag in an NSIS installer (.exe)')
parser.add_argument('--dmg-tag', help='Package the snapshot of a given tag in a DMG package (.dmg)')

# Variable overrides
parser.add_argument('--with-llvm-url', action='store', help='Specify an alternate URL of LLVM repo',
                    default='http://root.cern.ch/git/llvm.git')
parser.add_argument('--with-clang-url', action='store', help='Specify an alternate URL of Clang repo',
                    default='http://root.cern.ch/git/clang.git')
parser.add_argument('--with-cling-url', action='store', help='Specify an alternate URL of Cling repo',
                    default='https://github.com/root-project/cling.git')

parser.add_argument('--no-test', help='Do not run test suite of Cling', action='store_true')
parser.add_argument('--skip-cleanup', help='Do not clean up after a build', action='store_true')
parser.add_argument('--use-wget', help='Do not use Git to fetch sources', action='store_true')
parser.add_argument('--create-dev-env', help='Set up a release/debug environment')

if platform.system() != 'Windows':
    parser.add_argument('--with-workdir', action='store', help='Specify an alternate working directory for CPT',
                        default=os.path.expanduser(os.path.join('~', 'ci', 'build')))
else:
    parser.add_argument('--with-workdir', action='store', help='Specify an alternate working directory for CPT',
                        default='C:\\ci\\build\\')

parser.add_argument('--make-proper', help='Internal option to support calls from build system')
parser.add_argument('--verbose', help='Tell CMake to build with verbosity', action='store_true')
parser.add_argument('--with-cmake-flags', help='Additional CMake configuration flags', default='')
parser.add_argument('--stdlib', help=('C++ Library to use, stdlibc++ or libc++.'
                                     '  To build a spcific llvm <tag> of libc++ with cling '
                                     'specify libc++,<tag>'),
                    default='')
parser.add_argument('--compiler', help='The compiler being used to make cling (for heuristics only)',
                    default='')


args = vars(parser.parse_args())

###############################################################################
#                           Platform initialization                           #
###############################################################################

OS = platform.system()
FAMILY = os.name.upper()

if OS == 'Windows':
    DIST = 'N/A'
    RELEASE = OS + ' ' + platform.release()
    REV = platform.version()

    EXEEXT = '.exe'
    SHLIBEXT = '.dll'

    TMP_PREFIX = 'C:\\Windows\\Temp\\cling-obj\\'

elif OS == 'Linux':
    DIST = platform.linux_distribution()[0]
    RELEASE = platform.linux_distribution()[2]
    REV = platform.linux_distribution()[1]

    EXEEXT = ''
    SHLIBEXT = '.so'

    TMP_PREFIX = os.path.join(os.sep, 'tmp', 'cling-obj' + os.sep)

elif OS == 'Darwin':
    DIST = 'MacOSX'
    RELEASE = platform.release()
    REV = platform.mac_ver()[0]

    EXEEXT = ''
    SHLIBEXT = '.dylib'

    TMP_PREFIX = os.path.join(os.sep, 'tmp', 'cling-obj' + os.sep)

else:
    # Extensions will be detected anyway by set_ext()
    EXEEXT = ''
    SHLIBEXT = ''

    # TODO: Need to test this in other platforms
    TMP_PREFIX = os.path.join(os.sep, 'tmp', 'cling-obj' + os.sep)

###############################################################################
#                               Global variables                              #
###############################################################################

workdir = os.path.abspath(os.path.expanduser(args['with_workdir']))
srcdir = os.path.join(workdir, 'cling-src')
CLING_SRC_DIR = os.path.join(srcdir, 'tools', 'cling')
CPT_SRC_DIR = os.path.join(CLING_SRC_DIR, 'tools', 'packaging')
LLVM_OBJ_ROOT = os.path.join(workdir, 'builddir')
prefix = ''
LLVM_GIT_URL = args['with_llvm_url']
CLANG_GIT_URL = args['with_clang_url']
CLING_GIT_URL = args['with_cling_url']
EXTRA_CMAKE_FLAGS = args.get('with_cmake_flags')
CMAKE = os.environ.get('CMAKE', None)
if not CMAKE:
    if platform.system() == 'Windows':
        CMAKE = os.path.join(TMP_PREFIX, 'bin', 'cmake', 'bin', 'cmake.exe')
    else:
        CMAKE = 'cmake'

# logic is too confusing supporting both at the same time
if args.get('stdlib') and EXTRA_CMAKE_FLAGS.find('-DLLVM_ENABLE_LIBCXX=') != -1:
    print('use of --stdlib cannot be combined with -DLLVM_ENABLE_LIBCXX')
    parser.print_help()
    raise SystemExit

CLING_BRANCH = CLANG_BRANCH = LLVM_BRANCH = None
if args['current_dev']:
    cDev = args['current_dev']
    if cDev.startswith('branch:'):
      CLING_BRANCH = CLANG_BRANCH = LLVM_BRANCH = cDev[7:]
    elif cDev.startswith('branches:'):
      CLING_BRANCH, CLANG_BRANCH, LLVM_BRANCH = cDev[9:].split(',')

# llvm_revision = urlopen(
#    "https://raw.githubusercontent.com/root-project/cling/master/LastKnownGoodLLVMSVNRevision.txt").readline().strip().decode(
#   'utf-8')
VERSION = ''
REVISION = ''
# Travis needs some special behaviour
TRAVIS_BUILD_DIR = os.environ.get('TRAVIS_BUILD_DIR', None)
APPVEYOR_BUILD_FOLDER = os.environ.get('APPVEYOR_BUILD_FOLDER', None)

# Make sure git log is invoked without a pager.
os.environ['GIT_PAGER']=''

print('Cling Packaging Tool (CPT)')
print('Arguments vector: ' + str(sys.argv))
box_draw_header()
print('Thread Model: ' + FAMILY)
print('Operating System: ' + OS)
print('Distribution: ' + DIST)
print('Release: ' + RELEASE)
print('Revision: ' + REV)
print('Architecture: ' + platform.machine())
if args['compiler']:
  cInfo = None
  cInfo = exec_subprocess_check_output(args['compiler'] + ' --version', srcdir).decode('utf-8')
  print("Compiler: '%s' : %s" % (args['compiler'], cInfo.split('\n',1)[0] if cInfo else ''))

if len(sys.argv) == 1:
    print("Error: no options passed")
    parser.print_help()

# This is needed in Windows
if not os.path.isdir(workdir):
    os.makedirs(workdir)
if not (TRAVIS_BUILD_DIR or APPVEYOR_BUILD_FOLDER) and os.path.isdir(TMP_PREFIX):
    shutil.rmtree(TMP_PREFIX)
if not os.path.isdir(TMP_PREFIX):
    os.makedirs(TMP_PREFIX)

if args['check_requirements']:
    box_draw('Check availability of required softwares')
    if DIST == 'Ubuntu':
        check_ubuntu('git')
        check_ubuntu('cmake')
        check_ubuntu('gcc')
        check_ubuntu('g++')
        check_ubuntu('gnupg')
        check_ubuntu('python')
        check_ubuntu('SSL')
        yes = {'yes', 'y', 'ye', ''}
        no = {'no', 'n'}

        choice = input('''
Do you want to continue? [yes/no]: ''').lower()
        while True:
            if choice in yes:
                # Need to communicate values to the shell. Do not use exec_subprocess_call()
                subprocess.Popen(['sudo apt-get update'],
                                 shell=True,
                                 stdin=subprocess.PIPE,
                                 stdout=None,
                                 stderr=subprocess.STDOUT).communicate('yes'.encode('utf-8'))
                subprocess.Popen(['sudo apt-get install git cmake gcc g++ debhelper devscripts gnupg python'],
                                 shell=True,
                                 stdin=subprocess.PIPE,
                                 stdout=None,
                                 stderr=subprocess.STDOUT).communicate('yes'.encode('utf-8'))
                break
            elif choice in no:
                print('''
Install/update the required packages by:
  sudo apt-get update
  sudo apt-get install git cmake gcc g++ debhelper devscripts gnupg python
''')
                break
            else:
                choice = input("Please respond with 'yes' or 'no': ")
                continue

if args['current_dev']:
    llvm_revision = urlopen(
        "https://raw.githubusercontent.com/root-project/cling/master/LastKnownGoodLLVMSVNRevision.txt").readline().strip().decode(
        'utf-8')
    fetch_llvm(llvm_revision)
    fetch_clang(llvm_revision)
    libcpp = should_fetch_libcpp(llvm_revision)
    if libcpp: fetch_libcpp(llvm_revision, libcpp)

    # Travis has already cloned the repo out, so don;t do it again
    # Particularly important for building a pull-request
    if TRAVIS_BUILD_DIR or APPVEYOR_BUILD_FOLDER:
        ciCloned = TRAVIS_BUILD_DIR if TRAVIS_BUILD_DIR else APPVEYOR_BUILD_FOLDER
        clingDir = os.path.join(srcdir, 'tools', 'cling')
        if TRAVIS_BUILD_DIR:
            os.rename(ciCloned, clingDir)
            TRAVIS_BUILD_DIR = clingDir
        else:
            # Cannot move the directory: it is being used by another process
            os.mkdir(clingDir)
            for f in os.listdir(APPVEYOR_BUILD_FOLDER):
                shutil.move(os.path.join(APPVEYOR_BUILD_FOLDER, f), clingDir)
            APPVEYOR_BUILD_FOLDER = clingDir

        # Check validity and show some info
        box_draw("Using CI clone, last 5 commits:")
        exec_subprocess_call('git log -5 --pretty="format:%h <%ae> %<(60,trunc)%s"', clingDir)
        print('\n')
    else:
        fetch_cling(CLING_BRANCH if CLING_BRANCH else 'master')

    set_version()
    if args['current_dev'] == 'tar':
        if OS == 'Windows':
            get_win_dep()
            compile(os.path.join(workdir, 'cling-win-' + platform.machine().lower() + '-' + VERSION), libcpp)
        else:
            if DIST == 'Scientific Linux CERN SLC':
                compile(os.path.join(workdir, 'cling-SLC-' + REV + '-' + platform.machine().lower() + '-' + VERSION), libcpp)
            else:
                compile(os.path.join(workdir,
                                     'cling-' + DIST + '-' + REV + '-' + platform.machine().lower() + '-' + VERSION), libcpp)
        install_prefix()
        if not args['no_test']:
            test_cling()
        tarball()
        cleanup()

    elif args['current_dev'] == 'deb' or (args['current_dev'] == 'pkg' and DIST == 'Ubuntu'):
        compile(os.path.join(workdir, 'cling-' + VERSION), libcpp)
        install_prefix()
        if not args['no_test']:
            test_cling()
        tarball_deb()
        debianize()
        cleanup()

    elif args['current_dev'] == 'rpm' or (args['current_dev'] == 'pkg' and platform.dist()[0] == 'redhat'):
        compile(os.path.join(workdir, 'cling-' + VERSION.replace('-' + REVISION[:7], '')), libcpp)
        install_prefix()
        if not args['no_test']:
            test_cling()
        tarball()
        rpm_build()
        cleanup()

    elif args['current_dev'] == 'nsis' or (args['current_dev'] == 'pkg' and OS == 'Windows'):
        get_win_dep()
        compile(os.path.join(workdir, 'cling-' + RELEASE + '-' + platform.machine().lower() + '-' + VERSION), libcpp)
        install_prefix()
        if not args['no_test']:
            test_cling()
        make_nsi()
        build_nsis()
        cleanup()

    elif args['current_dev'] == 'dmg' or (args['current_dev'] == 'pkg' and OS == 'Darwin'):
        compile(os.path.join(workdir, 'cling-' + DIST + '-' + REV + '-' + platform.machine().lower() + '-' + VERSION), libcpp)
        install_prefix()
        if not args['no_test']:
            test_cling()
        make_dmg()
        cleanup()
    elif args['current_dev'].startswith('branch'):
        compile(os.path.join(workdir, 'cling-' + VERSION.replace('-' + REVISION[:7], '')), libcpp)
        #install_prefix()
        if not args['no_test']:
            test_cling()
        cleanup()

if args['last_stable']:
    tag = json.loads(urlopen("https://api.github.com/repos/vgvassilev/cling/tags")
                     .read().decode('utf-8'))[0]['name'].encode('ascii', 'ignore').decode("utf-8")

    # For Python 3 compatibility
    tag = str(tag)

    # FIXME
    assert tag[0] is "v"
    assert CLING_BRANCH == None
    llvm_revision = urlopen(
        'https://raw.githubusercontent.com/root-project/cling/%s/LastKnownGoodLLVMSVNRevision.txt' % tag
    ).readline().strip().decode('utf-8')

    fetch_llvm(llvm_revision)
    fetch_clang(llvm_revision)
    libcpp = should_fetch_libcpp(llvm_revision)
    if libcpp: fetch_libcpp(llvm_revision, libcpp)

    print("Last stable Cling release detected: ", tag)
    fetch_cling(tag)

    if args['last_stable'] == 'tar':
        set_version()
        if OS == 'Windows':
            get_win_dep()
            compile(os.path.join(workdir, 'cling-win-' + platform.machine().lower() + '-' + VERSION), libcpp)
        else:
            if DIST == 'Scientific Linux CERN SLC':
                compile(os.path.join(workdir, 'cling-SLC-' + REV + '-' + platform.machine().lower() + '-' + VERSION), libcpp)
            else:
                compile(os.path.join(workdir,
                                     'cling-' + DIST + '-' + REV + '-' + platform.machine().lower() + '-' + VERSION), libcpp)
        install_prefix()
        if not args['no_test']:
            test_cling()
        tarball()
        cleanup()

    elif args['last_stable'] == 'deb' or (args['last_stable'] == 'pkg' and DIST == 'Ubuntu'):
        set_version()
        compile(os.path.join(workdir, 'cling-' + VERSION), libcpp)
        install_prefix()
        if not args['no_test']:
            test_cling()
        tarball_deb()
        debianize()
        cleanup()

    elif args['last_stable'] == 'rpm' or (args['last_stable'] == 'pkg' and platform.dist()[0] == 'redhat'):
        set_version()
        compile(os.path.join(workdir, 'cling-' + VERSION), libcpp)
        install_prefix()
        if not args['no_test']:
            test_cling()
        tarball()
        rpm_build()
        cleanup()

    elif args['last_stable'] == 'nsis' or (args['last_stable'] == 'pkg' and OS == 'Windows'):
        set_version()
        get_win_dep()
        compile(os.path.join(workdir, 'cling-' + DIST + '-' + REV + '-' + platform.machine() + '-' + VERSION), libcpp)
        install_prefix()
        if not args['no_test']:
            test_cling()
        make_nsi()
        build_nsis()
        cleanup()

    elif args['last_stable'] == 'dmg' or (args['last_stable'] == 'pkg' and OS == 'Darwin'):
        set_version()
        compile(os.path.join(workdir, 'cling-' + DIST + '-' + REV + '-' + platform.machine().lower() + '-' + VERSION), libcpp)
        install_prefix()
        if not args['no_test']:
            test_cling()
        make_dmg()
        cleanup()

if args['tarball_tag']:
    llvm_revision = urlopen(
        "https://raw.githubusercontent.com/root-project/cling/%s/LastKnownGoodLLVMSVNRevision.txt" % args[
            'tarball_tag']).readline().strip().decode(
        'utf-8')
    fetch_llvm(llvm_revision)
    fetch_clang(llvm_revision)
    fetch_cling(args['tarball_tag'])
    libcpp = should_fetch_libcpp(llvm_revision)
    if libcpp: fetch_libcpp(llvm_revision, libcpp)

    set_version()

    if OS == 'Windows':
        get_win_dep()
        compile(os.path.join(workdir, 'cling-win-' + platform.machine().lower() + '-' + VERSION))
    else:
        if DIST == 'Scientific Linux CERN SLC':
            compile(os.path.join(workdir, 'cling-SLC-' + REV + '-' + platform.machine().lower() + '-' + VERSION), libcpp)
        else:
            compile(
                os.path.join(workdir, 'cling-' + DIST + '-' + REV + '-' + platform.machine().lower() + '-' + VERSION), libcpp)

    install_prefix()
    if not args['no_test']:
        test_cling()
    tarball()
    cleanup()

if args['deb_tag']:
    llvm_revision = urlopen(
        "https://raw.githubusercontent.com/root-project/cling/%s/LastKnownGoodLLVMSVNRevision.txt" % args[
            'deb_tag']).readline().strip().decode(
        'utf-8')
    fetch_llvm(llvm_revision)
    fetch_clang(llvm_revision)
    fetch_cling(args['deb_tag'])
    libcpp = should_fetch_libcpp(llvm_revision)
    if libcpp: fetch_libcpp(llvm_revision, libcpp)

    set_version()
    compile(os.path.join(workdir, 'cling-' + VERSION), libcpp)
    install_prefix()
    if not args['no_test']:
        test_cling()
    tarball_deb()
    debianize()
    cleanup()

if args['rpm_tag']:
    llvm_revision = urlopen(
        "https://raw.githubusercontent.com/root-project/cling/%s/LastKnownGoodLLVMSVNRevision.txt" % args[
            'rpm_tag']).readline().strip().decode(
        'utf-8')
    fetch_llvm(llvm_revision)
    fetch_clang(llvm_revision)
    fetch_cling(args['rpm_tag'])
    libcpp = should_fetch_libcpp(llvm_revision)
    if libcpp: fetch_libcpp(llvm_revision, libcpp)

    set_version()
    compile(os.path.join(workdir, 'cling-' + VERSION), libcpp)
    install_prefix()
    if not args['no_test']:
        test_cling()
    tarball()
    rpm_build()
    cleanup()

if args['nsis_tag']:
    llvm_revision = urlopen(
        "https://raw.githubusercontent.com/root-project/cling/%s/LastKnownGoodLLVMSVNRevision.txt" % args[
            'nsis_tag']).readline().strip().decode(
        'utf-8')
    fetch_llvm(llvm_revision)
    libcpp = fetch_libcpp(llvm_revision)
    fetch_clang(llvm_revision)
    fetch_cling(args['nsis_tag'])
    set_version()
    get_win_dep()
    compile(os.path.join(workdir, 'cling-' + DIST + '-' + REV + '-' + platform.machine() + '-' + VERSION), libcpp)
    install_prefix()
    if not args['no_test']:
        test_cling()
    make_nsi()
    build_nsis()
    cleanup()

if args['dmg_tag']:
    llvm_revision = urlopen(
        "https://raw.githubusercontent.com/root-project/cling/%s/LastKnownGoodLLVMSVNRevision.txt" % args[
            'dmg_tag']).readline().strip().decode(
        'utf-8')
    fetch_llvm(llvm_revision)
    fetch_clang(llvm_revision)
    fetch_cling(args['dmg_tag'])
    libcpp = should_fetch_libcpp(llvm_revision)
    if libcpp: fetch_libcpp(llvm_revision, libcpp)

    set_version()
    compile(os.path.join(workdir, 'cling-' + DIST + '-' + REV + '-' + platform.machine().lower() + '-' + VERSION), libcpp)
    install_prefix()
    if not args['no_test']:
        test_cling()
    make_dmg()
    cleanup()

if args['create_dev_env']:
    llvm_revision = urlopen(
        "https://raw.githubusercontent.com/root-project/cling/master/LastKnownGoodLLVMSVNRevision.txt"
    ).readline().strip().decode('utf-8')
    fetch_llvm(llvm_revision)
    fetch_clang(llvm_revision)
    fetch_cling('master')
    libcpp = should_fetch_libcpp(llvm_revision)
    if libcpp: fetch_libcpp(llvm_revision, libcpp)

    set_version()
    if OS == 'Windows':
        get_win_dep()
        compile(os.path.join(workdir, 'cling-win-' + platform.machine().lower() + '-' + VERSION), libcpp)
    else:
        if DIST == 'Scientific Linux CERN SLC':
            compile(os.path.join(workdir, 'cling-SLC-' + REV + '-' + platform.machine().lower() + '-' + VERSION), libcpp)
        else:
            compile(
                os.path.join(workdir, 'cling-' + DIST + '-' + REV + '-' + platform.machine().lower() + '-' + VERSION), libcpp)
    install_prefix()
    if not args['no_test']:
        test_cling()

if args['make_proper']:
    # This is an internal option in CPT, meant to be integrated into Cling's build system.
    with open(os.path.join(LLVM_OBJ_ROOT, 'config.log'), 'r') as log:
        for line in log:
            if re.match('^LLVM_PREFIX=', line):
                prefix = re.sub('^LLVM_PREFIX=', '', line).replace("'", '').strip()

    set_version()
    install_prefix()
    cleanup()

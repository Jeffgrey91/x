import launch_utils as lu

config = lu.args
python = lu.python
git = lu.git
index_url = lu.index_url
repos_dir = lu.dir_repos
commit = lu.commit_hash
tag = lu.git_tag
execute = lu.run
installed = lu.is_installed
repo_path = lu.repo_dir
pip_install = lu.run_pip
check_python = lu.check_run_python
clone_repo = lu.git_clone
pull_repo = lu.git_pull_recursive
list_extensions = lu.list_extensions
install_extension = lu.run_extension_installer
prepare_env = lu.prepare_environment
configure_tests = lu.configure_for_tests
start_server = lu.start

def run_program():
  if config.dump_sysinfo:
    filenam = lu.dump_sysinfo()
    print(f"System info saved as {filenam}. Exiting...")
    exit(0)
  
  print('Starting up...')
  lu.startup_timer.record("initial startup")

  with lu.startup_timer.subcategory("prepare environment"):
    if not config.skip_prepare_environment:
      prepare_env()

    if config.test_server:
      configure_tests()

    start_server()

if __name__ == "__main__":
  run_program()
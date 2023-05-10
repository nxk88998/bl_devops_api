from git.repo import Repo
import shutil
import os,stat,errno,sys
from urllib.parse import urlparse

class Git():
    def __init__(self, git_repo, repo_dir):
        self.git_repo = git_repo
        self.repo_dir = repo_dir
        self.repo = None

    def get_repo(self):
        if os.path.exists(self.repo_dir):
            # 处理windows下PermissionError问题
            def handle_remove_read_only(func, path, exc):
                excvalue = exc[1]
                if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
                    os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
                    func(path)
                else:
                    sys.exit(1)
            shutil.rmtree(self.repo_dir, onerror=handle_remove_read_only)

        repo = Repo.clone_from(self.git_repo, to_path=self.repo_dir)
        self.repo = repo
        return repo

    def get_branch(self):
        branch = []
        for ref in self.repo.remote().refs:
            if ref.remote_head != 'HEAD':
                branch.append(ref.remote_head)
        return branch

def git_repo_auth(git_repo, username, password):
    result = urlparse(git_repo)
    # 拼接用户名和密码，格式：http://root:12345.com@192.168.1.90:88/root/java-demo.git
    git_repo = "%s://%s:%s@%s%s" %(result.scheme,username,password,result.netloc,result.path)
    return git_repo

if __name__ == "__main__":
    repo_dir = os.path.join(os.getcwd(), "repos")
    print(repo_dir)
    git = Git("https://gitee.com/lw-corn/corn-grain.git", repo_dir)
    git.get_repo()
    print(git.get_branch())
    print(git_repo_auth("https://gitee.com/lw-corn/corn-grain.git", "13065606821", "csnxk88998!"))



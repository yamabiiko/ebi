import os
from rich.console import Console
from rich.theme import Theme
import random
import argparse
import sqids

theme = Theme({
    "warning": "bold yellow",
    "error": "bold red",
    "info": "bold magenta",
    "default": "white"
})
console = Console(theme=theme)

class DirectoryGenerator:
    
    def __init__(self, seed, depth, branch_factor, max_files, max_filesize, max_tags):
        # Runtime Variables
        self.root_dir = None
        self.test_dir = None
        self.tag_file = None
        self.id_gen = None
        self.id_counter = 0
        self.tags = None
        # Parameters
        self.seed = seed
        self.depth = depth
        self.branch_factor = branch_factor
        self.max_files = max_files
        self.max_filesize = max_filesize    
        self.max_tags = max_tags
        # Test Environment Setup
        self._setup()

    def _setup(self):
        # Initialises the pseudorandom generator
        if not self.seed:
            self.seed = random.randint(0, 1000000)
        random.seed(self.seed)
        key_chars = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        random.shuffle(key_chars)
        self.id_gen = sqids.Sqids(alphabet="".join(key_chars), min_length=8)
        console.print("Seed: " + str(self.seed), style="info")
        # Saves the Root directory
        self.root_dir = os.path.abspath(os.path.join(__file__, "..", "..", ".."))
        # Generates the Test directory (if it does not exist)
        src_dir = os.path.dirname(os.path.abspath(__file__))
        test_dir = os.path.join(src_dir, "..", "..", "Tests")
        self.test_dir = test_dir
        try:
            os.makedirs(test_dir)
            console.print("WARNING: Test directory does not exist. Creating one now.", style="warning")
        except FileExistsError:
            pass
        
    def _getID(self):
        ID = self.id_gen.encode([self.id_counter])
        self.id_counter += 1
        return ID
    
    def _addGitignore(self, path):
        gitignore_path = os.path.abspath(self.root_dir + "/.gitignore")
        with open(gitignore_path, "a") as gitignore_file:
            gitignore_file.write(f"{path}\n")
        
    def _getTag(self):
        n = random.random()
        if n < 0.3 and len(self.tags) > 0:
            return random.choice(list(self.tags))
        else:
            return self._getID()
    
    def _writeFile(self, path):
        with open(path, "wb") as file:
            if self.max_filesize > 0:
                bytes_to_write = random.randint(0, self.max_filesize)
                file.write(random.randbytes(bytes_to_write))
    
    def _addTag(self, path, blacklist):
        tag = self._getTag()
        while tag in blacklist:
            tag = self._getTag()
        self.tags.add(tag)
        self.tag_file.write(f"{path}\t{tag}\n")
        return tag
            
    def _generate(self, path, depth):
        # Generate Subdirectories and Files
        subdirs = random.randint(1, self.branch_factor)
        files = random.randint(0, self.max_files)
        for _ in range(subdirs):
            subdir_name = self._getID()
            subdir_path = os.path.join(path, subdir_name)
            if depth < self.depth:
                os.makedirs(subdir_path)
                self._generate(subdir_path, depth + 1)
        for _ in range(files):
            file_name = self._getID() + ".dat"
            file_path = os.path.join(path, file_name)
            self._writeFile(file_path)
            tagSet = set()
            for _ in range(random.randint(1, self.max_tags)):
                tag = self._addTag(file_path.split("\\")[-1], blacklist=tagSet)
                tagSet.add(tag)
            
    def generate(self, name):
        # Initialise Environment Variables
        self.id_counter = 0
        self.tags = set()
        # Create Test Directory and Tag File
        test_path = os.path.join(self.test_dir, "Generated", name)
        try:
            os.makedirs(test_path)
            self._addGitignore(test_path)
            self._addGitignore(os.path.join(self.test_dir, name + ".tag"))
            with open(os.path.join(self.test_dir,"Generated", name + ".tag"), "w") as tag_file:
                self.tag_file = tag_file
                self._generate(test_path, 0)
        except FileExistsError:
            console.print("ERROR: Test Directory '" + name + "' already exists", style="error")

def main():
    parser = argparse.ArgumentParser(prog="Test Workspace Generator", description="Generates a test directory structure", add_help=False)
    parser.add_argument("-n", type=str, dest="name", metavar="name", required=True, help="Name of the test directory")
    parser.add_argument("-s", type=int, dest="seed", metavar="seed", default=None, help="Seed for the random number generator")
    parser.add_argument("-d", type=int, dest="depth", metavar="depth", default=4, help="Max depth of the directory tree")
    parser.add_argument("-b", type=int, dest="branch_factor", metavar="branch", default=4, help="Max Branching factor of the directory tree")
    parser.add_argument("-f", type=int, dest="max_files", metavar="files", default=3, help="Max number of files per directory")
    parser.add_argument("-fs", type=int, dest="max_filesize", metavar="fsize", default=0, help="Max size of the files in Bytes")
    parser.add_argument("-t", type=int, dest="max_tags", metavar="tags", default=2, help="Max number of tags per file")
    parser.add_argument('-v', action='version', version='%(prog)s 1.0', help="Show program's version number and exit")
    parser.add_argument('-h', action='help', default=argparse.SUPPRESS, help='Show this help message and exit')
    args = parser.parse_args()

    generator = DirectoryGenerator(
        seed=args.seed,
        depth=args.depth,
        branch_factor=args.branch_factor,
        max_files=args.max_files,
        max_filesize=args.max_filesize,
        max_tags=args.max_tags
    )
    generator.generate(args.name)

if __name__ == "__main__":
    main()
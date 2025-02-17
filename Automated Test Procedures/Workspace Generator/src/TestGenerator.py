import os
from rich.console import Console
from rich.theme import Theme
import random
import argparse
import sqids
import string

# Custom Theme for Rich Console
theme = Theme({
    "warning": "bold #ffff00",
    "critical": "bold #ff5f00",
    "error": "bold #ff0000",
    "success": "bold #00ff00",
    "info": "bold #ffffff",
    "default": "#ffffff",
    "repr.number": "#00ff00",
    "repr.str": ""
})
console = Console(theme=theme)
class DirectoryGenerator:
        
    """
        Initialises the DirectoryGenerator with the given parameters and sets up the test environment.
        
        Args:
            seed (int): The seed for random number generation.  If not provided, a random seed is generated.
            depth (int): The maximum depth of the directory tree.
            branch_factor (int): The maximum number of branches at each level of the directory tree.
            max_files (int): The maximum number of files to generate in each directory.
            max_filesize (int): The maximum size of each file in Bytes.
            max_tags (int): The maximum number of tags to assign to each file.
            tag_density (float): The probability that a path is tagged with an existing tag (if one exists).
            untagged_files (bool): Files can have no associated tags.
    """
    def __init__(self, seed, depth, branch_factor, max_files, max_filesize, max_tags):
    def __init__(self, seed, depth, branch_factor, max_files, max_filesize, max_tags, tag_density, untagged_files):
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
        self.tag_density = tag_density
        self.untagged_files = untagged_files
        # Test Environment Setup
        self._setup()


    """
        Initializes the pseudorandom generators, sets up the root and test directories.

        This method performs the following tasks:
        - Initializes the pseudorandom generators with a seed. If no seed is provided, a random seed is generated.
        - Sets up an ID generator using the Sqids library with a shuffled alphabet and a minimum length of 8 characters.
        - Prints the seed used for the pseudorandom generators.
        - Saves the root directory path.
        - Generates the test directory if it does not already exist.
    """  
    def _setup(self):
        # Initialises the pseudorandom generators
        if not self.seed:
            self.seed = random.randint(0, 1000000)
        random.seed(self.seed)
        key_chars = list(string.ascii_letters + string.digits)
        random.shuffle(key_chars)
        self.id_gen = sqids.Sqids(alphabet="".join(key_chars), min_length=8)
        console.print("Seed: " + str(self.seed), style="info")
        # Saves the Root directory
        self.root_dir = os.path.abspath(os.path.join(os.getcwd(), "..", "..", ".."))
        self.root_dir = os.path.abspath(os.path.join(__file__, "..", "..", ".."))
        # Generates the Test directory (if it does not exist)
        src_dir = os.path.dirname(os.path.abspath(__file__))
        test_dir = os.path.join(src_dir, "..", "..", "Tests")
        test_dir = os.path.abspath(os.path.join(src_dir, "..", "..", "Tests", "Workspaces", "Generated"))
        self.test_dir = test_dir
        try:
            os.makedirs(test_dir)
            console.print("WARNING: Test directory does not exist. Creating one now.", style="warning")
            console.print("WARNING: Test directory does not exist. It will be created", style="warning")
        except FileExistsError:
            pass
        
    """
        Generates a unique ID using the id_gen encoder and increments the id_counter.
        Generates a unique ID using the id_gen encoder (sqids) and increments the id_counter.

        Returns:
            str: The generated unique ID.
    """
    def _getID(self):
        ID = self.id_gen.encode([self.id_counter])
        self.id_counter += 1
        return ID
    
    """
        [DEPRECATED]
        
        Adds the specified path to the .gitignore file located in the root directory.

        Args:
            path (str): The path to be added to the .gitignore file.
    """
    def _addGitignore(self, path):
        gitignore_path = os.path.abspath(self.root_dir + "/.gitignore")
    def _addGitignore(self, path, dir=False):
        gitignore_path = os.path.join(self.root_dir, "..", ".gitignore")
        formatted_path = "/".join(path.split("\\")[-5:])
        with open(gitignore_path, "a") as gitignore_file:
            gitignore_file.write(f"{path}\n")
        
            if dir:
                gitignore_file.write(f"{formatted_path}/\n")
            else:
                gitignore_file.write(f"{formatted_path}\n")
                
    """
        Selects and returns a new tag (0.7) or an existing tag (0.3).
        Selects and returns a new tag (1-p) or an existing tag (p).

        Args:
            p (float, optional): The probability of selecting an existing tag. Defaults to 0.3.
            p (float): The probability of selecting an existing tag.

        Returns:
            str: Tag.
    """
    def _getTag(self, p=0.3):    
    def _getTag(self, p):
        n = random.random()
        if n < p and len(self.tags) > 0:
            return random.choice(list(self.tags))
        else:
            return self._getID()
    
    """
        Writes a file with random bytes to the specified path.

        Args:
            path (str): The path to the file to be written.
            ~ self.max_filesize (int, cli): The maximum size of the file in bytes.
    """
    def _writeFile(self, path):
        with open(path, "wb") as file:
            if self.max_filesize > 0:
                bytes_to_write = random.randint(0, self.max_filesize)
                file.write(random.randbytes(bytes_to_write))
    
    """
        Adds a tag to the specified path (file) and writes the path-tag pair to the tag file.
        Adds a tag to the specified path (file) and writes the path-tag pair to the tag file.  #[]
        Accepts a blacklist of tags, used to ensure that a tag-path link is unique.

        Args:
            path (str): The file path to which the tag will be associated.
            blacklist (set, optional): Tags to avoid. Defaults to an empty set.

        Returns:
            str: The tag that was added.
    """       
    def _addTag(self, path, blacklist=set()):
        tag = self._getTag()
        tag = self._getTag(self.tag_density)
        while tag in blacklist:
            tag = self._getTag(self.tag_density)
        self.tags.add(tag)
        self.tag_file.write(f"{path}\t{tag}\n")
        return tag
            
    """
        Recursively generates a directory structure with files and tags.

        Args:
            path (str): The current directory path where subdirectories and files will be generated.
            depth (int): The current depth of the directory structure.
            ~ self.depth (int, cli): The maximum depth of the directory tree.
            ~ self.branch_factor (int, cli): The maximum number of branches at each level of the directory tree.
            ~ self.max_files (int, cli): The maximum number of files to generate in each directory.
            ~ self.max_tags (int, cli): The maximum number of tags to assign to each file.
            ~ self.tag_density (float, cli): The probability that a path is tagged with an existing tag (if one exists).
            ~ self.untagged_files (bool, cli): Files can have no associated tags.
    """
    def _generate(self, path, depth):
        # Generate Subdirectories
        subdirs = random.randint(1, self.branch_factor)
        for _ in range(subdirs):
            subdir_name = self._getID()
            subdir_path = os.path.join(path, subdir_name)
            if depth < self.depth:
                os.makedirs(subdir_path)
                self._generate(subdir_path, depth + 1)
        # Generate Files
        files = random.randint(0, self.max_files)
        for _ in range(files):
            file_name = self._getID() + ".dat"
            file_path = os.path.join(path, file_name)
            self._writeFile(file_path)
            tagSet = set()
            if self.untagged_files:
                min_tags = 1 
            else:
                min_tags = 0
            for _ in range(random.randint(min_tags, self.max_tags)):
                tag = self._addTag(os.path.basename(file_path), blacklist=tagSet)
                tagSet.add(tag)            
                if len(self.tags) >= 1 and self.tag_density >= 0.99:
                    break
                
    """
        Generates a test environment with the specified name.

        Args:
            name (str): The name of the test environment to be generated.

        Raises:
            FileExistsError: If the test directory already exists.
    """
    def generate(self, name):
        tag = self.max_tags + 1
        
        # Initialise Environment Variables
        self.id_counter = 0
        self.tags = set()
        # Create Test Directory
        test_path = os.path.join(self.test_dir, name)
        os.makedirs(test_path)
        ''' [DEPRECATED]
        # Add Test Directory to .gitignore
        self._addGitignore(test_path, dir=True)```
        '''
        # Create Tag File
        if os.path.exists(os.path.join(self.test_dir, name + ".tag")):
            console.print("WARNING: Tag File already exists. It will be overwritten", style="critical")
        with open(os.path.join(self.test_dir, name + ".tag"), "w") as tag_file:     
            self.tag_file = tag_file
            # Add Tag File to .gitignore
            self._addGitignore(os.path.join(self.test_dir, name + ".tag"))
            # Generate Test Directory
            self._generate(test_path, 0)
            self.tag_file.flush()
            self.tag_file.close()


def main():
    """
    Generates a test directory structure with the specified name and (optional) parameters.
    
    Command-line arguments:
        -n, (str): Name of the test directory (required).
        -s, (int): Seed for the random number generator (default: None).
        -d, (int): Max depth of the directory tree (default: 4).
        -b, (int): Max branching factor of the directory tree (default: 4).
        -f, (int): Max number of files per directory (default: 5).
        -fs, (int): Max size of the files in Bytes (default: 1000).
        -t, (int): Max number of tags per file (default: 3).
        -td, (float): Probability of assigning an existing tag (Min: 0.0, Max: 1.0) (default: 0.3).
        -uf, (bool): Files can have no associated tags.
        -v, --version: Show program's version number and exit.
        -h, --help: Show help message and exit.
    """
    parser = argparse.ArgumentParser(prog="Test Workspace Generator", description="Generates a test directory structure", add_help=False, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-n", type=str, dest="name", metavar="name", required=True, help="Name of the test directory")
    parser.add_argument("-s", type=int, dest="seed", metavar="seed", default=None, help="Seed for the random number generator")
    parser.add_argument("-d", type=int, dest="depth", metavar="depth", default=4, help="Max depth of the directory tree")
    parser.add_argument("-b", type=int, dest="branch_factor", metavar="branch", default=4, help="Max Branching factor of the directory tree")
    parser.add_argument("-f", type=int, dest="max_files", metavar="files", default=5, help="Max number of files per directory")
    parser.add_argument("-fs", type=int, dest="max_filesize", metavar="bytes", default=1000, help="Max size of the files in Bytes")
    parser.add_argument("-t", type=int, dest="max_tags", metavar="tags", default=3, help="Max number of tags per file")
    parser.add_argument("-td", type=float, dest="tag_density", metavar="density", default=0.3, help="Probability of assigning an existing tag (Min: 0.0, Max: 1.0)")
    parser.add_argument("-uf", dest="untagged_files", action="store_true", help="Files can have no associated tags")
    parser.add_argument('-v', "--version", action='version', version='%(prog)s 1.0', help="Show program's version number and exit")
    parser.add_argument('-h', "--help", action='help', default=argparse.SUPPRESS, help='Show this help message and exit')
    args = parser.parse_args()

    generator = DirectoryGenerator(
        seed=args.seed,
        depth=args.depth,
        branch_factor=args.branch_factor,
        max_files=args.max_files,
        max_filesize=args.max_filesize,
        max_tags=args.max_tags,
        tag_density=args.tag_density,
        untagged_files=args.untagged_files
    )
    
    try:
        generator.generate(args.name)
    except FileExistsError as fe:
        console.print(f"ERROR: Test Directory '{args.name}' already exists", style="error")
        exit()

if __name__ == "__main__":
    main()
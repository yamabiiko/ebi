use chrono::{DateTime, Utc};
use std::collections::{BTreeSet, HashMap, HashSet};
use std::fs::{self, DirEntry};
use std::path::PathBuf;
use std::rc::Rc;
use std::result::Result;
use std::{io, rc};
// Shelf
#[derive(Debug)]
pub struct Shelf {
    root: Node,
    // String = Workspace identifier + Global
    ownership: HashMap<Tag, HashSet<String>>,
}

impl Shelf {
    pub fn new(path: PathBuf) -> Result<Self, io::Error> {
        Ok(Shelf {
            root: Node::new(path)?,
            ownership: HashMap::new(),
        })
    }

    pub async fn refresh(&self) -> Result<bool, io::Error> {
        todo!();
        // Must also update the 'modifiied', 'size' fields in Metadata
    }

    pub fn query(&self, query: Query) -> Result<Vec<&'static File>, QueryErr> {
        todo!();
    }

    pub fn insert(&self, file: PathBuf, tag: Tag) -> Result<bool, UpdateErr> {
        todo!();
    }

    pub fn delete(&self, file: Option<PathBuf>, tag: Tag) -> Result<bool, UpdateErr> {
        todo!();
    }
}

// Node
#[derive(Debug)]
struct Node {
    files: HashMap<PathBuf, Rc<File>>,
    tags: HashMap<Tag, Rc<File>>,
    node_tags: BTreeSet<&'static Tag>,   // Directory level tags
    directories: HashMap<PathBuf, Node>, // untagged: set of untagged files, support structure
}

impl Node {
    pub fn new(path: PathBuf) -> Result<Self, io::Error> {
        let entries = fs::read_dir(path)?
            .map(|res| res.map(|e| e.path()))
            .collect::<Result<Vec<_>, io::Error>>()?;
        let (dir_paths, file_paths): (Vec<_>, Vec<_>) = entries.into_iter().partition(|path| path.is_dir());
        let files = file_paths
            .into_iter()
            .map(|file_path| {
                (
                    file_path.clone(),
                    Rc::new(File::new(
                        file_path.clone(),
                        BTreeSet::new(),
                        BTreeSet::new(),
                        Metadata::new(),
                    )),
                )
            })
            .collect::<HashMap<PathBuf, Rc<File>>>();
        let directories = dir_paths
            .into_iter()
            .map(|dir| (dir.clone(), Node::new(dir.clone()).unwrap()))
            .collect::<HashMap<PathBuf, Node>>();
        return Ok(Node {
            files,
            tags: HashMap::new(),
            node_tags: BTreeSet::new(),
            directories,
        });
    }

    pub fn add_node_tag(&mut self, tag: &'static Tag) -> bool {
        self.node_tags.insert(tag)
    }

    pub fn remove_node_tag(&mut self, tag: Tag) -> bool {
        self.node_tags.remove(&tag)
    }
}

// Tag
#[derive(Debug, Eq, PartialOrd, PartialEq, Ord)]
pub struct Tag {
    name: String,
    parent: Option<&'static Tag>,
    subtags: BTreeSet<&'static Tag>, //Parent tags in a query will be substituted by a disjunctive expression of themselves and their subtags
}

#[derive(Debug)]
pub struct Metadata {
    created: DateTime<Utc>,
    modified: DateTime<Utc>,
    size: u64,
    extension: String,
}

impl Metadata {
    pub fn new() -> Self {
        //[!] Mock - Metadata will be read from File System
        Metadata {
            created: Utc::now(),
            modified: Utc::now(),
            size: 0,
            extension: String::new(),
        }
    }
}

#[derive(Debug)]
pub struct File {
    path: PathBuf,
    hash: u64,
    metadata: Metadata,
    tags: BTreeSet<&'static Tag>,
    dir_tags: BTreeSet<&'static Tag>,
}

#[derive(Debug)]
pub struct Query {}

// TODO: define appropriate errors, include I/O, etc.
pub enum QueryErr {
    SyntaxError, // The Query is incorrectly formatted
    KeyError,    // The Query uses tags which do not exist in the Shelf
}

// TODO: define appropriate errors
pub enum UpdateErr {
    PathNotFound,
}

impl File {
    pub fn new(
        path: PathBuf,
        tags: BTreeSet<&'static Tag>,
        dir_tags: BTreeSet<&'static Tag>,
        metadata: Metadata,
    ) -> Self {
        File {
            path,
            hash: 0,
            metadata,
            tags,
            dir_tags,
        }
    }

    pub fn add_tag(&mut self, tag: &'static Tag) -> bool {
        self.tags.insert(tag)
    }

    pub fn remove_tag(&mut self, tag: Tag) -> bool {
        self.tags.remove(&tag)
    }
}
